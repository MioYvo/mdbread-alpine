# coding=utf-8
# __author__ = 'Mio'
import json
import os.path
from collections import defaultdict

from schema import Schema, Use, Optional
from tornado.log import app_log
from tornado import gen

from parser.utils.gtornado.web import BaseRequestHandler, AGRequestHandler
from parser.utils.json_encoder import MySQLQueryEncoder
from parser.utils.tracking_column import get_tracking_column, set_last_row, TypeNotFoundException, \
    NotPickleLoadException, clear_last_row
from parser.models.mdb_service_logic import MDBLogic
import mdbread


class TestSendFile(AGRequestHandler):
    @gen.coroutine
    def post(self):

        mdb_path = os.path.join(self.settings['tmp_path'], "ProjectData.mdb")
        with open(mdb_path, 'rb') as f:
            code, body, headers = yield self.get_response(MDBLogic.post(
                query_parameters={"type": "aoi", "name": "2"},
                body_parameters=f.read()))

        self.write_ag_response(code, body, headers)


class FetchDataHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        """Secure fetch data by using MySQL parser-service.
        """
        mdb_path = os.path.join(self.settings['tmp_path'], self.get_query_argument('name'))

        with open(mdb_path, 'wb') as f:
            f.write(self.request.body)

        db = mdbread.MDB(mdb_path)

        rst = defaultdict(list)
        for table in db.tables:
            for row in db[table].records():
                rst[table].append(row)
        self.write_response(rst)
        return
