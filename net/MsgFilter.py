import json
import re
import logging

from utils.JDBridge import add_cookie

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("WS_logger")
logging.basicConfig(format=LOG_FORMAT)


def main_filter(msg_dict):
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
    msg = msg_dict["message"]
    cookie = cookie_filter(msg)
    if cookie is not None:
        cookie_status = add_cookie(cookie, remarks="", qq=user_id)
        print(cookie_status)
        if cookie_status is not None:
            return result_json(action=action, msg_type=msg_type, msg_id=msg_id, msg=cookie_status, echo="")
    # return result_json(status="failed", retcode=1400, data=None, echo=echo)
    return None


def cookie_filter(cookie_value):
    cookie_value = cookie_value.replace(" ", "")
    if cookie_value[-1] != ";":
        cookie_value = cookie_value + ";"
    if cookie_value.__contains__("pt_pin=") and cookie_value.__contains__("pt_key="):
        pt_pin = re.findall(r"pt_pin=.*?;", cookie_value)[0]
        pt_key = re.findall(r"pt_key=.*?;", cookie_value)[0]
        user_id = pt_pin[7:len(pt_pin) - 1]
        envs_type = "JD_COOKIE"
    elif cookie_value.__contains__("pin=") and cookie_value.__contains__("wskey="):
        pt_pin = re.findall(r"pin=.*?;", cookie_value)[0]
        pt_key = re.findall(r"pt_key=.*?;", cookie_value)[0]

        user_id = pt_pin[4:len(pt_pin) - 1]
        envs_type = "JD_WSCK"
    else:
        logger.info("非cookie信息")
        return None
    cookie_str = pt_pin + pt_key
    return extract_cookie(envs_type, user_id, cookie_str)


def extract_cookie(envs_type, user_id, value):
    r = list()
    r.append(envs_type)
    r.append(user_id)
    r.append(value)
    return r


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
