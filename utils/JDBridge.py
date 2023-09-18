import logging
import re
import urllib.parse
from operator import itemgetter

from db.SQLite import DBService
from test import timestamp
from utils.QL import QLService


class JDService:
    def __init__(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        logging.getLogger().setLevel(logging.INFO)
        self.logger = logging.getLogger("JD_logger")
        logging.basicConfig(format=LOG_FORMAT)

        self.qlService = QLService()
        self.db = DBService()
        self.refresh_envs_list()

    def add_cookie(self, cookie_dict, remarks="", qq="", wx=""):
        envs_type = cookie_dict["envs_type"]
        pin = cookie_dict["user_id"]
        cookie = cookie_dict["cookie"]
        #   检查cookie是否已经在数据库
        cookie_in_envs = self.db.select_envs_by_pin(pin, envs_type)
        #   添加新cookie
        if not cookie_in_envs:
            result = self.qlService.add_envs(name=envs_type, value=cookie, remarks=remarks)
            data = self.get_data(result)
            if data is None:
                return "cookie 完全相同，请重新获取cookie"
            self.db.insert_ql_envs(data, qq_num=qq, wx_num=wx)
            return "cookie 添加成功"
        #   更新cookie
        else:
            envs_id = cookie_in_envs[0]
            # envs_type = cookie_in_envs[1]
            result = self.qlService.update_envs(envs_id=envs_id, envs_type=envs_type, value=cookie, remarks=remarks)
            if result is None:
                return
            data = self.get_data(result)
            # 更新数据库QQ,WX和JD绑定关系
            self.db.update_ql_envs(data, envs_type=envs_type, qq_num=qq, wx_num=wx)
        return "cookie 更新成功"

    def query_asset(self, qq="", wx=""):
        user_name = ""
        asset = "查询异常"
        if self.db.select_info_by_qq(qq):
            # 查看cookie状态
            result_list = self.db.select_info_by_qq(qq)
            id = result_list[0]
            cookie_status = self.get_data(self.qlService.get_envs_list(id))["status"]
            if cookie_status != 0:
                return "cookie 已失效"
            user_name = urllib.parse.unquote(result_list[1])
            log_path = self.get_newest_logs_name()
            log = self.qlService.get_logs(log_path)
            asset = self.format_log_to_asset(logs=log, jd_name=user_name)
        return asset

    def format_log_to_asset(self, logs, jd_name):
        result = ""
        logs = logs.split("\n")
        while '' in logs:
            logs.remove('')
        flag = False
        for i in logs:
            if not i.__contains__("******") and not flag:
                continue
            elif not flag:
                # 匹配是否对应账号
                _jd_name = re.findall(r"】(\w+)", i)[0]
                if _jd_name == jd_name:
                    flag = True
                else:
                    flag = False
                continue
            # 截取完毕
            elif i.__contains__("******") and flag:
                break
            elif i.__contains__("开始发送通知"):
                break
            result = result + i + "\n"
        if len(result) == 0:
            result = f"找不到账号{jd_name}, 请重新添加cookie绑定"
        return result

    def get_newest_logs_name(self):
        full_logs = self.qlService.get_logs()
        # 筛选出对应的log的文件夹
        log_time = 0
        new_log = dict()
        for i in full_logs:
            if i["title"].__contains__("jd_bean_change") and i["mtime"] > log_time:
                log_time = i["mtime"]
                new_log = i["children"]
        if new_log is not None:
            log = sorted(new_log, key=itemgetter("mtime"), reverse=True)[0]
            result = log["title"] + "?path=" + log["parent"] + "&t=" + str(timestamp)
        else:
            result = ""
        return result

    def get_data(self, result):
        if result['code'] == 200:
            return result['data']
        else:
            self.logger.info("返回结果错误")
            self.logger.error(result['message'])
            return None

    def list_envs(self):
        result = self.qlService.get_envs_list()
        data = self.get_data(result)
        return data

    def refresh_envs_list(self):
        data = self.list_envs()
        self.logger.info("刷新 JD Cookie变量")
        self.db.insert_ql_envs(data)

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
