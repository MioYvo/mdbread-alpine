# -*- coding: utf-8 -*-

import ujson as json

from tornado import httpclient, gen
from tornado.web import RequestHandler
from schema import Schema, SchemaError

from parser.utils.gtornado.http_code import (HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_422_UNPROCESSABLE_ENTITY,
                                             HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN,
                                             HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED,
                                             HTTP_599_LOGIC_RESPONSE_FAILED, is_success)
from parser.utils.gtornado.error_code import ERR_UNKNOWN, ERR_NO_CONTENT, ERR_ARG, ERR_MULTIPLE_OBJ_RETURNED


class BaseRequestHandler(RequestHandler):
    def options(self):
        # self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
        # self.set_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        pass

    def write_response(self, content=None, error_code=0, message="", status_code=HTTP_200_OK, reason=None):
        self.set_status(status_code, reason=reason)
        if status_code != HTTP_204_NO_CONTENT:
            # 如果是204的返回, http的标准是不能有body, 所以tornado的httpclient接收的时候会
            # 报错变成599错误
            self.write(dict(error_code=error_code, message=message, content=content))

    def write_error_response(self, content=None, error_code=ERR_UNKNOWN, message="UnknownError",
                             status_code=HTTP_400_BAD_REQUEST, reason=None):
        """
        错误响应
        :param error_code:
        :param message:
        :param status_code:
        :param content:
        :param reason:
        :return:
        """
        self.clear()
        if status_code == HTTP_422_UNPROCESSABLE_ENTITY and not reason:
            reason = message
        self.write_response(content=content, error_code=error_code, message=message,
                            status_code=status_code, reason=reason)
        # self.finish()

    def write_no_content_response(self):
        self.set_status(HTTP_204_NO_CONTENT)

    def write_not_found_entity_response(self, content=None, message="没有找到对应实体"):
        """
        查询id没有结果
        :param message:
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=ERR_NO_CONTENT, message=message,
                                  status_code=HTTP_400_BAD_REQUEST)

    def write_multiple_results_found_response(self, content=None):
        """
        查询获取单个数据时，找到不止一个
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=ERR_MULTIPLE_OBJ_RETURNED,
                                  message="MultipleObjectsReturned",
                                  status_code=HTTP_400_BAD_REQUEST)

    def write_unknown_error_response(self, content=None):
        """
        创建中的错误
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=ERR_UNKNOWN, message="UnknownError",
                                  status_code=HTTP_422_UNPROCESSABLE_ENTITY, reason="UNPROCESSABLE_ENTITY")

    def write_parse_args_failed_response(self, message="args parse failed", content=None):
        """
        参数解析错误
        :param message:
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=ERR_ARG, message=message,
                                  status_code=HTTP_400_BAD_REQUEST)

    def write_duplicate_entry(self, content=None):
        """
        插入操作，重复键值
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=1062, message="Duplicate entry",
                                  status_code=HTTP_500_INTERNAL_SERVER_ERROR, reason="Duplicate entry")

    def write_logic_error_response(self, content=None):
        """
        逻辑层返回错误
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=106, message="LogicResponseFailed",
                                  status_code=HTTP_422_UNPROCESSABLE_ENTITY, reason="logic response failed")

    def write_forbidden_response(self, content=None, message="Forbidden"):
        """
        被禁止
        :param message:
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=107, message=message,
                                  status_code=HTTP_403_FORBIDDEN)

    def write_refund_money_error(self, content=None):
        """
        退款失败
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=108, message="RefundMoneyFailed",
                                  status_code=HTTP_422_UNPROCESSABLE_ENTITY, reason="RefundMoneyFailed")

    def write_cost_money_error(self, content=None):
        """
        扣款失败
        :param content:
        :return:
        """
        self.write_error_response(content=content, error_code=109, message="CostMoneyFailed",
                                  status_code=HTTP_422_UNPROCESSABLE_ENTITY, reason="RefundMoneyFailed")

    def write_unauthorized(self, content=None, message="Unauthorized"):
        """
        身份验证失败
        :param content:
        :param message:
        :return:
        """
        self.write_error_response(content=content, error_code=110, message=message, status_code=HTTP_401_UNAUTHORIZED)

    def set_headers(self, headers):
        if headers:
            for header in headers:
                self.set_header(header, headers[header])

    def get_token(self):
        try:
            token = self.request.headers.get("Authorization").split(' ')[1]
            return token
        except Exception as e:
            self.write_forbidden_response("Can't get token {}".format(e))
            return False

    def get_query_args(self):
        """
        获取query_arguments，只取值列表最后一个
        :return:
        """
        return {key: value[-1] if isinstance(value[-1], str) else value[-1].decode()
                for key, value in self.request.query_arguments.items()}

    def get_body_args(self):
        """
        获取body_arguments, 只取列表最后一个
        :return:
        """
        if self.request.body:
            return json.loads(self.request.body)
        if self.request.body_arguments:
            return {key: value[-1]
                    for key, value in self.request.body_arguments.items()}
        return {}

    @staticmethod
    def parse_response_content(response_body):
        """
        解析返回内容
        :param response_body:
        :return:
        """
        try:
            data = Schema({
                "content": object,
                "message": str,
                "error_code": int
            }).validate(response_body)
        except SchemaError as e:
            return False, e
        else:
            return True, data


class AGRequestHandler(BaseRequestHandler):
    asyncHTTPClient = httpclient.AsyncHTTPClient()

    def write_ag_response(self, code, body, headers=None):
        # 写入请求头
        self.set_headers(headers)

        if code == HTTP_204_NO_CONTENT:
            self.write_response(status_code=HTTP_204_NO_CONTENT)
            return True
        if is_success(code):
            rst, data = self.parse_response_content(body)
            if rst is True:
                self.write_response(status_code=code, content=data['content'], message=data['message'])
                return True
            else:
                self.write_parse_args_failed_response(data)
                return None
        elif code == HTTP_599_LOGIC_RESPONSE_FAILED:
            self.write_logic_error_response(body)
            return None
        else:
            parse_rst, parse_data = self.parse_response_content(body)
            if parse_rst is True:
                self.write_error_response(
                    error_code=body['error_code'], message=body['message'], status_code=code, content=body['content']
                )
                return None
            else:
                self.write_parse_args_failed_response(parse_data)
                return None

    def return_ag_response_values(self, code, body, headers=None):
        """
        解析请求返回的信息，并返回数据，常用于错误信息返回（不使用headers）
        :param headers:
        :param code:
        :param body:
        :return:
        """
        if headers is not None:
            for i in ["X-Resource-Count"]:
                self.set_header(i, headers.get(i, ""))
                # for header in headers:
                #     self.add_header(header, headers[header])

        if code == HTTP_204_NO_CONTENT:
            self.write_response(status_code=HTTP_204_NO_CONTENT)
            return None
        elif is_success(code):
            rst, data = self.parse_response_content(body)
            if rst is True:
                return data
            else:
                self.write_parse_args_failed_response(data)
                return None
        elif code == HTTP_599_LOGIC_RESPONSE_FAILED:
            self.write_logic_error_response(body)
            return None
        else:
            parse_rst, parse_data = self.parse_response_content(body)
            if parse_rst is True:
                self.write_error_response(
                    error_code=body['error_code'], message=body['message'], status_code=code, content=body['content']
                )
                return None
            else:
                self.write_logic_error_response(parse_data)
                return None

    @gen.coroutine
    def get_response(self, request):
        """
        异步，获取单个request请求
        :param request: tornado.httpclient.HTTPRequest
        :return:
        """
        try:
            # response = yield httpclient.AsyncHTTPClient().fetch(request)
            response = yield self.asyncHTTPClient.fetch(request)
            code = response.code
            headers = response.headers
            headers.pop('Content-Length', None)
            if response.error:
                code, body = [HTTP_599_LOGIC_RESPONSE_FAILED, response.error.message]
            elif response.body:
                # print response.body
                body = json.loads(response.body)
            else:
                body = None
        except httpclient.HTTPError as http:
            # 失败请求4xx, 5xx
            code = http.code
            headers = None
            if http.response is None:
                body = http.message
            else:
                body = json.loads(http.response.body)

        raise gen.Return([code, body, headers])

    @gen.coroutine
    def get_response_list(self, request_list):
        """
        异步，获取列表中的request请求
        :param request_list: [tornado.httpclient.HTTPRequest, ...]
        :return:
        """
        # http_client = httpclient.AsyncHTTPClient()
        response_list = yield [self.asyncHTTPClient.fetch(request) for request in request_list]
        raise gen.Return(response_list)

    @gen.coroutine
    def get_response_dict(self, request_dict):
        """
        异步，获取字典中的request请求
        :param request_dict: {"key": tornado.httpclient.HTTPRequest, ...}
        :return:
        """
        # http_client = httpclient.AsyncHTTPClient()
        response_dict = yield {key: self.asyncHTTPClient.fetch(value) for key, value in request_dict.items()}
        raise gen.Return(response_dict)

    @staticmethod
    def parse_response_content(response_body):
        """
        解析返回内容
        :param response_body:
        :return:
        """
        try:
            data = Schema({
                "content": object,
                "message": str,
                "error_code": int
            }).validate(response_body)
        except SchemaError as e:
            return False, e.args
        else:
            return True, data
