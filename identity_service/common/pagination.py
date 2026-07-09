from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination matching the API design spec:
    {
        "data": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 125
        }
    }
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('data', data),
            ('pagination', OrderedDict([
                ('page', self.page.number),
                ('page_size', self.get_page_size(self.request)),
                ('total', self.page.paginator.count),
            ])),
        ]))
