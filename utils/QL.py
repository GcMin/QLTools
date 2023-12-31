import configparser
import json
import logging
import threading
from datetime import datetime

import requests


class QLService:
    def __init__(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        logging.getLogger().setLevel(logging.INFO)
        self._logger = logging.getLogger("QL")
        logging.basicConfig(format=LOG_FORMAT)
        self._lock = threading.Lock()
        # 读取青龙配置
        path = "./config.properties"
        config = configparser.ConfigParser()
        config.read(path)
        ql_address = config.get('QL', 'ql_url')
        client_id = config.get('QL', 'client_id')
        client_secret = config.get('QL', 'client_secret')

        self._url = f"{ql_address}/open"  # http://localhost:5700/open
        self._client_id = client_id
        self._client_secret = client_secret
        token = self.get_token()
        self._headers = {
            'Authorization': token,
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        self._envs_url = f"{self._url}/envs"
        self._logs_url = f"{self._url}/logs"

    def request_result(self, request_method, url, headers, data=None, msg=None):
        result_json = None
        try:
            result_json = requests.request(method=request_method,
                                           url=url,
                                           headers=headers,
                                           data=data).json()
            if result_json['code'] == 200:
                if msg is not None:
                    self._logger.info(msg)
                self._logger.info(f"请求{url}成功")
            else:
                self._logger.info(f"请求{url}失败:{result_json['message']}")
        except Exception as e:
            self._logger.info(f"request 失败{str(e)}")
            self._logger.error(e)
        return result_json

    def get_token(self):
        token = None
        url = f"{self._url}/auth/token?client_id={self._client_id}&client_secret={self._client_secret}"
        try:
            result_json = requests.get(url).json()
            if result_json['code'] == 200:
                token = f"{result_json['data']['token_type']} {result_json['data']['token']}"
            else:
                self._logger.info(f"登录失败:{result_json['message']}")
        except Exception as e:
            self._logger.info(f"登录失败{str(e)}")
            self._logger.error(e)
        return token

    def get_envs_list(self, envs_id=None):
        if envs_id is None:
            timestamp = datetime.timestamp(datetime.now())
            url = f"{self._envs_url}?t={timestamp}"
        else:
            url = f"{self._envs_url}/{envs_id}"
        return self.request_result("get", url, self._headers)

    def add_envs(self, value=None, name=None, remarks=None, msg=None):
        url = f"{self._envs_url}"
        new_envs = json.dumps([
            {
                "value": value,
                "name": name,
                "remarks": remarks
            }
        ])
        result = self.request_result("POST", url, self._headers, new_envs, msg)
        self._logger.info(f"添加新cookie成功 {name} {value}")
        return result

    def update_envs(self, envs_id, value, envs_type=None, remarks=None, msg=None):
        # 检查id是否还存在
        data = self.get_envs_list(envs_id=envs_id)["data"]
        if data is None:
            return None
        url = f"{self._envs_url}"
        new_envs = json.dumps(
            {
                "value": value,
                "name": envs_type,
                "remarks": remarks,
                "id": envs_id
            }
        )
        result = self.request_result("PUT", url, self._headers, new_envs, msg)
        self.enable_envs(envs_id, "enable")
        return result

    def enable_envs(self, envs_id, enable=None):
        url = f"{self._envs_url}/{enable}"
        new_envs = json.dumps(
            [
                envs_id
            ]
        )
        self.request_result("PUT", url, self._headers, new_envs)

    def delete_envs(self, envs_id, msg):
        url = f"{self._envs_url}"
        new_envs = json.dumps(
            [
                envs_id
            ]
        )
        return self.request_result("DELETE", url, self._headers, new_envs, msg)

    def get_logs(self, path=""):
        # test = "2023-09-18-08-28-00.log?path=6dylan6_jdpro_jd_bean_change_1983&t=1695022122383"
        url = f"{self._logs_url}/{path}"
        result = self.request_result("GET", url, self._headers)["data"]
        return result


