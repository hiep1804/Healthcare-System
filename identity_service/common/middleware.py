import uuid
from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware to handle X-Request-Id and X-Correlation-Id headers.
    Generates X-Request-Id if not provided.
    Passes both headers through to the response.
    """

    def process_request(self, request):
        request_id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        correlation_id = request.META.get('HTTP_X_CORRELATION_ID', request_id)
        request.request_id = request_id
        request.correlation_id = correlation_id

    def process_response(self, request, response):
        request_id = getattr(request, 'request_id', None)
        correlation_id = getattr(request, 'correlation_id', None)
        if request_id:
            response['X-Request-Id'] = request_id
        if correlation_id:
            response['X-Correlation-Id'] = correlation_id
        return response
