from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token

class ReplaceCSRFTokenMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Ensure the response contains the placeholder and is of a type that can be modified
        if response.get('Content-Type', '').startswith('text/html'):
            content = response.content.decode()
            if 'csrf_token_placeholder' in content:
                csrf_token = get_token(request)
                # Replace the placeholder with the actual CSRF token
                response.content = content.replace(
                    'csrf_token_placeholder', csrf_token
                ).encode()
        return response
