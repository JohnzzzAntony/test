import re
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class NoCacheMiddleware(MiddlewareMixin):
    """
    Middleware that prevents browser caching of HTML pages.
    Ensures admin changes appear immediately without stale cache.
    """
    def process_response(self, request, response):
        # Only apply to HTML responses from the main site (not admin)
        if 'text/html' in response.get('Content-Type', '') and not request.path.startswith('/admin/'):
            # Prevent browser caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Vary'] = 'Cookie, Authorization'
        return response


class StripHTMLCommentsMiddleware(MiddlewareMixin):
    """
    Middleware that strips HTML comments from outgoing responses to prevent
    sensitive developer context or 'green headlines' from being visible in page source.
    """
    def process_response(self, request, response):
        # Only process HTML responses
        if 'text/html' in response.get('Content-Type', ''):
            content = response.content.decode('utf-8', errors='ignore')
            
            # 1. Strip HTML comments (except IE conditionals)
            comment_pattern = re.compile(r'<!--(?!\s*\[)[\s\S]*?-->')
            new_content = comment_pattern.sub('', content)
            
            # 2. Basic Minification: Collapse multiple spaces and newlines
            # This makes the source look more 'production-ready' and hides structure
            # We only do this if DEBUG is False to avoid breaking script tags or preformatted text
            if not settings.DEBUG:
                # Replace multiple spaces with a single space
                new_content = re.sub(r'[ \t]+', ' ', new_content)
                # Remove spaces at the start/end of lines
                new_content = re.sub(r'^[ \t]+|[ \t]+$', '', new_content, flags=re.MULTILINE)
                # Optionally collapse multiple newlines
                new_content = re.sub(r'\n+', '\n', new_content)
            
            response.content = new_content.encode('utf-8')
        return response
