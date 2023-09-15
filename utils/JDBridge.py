import logging
import re

import uvicorn

from db.SQLite import DBService
from utils.QL import QLService
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, WebSocket, APIRouter
from pydantic import BaseModel, Field


class Cookie(BaseModel):
    cookie: str = Field("")
    qq: str = Field("")
    wx: str = Field("")


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("JD_logger")
logging.basicConfig(format=LOG_FORMAT)

qlService = QLService()
db = DBService()


def add_cookie(cookie_list, remarks="", qq="", wx=""):
    envs_type = cookie_list[0]
    pin = cookie_list[0] + "_" + cookie_list[1]
    value = cookie_list[2]
    #   检查cookie是否已经在数据库
    cookie_in_envs = db.select_envs_by_pin(pin)
    #   添加新cookie
    if not cookie_in_envs:
        result = qlService.add_envs(name=envs_type, value=value, remarks=remarks)
        data = get_data(result)
        db.insert_ql_envs(data, qq_num=qq, wx_num=wx)
        return "cookie 添加成功"
    #   更新cookie
    else:
        id = cookie_in_envs[0]
        name = cookie_in_envs[2]
        qq = cookie_in_envs[10]
        wx = cookie_in_envs[11]
        result = qlService.update_envs(envs_id=id, name=name, value=value, remarks=remarks)
        if result is None:
            return
        data = get_data(result)
        db.update_ql_envs(data, qq_num=qq, wx_num=wx)
    return "cookie 更新成功"
    # envs_id = data['id']
    # envs_name = data['name']
    # envs_value = data['value']
    # envs_remarks = data['remarks']
    # envs_status = data['status']
    # envs_timestamp = data['timestamp']
    # envs_position = data['position']
    # envs_update_time = data['updatedAt']
    # envs_create_time = data['createdAt']


def query_asset():
    return None


def get_data(result):
    if result['code'] == 200:
        return result['data']
    else:
        logger.info("返回结果错误")
        logger.error(result['message'])


def list_envs():
    result = qlService.get_envs_list()
    data = get_data(result)
    return data


def refresh_envs_list():
    data = list_envs()
    logger.info("刷新 JD Cookie变量")
    db.insert_ql_envs(data)

refresh_envs_list()


# def check_cookie(cookie_value):
#     if cookie_value[-1] != ";":
#         cookie_value = cookie_value + ";"
#     if cookie_value.__contains__("pt_pin=") and cookie_value.__contains__("pt_key="):
#         pt_pin = re.findall(r"pt_pin=.*?;", cookie_value)[0]
#         user_id = pt_pin[7:len(pt_pin) - 1]
#         envs_type = "JD_COOKIE"
#     elif cookie_value.__contains__("pin=") and cookie_value.__contains__("wskey="):
#         pt_pin = re.findall(r"pin=.*?;", cookie_value)[0]
#         user_id = pt_pin[4:len(pt_pin) - 1]
#         envs_type = "JD_WSCK"
#     else:
#         logger.info("输入cookie错误, 请重新输入")
#         return None
#     return extract_cookie(envs_type, user_id, cookie_value)
#
#
# def extract_cookie(envs_type, user_id, value):
#     r = list()
#     r.append(envs_type)
#     r.append(user_id)
#     r.append(value)
#     return r


if __name__ == '__main__':
    # pt_key=app_openAAJlAFfjU1kofX83SxRirnw862FS56GOlKWMmX1sPZkNdwRt3STA;pt_pin=test1;
    # pin=WSCKtest;wskey = AAJlAFxjAECa9Zig26MmdrX7Fafkqy2WEHYDBys9yaf4pPQgPMqf1ysEHKaLdUiXrT - cGQUfCRGK3xP3m3LfEZ7ne2YPn1JA;
    uvicorn.run('JDBridge:app', host='0.0.0.0', port=8000, reload=True)
