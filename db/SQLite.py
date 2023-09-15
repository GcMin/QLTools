import logging
import re
import sqlite3
import threading
import sys


class DBService:
    def __init__(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        logging.getLogger().setLevel(logging.INFO)
        self._logger = logging.getLogger("DB_logger")
        logging.basicConfig(format=LOG_FORMAT)
        self._conn = sqlite3.connect('./resources/QLJD.db', check_same_thread=False)
        self._cur = self._conn.cursor()
        self.init_talbes()

    def init_talbes(self):
        sql = "create table if not exists ql_envs" \
              "(id      int primary key," \
              "pin      text unique," \
              "name     text," \
              "value    text," \
              "remarks  text," \
              "timestamp    text," \
              "status   int," \
              "position int," \
              "createdAt    text," \
              "updatedAt    text," \
              "qq_num   text," \
              "wx_num text" \
              ")"
        self._cur.execute(sql)
        self._conn.commit()

    def select_envs_by_pin(self, pin):
        sql = f"select * from ql_envs where pin='{pin}'"
        try:
            result = self._cur.execute(sql).fetchone()
            if result is None:
                return False
            else:
                return result
        except Exception as e:
            self._logger.info(f"{str(e)}")
            self._logger.error(e)

    def update_ql_envs(self, data, qq_num="", wx_num=""):
        value = data['value']
        user_name = self.retrieve_pin(value)
        sql = "update ql_envs " \
              f"set id={data['id']}," \
              f"pin='{data['name']}_{user_name}'," \
              f"name='{data['name']}'," \
              f"value='{data['value']}'," \
              f"remarks='{data['remarks']}'," \
              f"timestamp='{data['timestamp']}'," \
              f"status={data['status']}," \
              f"position={data['position']}," \
              f"createdAt='{data['createdAt']}'," \
              f"updatedAt='{data['updatedAt']}'," \
              f"qq_num='{qq_num}'," \
              f"wx_num='{wx_num}' " \
              f"where id = {data['id']}"
        try:
            self._logger.info(sql)
            self._cur.execute(sql)
            self._logger.info(f"更新账号:{user_name}成功")
        except Exception as e:
            self._logger.info(f"{str(e)}")
            self._logger.error(e)
        self._conn.commit()

    def insert_ql_envs(self, data, qq_num="", wx_num=""):
        for i in data:
            envs_type = i['name']

            if envs_type != 'JD_COOKIE' and envs_type != 'JD_WSCK':
                continue
            value = i['value']
            user_name = self.retrieve_pin(value)
            sql = "insert or ignore into ql_envs " \
                  f"values({i['id']},'{envs_type}_{user_name}','{i['name']}','{i['value']}','{i['remarks']}','{i['timestamp']}'," \
                  f"{i['status']},{i['position']},'{i['createdAt']}','{i['updatedAt']}','{qq_num}','{wx_num}')"
            try:
                self._logger.info(sql)
                self._cur.execute(sql)
                self._logger.info(f"添加账号:{user_name}成功")
            except Exception as e:
                self._logger.info(f"{str(e)}")
                self._logger.error(e)
        self._conn.commit()

    def retrieve_pin(self, str):
        user_id = None
        if str.__contains__("pt_pin=") and str.__contains__("pt_key="):
            pt_pin = re.findall(r"pt_pin=.*?;", str)[0]
            user_id = pt_pin[7:len(pt_pin) - 1]
        elif str.__contains__("pin=") and str.__contains__("wskey="):
            pt_pin = re.findall(r"pin=.*?;", str)[0]
            user_id = pt_pin[4:len(pt_pin) - 1]
        return user_id


if __name__ == '__main__':
    db = DBService()
    db.select_ql_envs_by_pin()