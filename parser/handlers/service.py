# coding=utf-8
# __author__ = 'Mio'
import json
import os.path
from operator import itemgetter

from schema import Schema, Use, Optional
from tornado.log import app_log
from tornado import gen

from parser.utils.gtornado.web import BaseRequestHandler, AGRequestHandler
from parser.utils.json_encoder import MySQLQueryEncoder
from parser.utils.tracking_column import set_last_row, clear_last_row, get_tracking_column
from parser.models.mdb_service_logic import MDBLogic
import mdbread


class TestSendFile(AGRequestHandler):
    @gen.coroutine
    def post(self):
        mdb_path = os.path.join(self.settings['tmp_path'], "ProjectData.mdb")
        with open(mdb_path, 'rb') as f:
            code, body, headers = yield self.get_response(MDBLogic.post(
                query_parameters={
                    "type": "aoi", "file_name": "2", "table": "Project",
                    "tracking_column_type": "id",
                    "tracking_column": "ID"
                },
                body_parameters=f.read()))

        self.write_ag_response(code, body, headers)


class FetchDataHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        """Secure fetch data by using MySQL parser-service.
        """
        data = self.post_query_schema()
        if not data:
            return

        if data['clear_run'] is True:
            clear_last_row(data['type'])

        if data['tracking_column'] and data['tracking_column_type']:
            tracking_column = get_tracking_column(
                data['type'], data['tracking_column'], data['tracking_column_type'])
        else:
            tracking_column = None

        mdb_path = os.path.join(self.settings['tmp_path'], data['file_name'])

        with open(mdb_path, 'wb') as f:
            f.write(self.request.body)

        db = mdbread.MDB(mdb_path)
        if data['table'] not in db.tables:
            self.write_error_response("table {} not found".format(data['table']))
            return

        table = db[data['table']]

        result = []
        for row in table.records():
            d = dict(zip(table.columns, row))
            if tracking_column:
                if d.get(data['tracking_column']) and d[data['tracking_column']] > tracking_column:
                    result.append(d)
                else:
                    continue
            else:
                result.append(dict(zip(table.columns, row)))

        result.sort(key=itemgetter('ID'))

        set_last_row(data['type'], result[-1] if result else None)
        secure_result = dict(error_code=0, message="", content=result)
        result_dumped = json.dumps(secure_result, cls=MySQLQueryEncoder)
        self.set_header("Content-Type", "application/json;charset=UTF-8")
        self.write(result_dumped)
        return

    def post_query_schema(self):
        try:
            data = Schema({
                "type": Use(str),
                "file_name": Use(str),
                "table": Use(str),
                Optional("tracking_column", default=None): Use(str),
                Optional("tracking_column_type", default=None): Use(str),
                Optional("clear_run", default=False): Use(bool)
            }).validate(self.get_query_args())
        except Exception as e:
            app_log.error(e)
            self.write_parse_args_failed_response(content=e.args)
            return False
        else:
            return data
