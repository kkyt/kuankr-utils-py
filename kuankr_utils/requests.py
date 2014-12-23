#coding: utf8
#http://mihai.ibanescu.net/chunked-encoding-and-python-requests

from __future__ import absolute_import

import httplib
import requests
#from requests.adapters import HTTPAdapter, TimeoutSauce
from requests.adapters import *
from requests.adapters import _ProxyError, _HTTPError, _SSLError
import sys

def response_hook(response, *args, **kwargs):
    response.iter_chunks = lambda amt=None: iter_chunks(response.raw._fp, amt=amt)
    return response

def iter_chunks(response, amt=None):
    """
    A copy-paste version of httplib.HTTPConnection._read_chunked() that
    yields chunks served by the server.
    """
    if response.chunked:
        while True:
            line = response.fp.readline().strip()
            arr = line.split(';', 1)
            try:
                chunk_size = int(arr[0], 16)
            except ValueError:
                response.close()
                raise httplib.IncompleteRead(chunk_size)
            if chunk_size == 0:
                break
            value = response._safe_read(chunk_size)
            yield value
            # we read the whole chunk, get another
            response._safe_read(2)      # toss the CRLF at the end of the chunk

        # read and discard trailer up to the CRLF terminator
        ### note: we shouldn't have any trailers!
        while True:
            line = response.fp.readline()
            if not line:
                # a vanishingly small number of sites EOF without
                # sending the trailer
                break
            if line == '\r\n':
                break

        # we read everything; close the "file"
        response.close()
    else:
        # Non-chunked response. If amt is None, then just drop back to
        # response.read()
        if amt is None:
            r = response.read()
            #NOTE: don't yield empty chunk
            if r:
                yield r
        else:
            # Yield chunks as read from the HTTP connection
            while True:
                ret = response.read(amt)
                if not ret:
                    break
                yield ret

class HTTPStreamAdapter(HTTPAdapter):
    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        import gevent
        conn = self.get_connection(request.url, proxies)

        self.cert_verify(conn, request.url, verify, cert)
        url = self.request_url(request, proxies)
        self.add_headers(request)

        chunked = not (request.body is None or 'Content-Length' in request.headers)

        timeout = TimeoutSauce(connect=timeout, read=timeout)

        try:
            if not chunked:
                resp = conn.urlopen(
                    method=request.method,
                    url=url,
                    body=request.body,
                    headers=request.headers,
                    redirect=False,
                    assert_same_host=False,
                    preload_content=False,
                    decode_content=False,
                    retries=self.max_retries,
                    timeout=timeout
                )

            # Send the request.
            else:
                if hasattr(conn, 'proxy_pool'):
                    conn = conn.proxy_pool

                low_conn = conn._get_conn(timeout=timeout)

                try:
                    low_conn.putrequest(request.method,
                                        url,
                                        skip_accept_encoding=True)

                    for header, value in request.headers.items():
                        low_conn.putheader(header, value)

                    low_conn.endheaders()

                    def send_body():
                        for i in request.body:
                            low_conn.send(hex(len(i))[2:].encode('utf-8'))
                            low_conn.send(b'\r\n')
                            low_conn.send(i)
                            low_conn.send(b'\r\n')
                            #must sleep to make streams LIVE
                            gevent.sleep(0)
                        low_conn.send(b'0\r\n\r\n')
                    gevent.spawn(send_body)

                    r = low_conn.getresponse()
                    resp = HTTPResponse.from_httplib(
                        r,
                        pool=conn,
                        connection=low_conn,
                        preload_content=False,
                        decode_content=False
                    )
                except:
                    # If we hit any problems here, clean up the connection.
                    # Then, reraise so that we can handle the actual exception.
                    low_conn.close()
                    raise
                else:
                    # All is well, return the connection to the pool.
                    conn._put_conn(low_conn)

        except socket.error as sockerr:
            raise ConnectionError(sockerr, request=request)

        except MaxRetryError as e:
            raise ConnectionError(e, request=request)

        except _ProxyError as e:
            raise ProxyError(e)

        except (_SSLError, _HTTPError) as e:
            if isinstance(e, _SSLError):
                raise SSLError(e, request=request)
            elif isinstance(e, TimeoutError):
                raise Timeout(e, request=request)
            else:
                raise

        return self.build_response(request, resp)


"""
def main():
    if len(sys.argv) != 2:
        print "Usage: %s " % sys.argv[0]
        return 1

    headers = { 'Accept-Encoding' : 'identity' }
    sess = requests.sessions.Session()
    sess.headers.update(headers)
    sess.verify = False
    sess.prefetch = False
    sess.hooks.update(response=response_hook)
    resp = sess.get(sys.argv[1])
    cb = lambda x: sys.stdout.write("Read: %s\n" % x)
    for chunk in resp.iter_chunks():
        cb(chunk)

"""

