import logging
from urllib.parse import urljoin, urlparse

from w3lib.url import safe_url_string

from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware, _build_redirect_request

class RedirectMiddleware2(BaseRedirectMiddleware):
    """
    Handle redirection of requests based on response status
    and meta-refresh html tag.
    """

    def process_response(self, request, response, spider):
        if (
            request.meta.get('dont_redirect', False)
            or response.status in getattr(spider, 'handle_httpstatus_list', [])
            or response.status in request.meta.get('handle_httpstatus_list', [])
            or request.meta.get('handle_httpstatus_all', False)
        ):
            return response
        print("############")
        allowed_status = (301, 302, 303, 307, 308, 200)
        print(response.headers, dir(response), response.request, request)
        if 'Location' not in response.headers or response.status not in allowed_status:
            return response
        print("############ 2")
        location = safe_url_string(response.headers['Location'])
        if response.headers['Location'].startswith(b'//'):
            request_scheme = urlparse(request.url).scheme
            location = request_scheme + '://' + location.lstrip('/')
        print("############ 3")
        redirected_url = urljoin(request.url, location)

        if response.status in (301, 307, 308) or request.method == 'HEAD':
            redirected = _build_redirect_request(request, url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        redirected = self._redirect_request_using_get(request, redirected_url)
        return self._redirect(redirected, request, spider, response.status)
