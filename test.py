import re
import urllib.parse
# str ="pt_key=app_openAAJlAFfjU1kofX83SxRirnw862FS56GOlKWMmX1sPZkNdwRt3STA;pt_pin=test1;"
# # str = "shshshfpb=AAk9j6qCKEdetDzc2AFPgEhFhCN5LoiCI2F_kfwAAAAA; __jd_ref_cls=Babel_dev_other_DDNC_exposure; __jda=122270672.16948819291931216833104.1694881929.1694913740.1694916110.3; __jdb=122270672.3.16948819291931216833104|3.1694916110; __jdc=122270672; __jdv=122270672%7Ckong%7Ct_1000089893_157_0_184__fde590c7f029435a%7Ctuiguang%7C2b5d08a423db4c2b9dbc7a2554fa2214%7C1694916094445; mba_muid=16948819291931216833104.6070.1694916576956; mba_sid=6070.11; pre_seq=6; pre_session=d7ad0f37360053e012116108de4ba22088d85fe4|12724; pt_key=app_openAAJlBdf4ADCj3dtB6u8iAGk244NP3PvOJb7wTgODnQGYXlQ0tZTqO17XxocX4V385MePelYG9wk; pt_pin=%E5%AE%85treasure; pwdt_id=%E5%AE%85treasure; sid=58052f1b534c6825598c9e14947bef5w; 3AB9D23F7A4B3C9B=QCXBC5RVLBCX6OXRQXJXVYHBFVSXDVW3VN2X52Y43V6XYYOBA4M3MDLQLA2LQ7RALCFZCVQW4AKXIMDTQLEYRC6LBI; 3AB9D23F7A4B3CSS=jdd03QCXBC5RVLBCX6OXRQXJXVYHBFVSXDVW3VN2X52Y43V6XYYOBA4M3MDLQLA2LQ7RALCFZCVQW4AKXIMDTQLEYRC6LBIAAAAMKUDTHPTIAAAAACNFINYSKZSSNVAX; unpl=JF8EAL5nNSttWxhQUBoLSxcTSQgHWw8LGB9WPDUDBF5cT1FSSwEYEhV7XlVdXxRKHx9vYRRUXFNKVA4ZBysiEEpcVV9UAEIfAV9nAVIzWSVUDB5sdUVFH1lcXw8OHBYAZ2IHUA1oe1cFKwMrEhdNXldXVQBIEwBnYQZUWF5OXQccMhoiEENZZF5cCU0XB29vA11aWktUNSsGHREWT1xVX144SicCXyxrVRBYTFIGGAsTGhNPXlxYXghOEQZmZQJkXGhI%7CJF8EAKxnNSttCkpXDBlVHUUYQl1QWw5fGx8KODBSVl9YHlMASwNJF0J7XlVdXxRKHh9vYxRUWVNJXA4fBysiE0peVVxfDE4TC19jBFNUWk5RBSsyGBIgSm1UWVQBQhUEbGYGUV1aT1EDGAEaERZJbVVuXgxKJwNuZgNVX1lDVQYaBhsTIHtcZF9tCXtWbW9mB1JVX0NcSBsFEhsZSVpXX14NSxUHamEGV1xbTVY1GjIb; shshshfpa=48e2f774-3a65-7fc9-9941-3bc2f2224b31-1660269809; shshshfpx=48e2f774-3a65-7fc9-9941-3bc2f2224b31-1660269809; unionwsws=%7B%22devicefinger%22%3A%22eidIfa7f81222esakrxIKCAGRhWta6B9vS0zzJK8SaYXeXQu8j7VMbR6JIc2ntsOnulQL3dXRmj4ItiM5iONnQqAa5Xz22ZS1VN8vWM5xAs1DwhZa9g3%22%7D"
# str.replace(" ","")
# if str.__contains__("pt_pin=") and str.__contains__("pt_key="):
#     pt_pin = re.findall(r"pt_pin=.*?;", str)[0]
#     pt_key = re.findall(r"pt_key=.*?;", str)[0]
#     print(pt_pin)
#     print(pt_key)
from datetime import datetime
from operator import itemgetter
from utils.QL import QLService

#
ql = QLService()

timestamp = datetime.timestamp(datetime.now())
# test = "2023-09-18-08-28-00.log?path=6dylan6_jdpro_jd_bean_change_1983&t=1695022122383"
# url = f"{self._logs_url}/{log_name}"

def get_log_name():
    t = timestamp
    path = ""
    log_name = ""
    full_logs = ql.get_logs()
    asset_log = extract_newest_asset_log_path(full_logs)
    # print(asset_log)
    asset = ql.get_logs(asset_log)
    print(asset)


def extract_newest_asset_log_path(logs):
    # 筛选出对应的log的文件夹
    log_time = 0
    new_log = dict()
    for i in logs:
        if i["title"].__contains__("jd_bean_change") and i["mtime"] > log_time:
            log_time=i["mtime"]
            new_log = i["children"]
    if new_log is not None:
        log = sorted(new_log, key=itemgetter("mtime"), reverse=True)[0]
        result = log["title"] + "?path=" + log["parent"] + "&t=" + str(timestamp)
        print(result)
    else:
        result = ""
    return result

def format_name():
     s = "%E5%AE%85treasure"
     print(urllib.parse.unquote(s))

if __name__ == '__main__':
    format_name()