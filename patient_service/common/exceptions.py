from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Custom exception handler for standardized error responses."""
    response = exception_handler(exc, context)
    request = context.get('request')
    request_id = getattr(request, 'request_id', None) if request else None

    if response is not None:
        error_code = getattr(exc, 'default_code', 'ERROR')
        if isinstance(error_code, str):
            error_code = error_code.upper()
        else:
            error_code = 'ERROR'

        message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)

        error_response = {
            'error': {
                'code': error_code,
                'message': message,
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data},
                'request_id': request_id,
            }
        }
        response.data = error_response
        return response

    return Response(
        {
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred.',
                'details': {},
                'request_id': request_id,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
