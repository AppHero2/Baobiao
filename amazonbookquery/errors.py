"""
Contains all errors specific to this package.
"""

import re
import sys

__all__ = [
    'AccountLimitExceeded', 'AWSError', 'CartInfoMismatch', 'DEFAULT_ERROR_REGS',
    'InvalidClientTokenId', 'InvalidSignature', 'InvalidAccount', 'MissingClientTokenId', 'MissingParameters',
    'ParameterOutOfRange', 'DeprecatedOperation', 'InternalError',
    'InvalidCartId', 'InvalidCartItem', 'InvalidListType', 'InvalidOperation',
    'InvalidParameterCombination', 'InvalidParameterValue',
    'InvalidResponseGroup', 'InvalidSearchIndex', 'ItemAlreadyInCart',
    'NoExactMatchesFound', 'NoSimilarityForASIN',
    'NotEnoughParameters', 'TooManyRequests', 'UnknownLocale', '_e'
]


class AWSError(Exception):
    """
    Generic AWS error message with the following attributes:

        ``code``
            The Amazon error code (e.g. ``AWS.InvalidEnumeratedParameter``)

        ``msg``
            The original error message from Amazon

        ``xml``
            XML returned from Amazon as processed by the API's result processor

    You can (and should) still pass additional arguments to derived exceptions
    which (as with :class:`BaseException`) will be stored in ``args``.
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self)
        self.args = args
        self.code = kwargs.pop('code', None)
        self.msg = kwargs.pop('msg', None)
        self.xml = kwargs.pop('xml', None)

    def __str__(self):  # pragma: no cover
        if self.code is not None:
            return '%(code)s: %(msg)s' % self.__dict__
        return Exception.__str__(self)


class UnknownLocale(AWSError):
    """
    Raised when unknown locale is specified.
    """


class InternalError(AWSError):
    """
    Amazon encountered an internal error. Please try again.
    """


class InvalidClientTokenId(AWSError):
    """
    The AWS Access Key Id you provided does not exist in Amazon's records.
    """


class MissingClientTokenId(AWSError):
    """
    Request must contain AWSAccessKeyId or X.509 certificate.
    """


class InvalidSignature(AWSError):
    """
    The AWS Secret key you provided is invalid.
    """


class InvalidAccount(AWSError):
    """
    Your account has no access to the product API.
    """


class MissingParameters(AWSError):
    """
    Your request is missing required parameters. Required parameters include
    XXX.
    """


class ParameterOutOfRange(AWSError):
    """
    The value you specified for XXX is invalid.
    """


class InvalidSearchIndex(AWSError):
    """
    The value specified for SearchIndex is invalid. Valid values include:

    All, Apparel, Automotive, Baby, Beauty, Blended, Books, Classical, DVD,
    Electronics, ForeignBooks, HealthPersonalCare, HomeGarden, HomeImprovement,
    Jewelry, Kitchen, Magazines, MP3Downloads, Music, MusicTracks,
    OfficeProducts, OutdoorLiving, PCHardware, Photo, Shoes, Software,
    SoftwareVideoGames, SportingGoods, Tools, Toys, VHS, Video, VideoGames,
    Watches
    """


class InvalidResponseGroup(AWSError):
    """
    The specified ResponseGroup parameter is invalid. Valid response groups for
    ItemLookup requests include:

    Accessories, AlternateVersions, BrowseNodes, Collections, EditorialReview,
    Images, ItemAttributes, ItemIds, Large, ListmaniaLists, Medium,
    MerchantItemAttributes, OfferFull, OfferListings, OfferSummary, Offers,
    PromotionDetails, PromotionSummary, PromotionalTag, RelatedItems, Request,
    Reviews, SalesRank, SearchBins, SearchInside, ShippingCharges,
    Similarities, Small, Subjects, Tags, TagsSummary, Tracks, VariationImages,
    VariationMatrix, VariationMinimum, VariationOffers, VariationSummary,
    Variations.
    """


class InvalidParameterValue(AWSError):
    """
    The specified ItemId parameter is invalid. Please change this value and
    retry your request.
    """


class InvalidListType(AWSError):
    """
    The value you specified for ListType is invalid. Valid values include:
    BabyRegistry, Listmania, WeddingRegistry, WishList.
    """


class NoSimilarityForASIN(AWSError):
    """
    When you specify multiple items, it is possible for there to be no
    intersection of similar items.
    """


class NoExactMatchesFound(AWSError):
    """
    We did not find any matches for your request.
    """


class TooManyRequests(AWSError):
    """
    You are submitting requests too quickly and your requests are being
    throttled. If this is the case, you need to slow your request rate to one
    request per second.
    """


class NotEnoughParameters(AWSError):
    """
    Your request should have at least one parameter which you did not submit.
    """


class InvalidParameterCombination(AWSError):
    """
    Your request contained a restricted parameter combination.
    """


class DeprecatedOperation(AWSError):
    """
    The specified feature (operation) is deprecated.
    """


class InvalidOperation(AWSError):
    """
    The specified feature (operation) is invalid.
    """


class InvalidCartItem(AWSError):
    """
    The item you specified, ???, is not eligible to be added to the cart. Check
    the item's availability to make sure it is available.
    """


class ItemAlreadyInCart(AWSError):
    """
    The item you specified, ???, is already in your cart.

    .. deprecated:: 0.2.6
    """


class CartInfoMismatch(AWSError):
    """
    Your request contains an invalid AssociateTag, CartId and HMAC combination.
    Please verify the AssociateTag, CartId, HMAC and retry.

    Remember that all Cart operations must pass in the CartId and HMAC that were
    returned to you during the CartCreate operation.
    """


class InvalidCartId(AWSError):
    """
    Your request contains an invalid value for CartId. Please check your CartId
    and retry your request.
    """


class AccountLimitExceeded(AWSError):
    """
    Account limit of 2000 requests per hour exceeded.
    """


DEFAULT_ERROR_REGS = {
    'invalid-value': re.compile(
        'The value you specified for (?P<parameter>\w+) is invalid.'),

    'invalid-parameter-value': re.compile(
        '(?P<value>.+?) is not a valid value for (?P<parameter>\w+). Please '
        'change this value and retry your request.'),

    'no-similarities': re.compile(
        'There are no similar items for this ASIN: (?P<ASIN>\w+).'),

    'not-enough-parameters': re.compile(
        'Your request should have atleast (?P<number>\d+) of the following '
        'parameters: (?P<parameters>[\w ,]+).'),

    'invalid-parameter-combination': re.compile(
        'Your request contained a restricted parameter combination.'
        '\s*(?P<message>\w.*)$'),  # only the last bit is of interest here

    'already-in-cart': re.compile(
        'The item you specified, (?P<item>.*?), is already in your cart.'),

    'missing-parameters': re.compile(
        'Your request is missing required parameters. Required parameters '
        'include (?P<parameter>\w+).'),
}

def _e(error_class, *args, **kwargs):
    """
    Returns an exception of type ``error_class`` based on an instance of
    :class:`AWSError`  all relevant information appended.
    """
    exc = sys.exc_info()[1]
    error = error_class(*args)
    error.msg = exc.msg
    error.code = exc.code
    error.xml = exc.xml
    return error

