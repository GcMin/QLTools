import logging
import re
from functools import lru_cache

import uvicorn

from db.SQLite import DBService
from tools.QL import QLService
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel,Field


class Cookie(BaseModel):
    cookie: str = Field("")
    qq: str = Field("")
    wx: str = Field("")



class JDService:
    def __init__(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        logging.getLogger().setLevel(logging.INFO)
        self._logger = logging.getLogger("JD_logger")
        logging.basicConfig(format=LOG_FORMAT)

        self._qlService = QLService(api_url="http://192.168.67.245:5700",
                                    client_id="AUiUPsl-DAc3",
                                    client_secret="WtqCtvm06Qudq7x-R7ETPtAJ")
        self._db = DBService()



    @app.post("/addcookie")
    def add_Cookie(self, receieve_str: Cookie):
        #   检查是否符合cookie
        print(receieve_str)
        self._logger.info("进入")
        value = receieve_str.cookie
        qq = receieve_str.qq
        wx = receieve_str.wx
        remarks = qq
        self._logger.info(receieve_str)
        cookie_result = self.check_cookie(value)
        if cookie_result is not None:
            envs_type = cookie_result[0]
            pin = cookie_result[0] + "_" + cookie_result[1]
            #   检查cookie是否已经在数据库
            cookie_in_envs = self._db.select_envs_by_pin(pin)
            #   添加新cookie
            if not cookie_in_envs:
                result = self._qlService.add_envs(name=envs_type, value=value, remarks=remarks)
                data = self.get_data(result)
                self._db.insert_ql_envs(data, qq_num=qq, wx_num=wx)
            #   更新cookie
            else:
                id = cookie_in_envs[0]
                name = cookie_in_envs[2]
                qq = cookie_in_envs[10]
                wx = cookie_in_envs[11]
                result = self._qlService.update_envs(envs_id=id, name=name, value=value, remarks=remarks)
                data = self.get_data(result)
                self._db.update_ql_envs(data, qq_num=qq, wx_num=wx)
            # self.refresh_envs_list()
        # envs_id = data['id']
        # envs_name = data['name']
        # envs_value = data['value']
        # envs_remarks = data['remarks']
        # envs_status = data['status']
        # envs_timestamp = data['timestamp']
        # envs_position = data['position']
        # envs_update_time = data['updatedAt']
        # envs_create_time = data['createdAt']

    def query_Asset(self):
        return None

    def get_data(self, result):
        if result['code'] == 200:
            return result['data']
        else:
            self._logger.info("返回结果错误")
            self._logger.error(result['message'])

    def list_envs(self):
        result = self._qlService.get_envs_list()
        data = self.get_data(result)
        return data

    def refresh_envs_list(self):
        data = self.list_envs()
        self._logger.info("刷新 JD Cookie变量")
        self._db.insert_ql_envs(data)

    def check_cookie(self, str):
        list1 = list()
        if str.__contains__("pt_pin=") and str.__contains__("pt_key="):
            pt_pin = re.findall(r"pt_pin=.*?;", str)[0]
            user_id = pt_pin[7:len(pt_pin) - 1]
            envs_type = "JD_COOKIE"
            list1.append(envs_type)
            list1.append(user_id)
            return list1
        elif str.__contains__("pin=") and str.__contains__("wskey="):
            pt_pin = re.findall(r"pin=.*?;", str)[0]
            user_id = pt_pin[4:len(pt_pin) - 1]
            envs_type = "JD_WSCK"
            list1.append(envs_type)
            list1.append(user_id)
            return list1
        else:
            self._logger.info("输入cookie错误, 请重新输入")
            return None


# if __name__ == '__main__':
    jdService = JDService()
    # # cookie = "pt_pin=%E5%AE%85treasure;pt_key=AAJk81EiADB6HAJC8VtY1R3F0uo60HHx7lUdteery3Ke_MsPlYtpbZh_-82kNIhC8FJEDXAOwp0;"
    # cookie = "pt_pin=%E5%AE%85treasure;pt_key=AAJk8dddR3F060Hx7lUdteery3Ke_MsPlYtpbZh_-82kNIhC8FJEDXAOwp0;"
    # testCookie = "pt_pin=sss;pt_key=update;"
    # wsck = "pin=%E5%AE%85treasure; wskey=AAJktqd-AEDse6dxK5Z8ntVh81E3ISxKccff1AIvqgDAJe1jYM87H_E0k2VFmr41_RAR2DfHYgY4SVWefH84Z77AujCbnlRt;"
    #
    #
    # list1 = list()
    # list1.append("1")
    # if list1:
    #     print("1")
    app = FastAPI()
    app.include_router(jdService.router)
    uvicorn.run('JDBridge:app', host='0.0.0.0', port=8000, reload=True)
