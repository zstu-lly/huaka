from queue import Queue
import os
import requests
import re
from threading import Thread
import logging
import json

logging.basicConfig(level=logging.INFO,
                    filemode='a',  # 'w' or 'a'
                    filename='numbers.txt',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(message)s')
logger = logging.getLogger(__name__)


def ascending(num):
    if num[-1] == num[-3] == num[-5] == num[-7]:
        if int(num[-2]) - int(num[-4]) == int(num[-4]) - int(num[-6]) == int(num[-6]) - int(num[-8]):
            return True
        else:
            return False

    elif num[-2] == num[-4] == num[-6] == num[-8]:
        if int(num[-1]) - int(num[-3]) == int(num[-3]) - int(num[-5]) == int(num[-5]) - int(num[-7]):
            return True
        else:
            return False
    else:
        return False


def classify_num(num):
    type_of_card = 'nothing'

    if re.search(
            "(?:0(?=1)|1(?=2)|2(?=3)|3(?=4)|4(?=5)|5(?=6)|6(?=7)|7(?=8)|8(?=9)){3,}\\d",
            num[-4:]):
        type_of_card = '顺子'
    elif re.search(
            "(?:0(?=1)|1(?=2)|2(?=3)|3(?=4)|4(?=5)|5(?=6)|6(?=7)|7(?=8)|8(?=9)){3,}\\d",
            num[:-4]):
        type_of_card = '中间顺子'
    elif re.search(
            '(?:9(?=8)|8(?=7)|7(?=6)|6(?=5)|5(?=4)|4(?=3)|3(?=2)|2(?=1)|1(?=0)){4,}\\d',
            num[-5:]):
        type_of_card = '倒顺'
    elif re.search('^\\d*(\\d)\\1\\1(\\d)\\2\\2\\d*$', num[-6:]):  # aaabbb
        type_of_card = 'aaabbb'
    elif re.search('(\\d)\\1(\\d)\\2(\\d)\\3', num[-6:]):  # aabbcc
        type_of_card = 'aabbcc'
    elif re.search('([\\d])\\1{2}', num[-3:]):
        type_of_card = '豹子'
    elif re.search('([\\d])\\1{4}', num):
        if '44444' in num:
            type_of_card = "5个4"
        else:
            type_of_card = '5A'
    elif re.search('([\\d])\\1{3}', num[-5:]):
        type_of_card = '尾4A'
    elif re.search('([\\d])\\1{3}', num):
        type_of_card = '中间4A'
    elif num[-8: -4] == num[-4:]:
        type_of_card = '真山'
    elif num[-6: -4] == num[-4:-2] == num[-2:]:
        type_of_card = 'ababab'

    elif re.search('000[1|8]', num[-4:]):  # 0001 或0008
        type_of_card = '0001 或0008'
    elif re.search('(\\d)\\1\\1(8)', num[-4:]):  # XXX8
        type_of_card = 'XXX8'
    # elif re.search('(\\d)(\\d)(\\d)\\1\\2\\3', num[-6:]):  # abcabc
    #     type_of_card = 'abcabc'
    elif re.search('(\\d)(\\d)\\1\\2\\1\\2\\1\\2', num[-8:]):  # abababab
        type_of_card = 'abababab'
    elif re.search('(\\d)(\\d)\\1\\2(\\d)(\\d)\\3\\4', num[-8:]):  # ababcdcd
        type_of_card = 'ababcdcd'
    elif re.search('^\\d*(\\d)\\1\\1.(\\d)\\2\\2\\d*$', num[-8:]):  # aaabcccd
        type_of_card = 'aaabcccd'
    elif re.search('(\\d)(\\d)\\2\\1(\\d)(\\d)\\4\\3', num[-8:]):  # abbacddc
        type_of_card = 'abbacddc'
    elif re.search('1688', num[-4:]):  # '1688'
        type_of_card = '1688'
    elif re.search('10086', num[-5:]):  # '10086'
        type_of_card = '10086'
    elif re.search('1314', num[-4:]):  # '1314'
        type_of_card = '1314'
    elif re.search('^\\d*(\\d)\\1\\1.(\\d)\\2(\\d)\\3.*$', num[-8:]):  # aaabccdd
        type_of_card = 'aaabccdd'
    elif len(set(num)) == 3:
        type_of_card = '3数字组合'
    elif re.search('(\\d)\\1(88)', num[-4:]):
        type_of_card = 'AA88'
    elif set(num) == {'1', '3', '4', '9'}:
        type_of_card = '1349风水号'
    elif ascending(num):
        type_of_card = '*a*a*a*a'
    elif re.search('(\\d)\\1(\\d)\\2(\\d)\\3(\\d)\\4', num[-8:]):
        type_of_card = '四对'
    elif num[-6:] == '678910':
        type_of_card = '678910'
    elif num[-5:] == '67890':
        type_of_card = '67890'

    return type_of_card


def get_all_province_info():
    if not os.path.exists('城市.txt'):
        url = "https://rwk.cmicrwx.cn/rwx/rwkweb/rwkCommon/getAllProvInfoTotal"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
            'Referer': "https://rwk.cmicrwx.cn/rwx/rwkvue/young/",
            "Content-Type": "application/json",
            "Host": "rwk.cmicrwx.cn",
        }
        payload_data = {"MsgType": "GetProvCityInfoReq", "Version": "1.0.0", "cardProductId": ""}

        response = requests.post(url, headers=headers, data=json.dumps(payload_data))
        response_dict = json.loads(response.text)

        file = open('城市.txt', 'w')
        for province in response_dict['allProvinceInfo']:
            province_id = province['provinceId']  # 省份的id
            province_name = province['provinceName']  # 直辖市名称或者省名
            for city in province['cityList']:
                # task_q.put({'city': city['cityName'], 'cityCode': city['cityId'], 'provCode': province_id,
                #             'province': province_name})
                # print(city['cityName'], city['cityId'], province_id, province_name)
                file.write(' '.join([city['cityName'], city['cityId'], province_id, province_name]) + '\n')
        file.close()

    task_q = Queue()
    task_list = list()
    with open('城市.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            try:
                city, cityCode, provCode, province = line.strip('\n').split(' ')
                # print(city, cityCode, provCode, province)
                task_list.append([city, cityCode, provCode, province])
            except Exception as e:
                print(e)

        # 先扫省会或者直辖市, 弟弟城市往后稍稍
        task_list = sorted(task_list, key=lambda x: abs(int(x[1])-int(x[2])))
        for task in task_list:
            print(task)
            city, cityCode, provCode, province = task
            task_q.put({'city': city, 'cityCode': cityCode, 'provCode': provCode, 'province': province})
    return task_q


def crawl_numbers():

    while not task_queue.empty():
        payload_data = task_queue.get()
        task_queue.put(payload_data)
        payload_data['MsgType'] = "LiveHKSelectNumberReq"
        payload_data['Version'] = "1.0.0"
        payload_data['count'] = 25
        payload_data['searchkey'] = ""
        payload_data['selecttype'] = 0
        # print(payload_data)
        url = "https://rwk.cmicrwx.cn/rwx/rwkweb/livehk/livehkMobile/selectNumber"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
            'Referer': "https://rwk.cmicrwx.cn/rwx/rwkvue/young/",
            "Content-Type": "application/json",
            "Host": "rwk.cmicrwx.cn",
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload_data))
            numbers = json.loads(response.text)["numbers"]
            for number in numbers:
                rule = classify_num(number)
                if rule != "nothing":
                    # 去重
                    if number in phone_num_set:
                        continue
                    phone_num_set.add(number)

                    print(number, rule, payload_data)
                    logger.info(' '.join([number, rule, str(payload_data)]))
                # else:
                #     logger.debug(' '.join([number, rule, str(payload_data)]))
        except Exception as e:
            pass


# 选号链接：https://rwk.cmicrwx.cn/rwx/rwkvue/young/#/infomation
phone_num_set = set()
task_queue = get_all_province_info()


if __name__ == '__main__':

    ths = []
    for i in range(100):
        th = Thread(target=crawl_numbers)
        th.start()
        ths.append(th)

    for th in ths:
        th.join()

