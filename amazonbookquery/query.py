#!/usr/bin/env python

import os
import sys
import requests
import hmac
import functools
from base64 import b64encode
from hashlib import sha256
from datetime import datetime, timedelta
from time import strftime, gmtime, sleep
from urllib.parse import quote
from urllib.request import HTTPError
from amazonbookquery.errors import *
from amazonbookquery.parser import Parser
from amazonbookquery.scrapy import Scrapy

class Query(object):

    REQUESTS_PER_SECOND = 1

    def __init__(self):
        self.access_key = os.getenv('AMAZON_ACCESS_KEY')
        self.secret_key = os.getenv('AMAZON_SECRET_KEY')
        self.associate_tag = os.getenv('AMAZON_ASSOC_KEY')
        self.host = 'webservices.amazon.com'

        self.last_call = datetime(1970, 1, 1)
        self.parser = Parser()

    def _build_url(self, **qargs):
        """
        Builds a signed URL for querying Amazon AWS.
        """

        # remove empty (=None) parameters
        for key in list(qargs):
            if qargs[key] is None:
                del qargs[key]

        if 'AWSAccessKeyId' not in qargs:
            qargs['AWSAccessKeyId'] = self.access_key
        if 'Service' not in qargs:
            qargs['Service'] = 'AWSECommerceService'

        if 'AssociateTag' not in qargs:
            qargs['AssociateTag'] = self.associate_tag

        if isinstance(qargs.get('ResponseGroup'), list):
            qargs['ResponseGroup'] = ','.join(qargs['ResponseGroup'])

        # add timestamp (this is required when using a signature)
        qargs['Timestamp'] = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())

        # create signature
        keys = sorted(qargs.keys())
        args = '&'.join('%s=%s' % (
            key, quote(str(qargs[key]).encode('utf-8'))) for key in keys)
        msg = 'GET'
        msg += '\n' + self.host
        msg += '\n/onca/xml'
        msg += '\n' + args

        key = self.secret_key or ''
        # On python3, HMAC needs bytes for key and msg
        try:
            hash = hmac.new(key, msg, sha256)
        except TypeError:
            hash = hmac.new(key.encode(), msg.encode(), sha256)

        signature = quote(b64encode(hash.digest()))
        return 'http://%s/onca/xml?%s&Signature=%s' % (
            self.host, args, signature)

    def _fetch(self, url):
        # Be nice and wait for some time
        # before submitting the next request
        delta = datetime.now() - self.last_call
        throttle = timedelta(seconds=1 / self.REQUESTS_PER_SECOND)
        if delta < throttle:
            wait = throttle - delta
            sleep(wait.seconds + wait.microseconds / 1000000.0)  # pragma: no cover
        self.last_call = datetime.now()

        response = requests.get(url, stream=True)
        response.raw.read = functools.partial(response.raw.read, decode_content=True)
        return response.raw

    def _parse(self, fp, operation):
        """
        Processes the AWS response (file like object). XML is fed in, some
        usable output comes out. It will use a different result_processor if
        you have defined one.
        """
        try:
            if operation == 'ItemSearch':
                return self.parser.parse_item_search(fp)
            else:
                return self.parser.parse_item_lookup(fp)
        except AWSError:
            e = sys.exc_info()[1]  # Python 2/3 compatible

            errors = {
                'InternalError': InternalError,
                'InvalidClientTokenId': InvalidClientTokenId,
                'MissingClientTokenId': MissingClientTokenId,
                'RequestThrottled': TooManyRequests,
                'Deprecated': DeprecatedOperation,
                'AWS.ECommerceService.NoExactMatches': NoExactMatchesFound,
                'AccountLimitExceeded': AccountLimitExceeded,
                'AWS.ECommerceService.ItemNotEligibleForCart': InvalidCartItem,
                'AWS.ECommerceService.CartInfoMismatch': CartInfoMismatch,
                'AWS.ParameterOutOfRange': ParameterOutOfRange,
                'AWS.InvalidAccount': InvalidAccount,
                'SignatureDoesNotMatch': InvalidSignature,
            }

            if e.code in errors:
                raise _e(errors[e.code])

            if e.code == 'AWS.MissingParameters':
                m = self._reg('missing-parameters').search(e.msg)
                raise _e(MissingParameters, m.group('parameter'))

            if e.code == 'AWS.InvalidEnumeratedParameter':
                m = self._reg('invalid-value').search(e.msg)
                if m is not None:
                    if m.group('parameter') == 'ResponseGroup':
                        raise _e(InvalidResponseGroup)
                    elif m.group('parameter') == 'SearchIndex':
                        raise _e(InvalidSearchIndex)

            if e.code == 'AWS.InvalidParameterValue':
                m = self._reg('invalid-parameter-value').search(e.msg)
                raise _e(InvalidParameterValue,
                         m.group('parameter'), m.group('value'))

            if e.code == 'AWS.RestrictedParameterValueCombination':
                m = self._reg('invalid-parameter-combination').search(e.msg)
                raise _e(InvalidParameterCombination, m.group('message'))

            if e.code == 'AWS.ECommerceService.ItemAlreadyInCart':
                item = self._reg('already-in-cart').search(e.msg).group('item')
                raise _e(ItemAlreadyInCart, item)

            raise

    def _reg(self, key):
        """
        Returns the appropriate regular expression (compiled) to parse an error
        message depending on the current locale.
        """
        return DEFAULT_ERROR_REGS[key]

    def _call(self, **qargs):
        url = self._build_url(**qargs)
        try:
            fp = self._fetch(url)
            return self._parse(fp, qargs['Operation'])
        except HTTPError:
            e = sys.exc_info()[1]
            if e.code in (400, 403, 410, 503):
                return self._parse(e.fp)
            if e.code == 500:
                raise InternalError
            raise

    def execute_query(self, title, author):
        try:
            asin = self._call(
                Operation='ItemSearch',
                Title=title,
                Author=author,
                SearchIndex='Books'
            )

            item = self._call(
                Operation='ItemLookup',
                ItemId=asin,
                ResponseGroup=['AlternateVersions', 'ItemAttributes', 'OfferFull', 'Offers', 'OfferListings', 'OfferSummary'],
                RelationshipType='AuthorityTitle'
            )

            scrapy = Scrapy()
            result = scrapy.scrape(item['detail_page_url'])

            item['total_new'] = result['total_new']
            item['total_used'] = result['total_used']
            item['total_collectible'] = result['total_collectible']

            return item
        except:
            raise