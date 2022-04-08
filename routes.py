__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from controller import document, bid_detection


def add_prefix(uri):
    return "{}{}".format('/api/v1/bidrigging', uri)


def register_urls(api):
    """
    Maps all the endpoints with controllers.
    """
    api.add_resource(document.Document, add_prefix('/documents'))
    api.add_resource(bid_detection.BidRiggingDetection, add_prefix('/detect'))

