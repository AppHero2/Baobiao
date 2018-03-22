#!/usr/bin/env python

from lxml import etree, objectify
from amazonbookquery.errors import AWSError

class SelectiveClassLookup(etree.CustomElementClassLookup):
    """
    Lookup mechanism for XML elements to ensure that ItemIds (like
    ASINs) are always StringElements and evaluated as such.

    Thanks to Brian Browning for pointing this out.
    """
    # pylint: disable-msg=W0613
    def lookup(self, node_type, document, namespace, name):
        if name in ('ItemId', 'ASIN'):
            return objectify.StringElement

class Parser:

    def __init__(self):
        self._parser = etree.XMLParser()
        lookup = SelectiveClassLookup()
        lookup.set_fallback(objectify.ObjectifyElementClassLookup())
        self._parser.set_element_class_lookup(lookup)

    def _get_item(self, data):
        tree = objectify.parse(data, self._parser)
        root = tree.getroot()

        try:
            nspace = root.nsmap[None]
            errors = root.xpath('//aws:Error', namespaces={'aws': nspace})
        except KeyError:
            errors = root.xpath('//Error')

        for error in errors:
            raise AWSError(
                code = error.Code.text,
                msg = error.Message.text,
                xml = root
            )

        item = root.Items.Item
        return item

    def parse_item_search(self, data):
        item = self._get_item(data)
        asin = item.ASIN.text

        return asin

    def parse_item_lookup(self, data):
        item = self._get_item(data)
        nspace = item.nsmap[None]
        author = detail_page_url = title = lowest_collectible_price = lowest_new_price = lowest_used_price = None
        total_new = total_used = total_collectible = 0
        sold_by_amazon = False
        sold_by_amazon_as_new = False
        alternate_asin = []

        attributes = offer_summary = alternate_versions = offers = []

        for child in item.getchildren():
            if child.tag == '{' + nspace + '}' + 'ItemAttributes':
                attributes = item.ItemAttributes.getchildren()
            if child.tag == '{' + nspace + '}' + 'OfferSummary':
                offer_summary = item.OfferSummary.getchildren()
            if child.tag == '{' + nspace + '}' + 'AlternateVersions':
                alternate_versions = item.AlternateVersions.getchildren()
            if child.tag == '{' + nspace + '}' + 'Offers':
                offers = item.Offers.getchildren()

        for attribute in attributes:
            if attribute.tag == '{' + nspace + '}' + 'Author':
                author = attribute.text
            if attribute.tag == '{' + nspace + '}' + 'Title':
                title = attribute.text
        for summary in offer_summary:
            if summary.tag == '{' + nspace + '}' + 'TotalNew':
                total_new = summary.text
            if summary.tag == '{' + nspace + '}' + 'TotalUsed':
                total_used = summary.text
            if summary.tag == '{' + nspace + '}' + 'TotalCollectible':
                total_collectible = summary.text
            if summary.tag == '{' + nspace + '}' + 'LowestNewPrice':
                lowest_new_price = summary.Amount.text
            if summary.tag == '{' + nspace + '}' + 'LowestUsedPrice':
                lowest_used_price = summary.Amount.text
            if summary.tag == '{' + nspace + '}' + 'LowestCollectiblePrice':
                lowest_collectible_price = summary.Amount.text
        for alternate_version in alternate_versions:
            if alternate_version.tag == '{' + nspace + '}' + 'AlternateVersion':
                alternate_asin.append(alternate_version.ASIN.text)
        for offer in offers:
            if offer.tag == '{' + nspace + '}' + 'Offer':
                for child in offer.getchildren():
                    if child.tag == '{' + nspace + '}' + 'Merchant':
                        sold_by_amazon = (child.Name.text == 'Amazon.com')
                    if child.tag == '{' + nspace + '}' + 'OfferAttributes':
                        sold_by_amazon_as_new = (child.Condition.text == 'New')

        detail_page_url = item.DetailPageURL.text

        return {
            'detail_page_url': detail_page_url,
            'author': author,
            'title': title,
            'total_new': int(total_new),
            'total_used': int(total_used),
            'total_collectible': int(total_collectible),
            'lowest_new_price': lowest_new_price,
            'lowest_used_price': lowest_used_price,
            'lowest_collectible_price': lowest_collectible_price,
            'sold_by_amazon': sold_by_amazon,
            'sold_by_amazon_as_new': sold_by_amazon_as_new,
            'alternate_asin': alternate_asin
        }