import json
import re
import logging

from utils.JDBridge import JDService

jdService = JDService()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("WS_logger")
logging.basicConfig(format=LOG_FORMAT)


def main_filter(msg_dict):

    return_msg = ""
    msg = msg_dict["message"]
    msg_type = msg_dict["message_type"]
    if msg_type == "private":
        user_id = msg_dict["user_id"]
        group_id = ""
        msg_id = user_id
        msg_type = "user_id"
        action = "send_private_msg"
    elif msg_type == "group":
        user_id = msg_dict["user_id"]
        group_id = msg_dict["group_id"]
        msg_id = group_id
        action = "send_group_msg"
        msg_type = "group_id"

    if msg == "查询":
        return_msg = query_filter(user_id)
    elif (msg.__contains__("pt_pin=") and msg.__contains__("pt_key=")) or (
            msg.__contains__("pin=") and msg.__contains__("wskey=")):
        return_msg = cookie_filter(msg, user_id)

    if len(return_msg) != 0:
        result = result_json(action=action, msg_type=msg_type, msg_id=msg_id, msg=return_msg, echo="")
        return result
    return None


def query_filter(user_id):
    result = jdService.query_asset(qq=user_id)
    return result


def cookie_filter(msg, qq):
    cookie = msg
    cookie = cookie.replace(" ", "")
    if cookie[-1] != ";":
        cookie = cookie + ";"
    if cookie.__contains__("pt_pin=") and cookie.__contains__("pt_key="):
        pt_pin = re.findall(r"pt_pin=.*?;", cookie)[0]
        pt_key = re.findall(r"pt_key=.*?;", cookie)[0]
        user_id = pt_pin[7:len(pt_pin) - 1]
        envs_type = "JD_COOKIE"
    elif cookie.__contains__("pin=") and cookie.__contains__("wskey="):
        pt_pin = re.findall(r"pin=.*?;", cookie)[0]
        pt_key = re.findall(r"pt_key=.*?;", cookie)[0]
        user_id = pt_pin[4:len(pt_pin) - 1]
        envs_type = "JD_WSCK"

    cookie_str = pt_pin + pt_key
    cookie_dict = {
        "envs_type": envs_type,
        "user_id": user_id,
        "cookie": cookie_str
    }
    cookie_status = jdService.add_cookie(cookie_dict, remarks="", qq=qq)
    return cookie_status


def result_json(action, msg_type, msg_id, msg, echo):
    result = {
        "action": action,
        "params": {
            f"{msg_type}": msg_id,
            "message": msg
        }
    }
    # result = json.dumps(js)
    logger.info(result)
    return result
