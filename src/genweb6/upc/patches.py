from urllib.parse import urlparse

import logging
import os

logger = logging.getLogger('plone.cachepurging')

def purge(self, session, url, httpVerb="PURGE"):
    """Perform the single purge request.

    Returns a triple ``(resp, xcache, xerror)`` where ``resp`` is the
    response object for the connection, ``xcache`` is the contents of the
    X-Cache header, and ``xerror`` is the contents of the first header
    found of the header list in ``self.errorHeaders``.
    """
    __traceback_info__ = url
    logger.debug("making %s request to %s", httpVerb, url)
    resp = session.request(httpVerb, url, timeout=self.timeout)
    xcache = resp.headers.get("x-cache", "")
    xerror = ""
    #import ipdb; ipdb.set_trace()
    ZOPE_HOME = os.environ['PWD']
    (scheme, host, path, params, query, fragment) = urlparse(url)
    try:
        f = open(ZOPE_HOME + '/var/log/urls_to_purge', 'a')
        f.write(path + '\n')
        f.close()
    except IOError:
        logger.warning('Can not write to urls_to_purge file on %s/var/log', ZOPE_HOME)
    except KeyError:
        logger.warning('No env variable called ZOPE_HOME')
    for header in self.errorHeaders:
        xerror = resp.headers.get(header, "")
        if xerror:
            # Break on first found.
            break
    logger.debug("%s of %s: %s %s", httpVerb, url, resp.status_code, resp.reason)
    return resp, xcache, xerror
