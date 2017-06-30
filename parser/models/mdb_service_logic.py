# coding=utf-8
# __author__ = 'mio'
from ujson import dumps

from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat
from tornado.log import app_log


MDB_HOST = "localhost"
# MDB_HOST = "mdb-parser-service"
mdb_logic = "http://{host}:6464/data".format(host=MDB_HOST)


class MDBLogic(object):
    request_timeout = 2
    connect_timeout = 0.5

    @classmethod
    def post(cls, query_parameters=None, body_parameters=None):
        url = url_concat(mdb_logic, query_parameters)
        # app_log.info(">>>>> post {} body:{}".format(url, body_parameters))
        return HTTPRequest(url=url, method='POST', body=body_parameters,
                           connect_timeout=cls.connect_timeout, request_timeout=cls.request_timeout)

    @classmethod
    def get(cls, query_parameters=None):
        url = url_concat(mdb_logic, query_parameters)
        app_log.info(">>>>> get {}".format(url))
        return HTTPRequest(url=url, method="GET",
                           connect_timeout=cls.connect_timeout, request_timeout=cls.request_timeout)
