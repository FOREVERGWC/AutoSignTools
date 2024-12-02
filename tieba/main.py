import hashlib
import re
import time

import requests
import yaml

from utils.user_agent_util import get_user_agent


def load_bduss(filename='../config/config.yml') -> str:
    """
    从配置文件加载bduss
    :param filename: 配置文件名称
    :return: bduss字符串
    """
    with open(filename, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['tieba']['BDUSS']


def load_cookies(filename='../config/config.yml') -> dict:
    """
    从配置文件加载cookie
    :param filename: 配置文件名称
    :return: cookie对象
    """
    with open(filename, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    cookie_str = config['tieba']['cookie']
    cookies = {}
    if cookie_str:
        cookie_pairs = cookie_str.split(';')
        for pair in cookie_pairs:
            if '=' in pair:
                name, value = pair.strip().split('=', 1)
                cookies[name] = value
    return cookies


def get_like_tieba_list(bduss) -> list:
    """
    获取关注贴吧列表
    :param bduss: BDUSS字符串
    :return: 关注贴吧列表
    """
    url = 'http://c.tieba.baidu.com/c/f/forum/like'
    data = {
        'BDUSS': bduss,
        '_client_type': '2',
        '_client_id': 'wappc_1534235498291_488',
        '_client_version': '9.7.8.0',
        '_phone_imei': '000000000000000',
        'from': '1008621y',
        'page_no': '1',
        'page_size': '200',
        'model': 'MI+5',
        'net_type': '1',
        'timestamp': str(int(time.time())),
        'vcode_tag': '11',
    }
    data = encode_data(data)
    cookies = load_cookies()
    headers = {
        'User-Agent': get_user_agent()
    }

    response = requests.post(url, data=data, cookies=cookies, headers=headers)
    return response.json()['forum_list']['non-gconforum']


def encode_data(data) -> dict:
    """
    数据加密
    :param data: 数据
    :return: 结果
    """
    s = ''
    keys = data.keys()
    for i in sorted(keys):
        s += i + '=' + str(data[i])
    sign = hashlib.md5((s + 'tiebaclient!!!').encode("utf-8")).hexdigest().upper()
    data.update({"sign": str(sign)})
    return data


def get_tbs(kw) -> str:
    """
    获取贴吧tbs
    :param kw: 吧名
    :return: tbs字符串
    """
    url = f"https://tieba.baidu.com/f?kw={kw}&fr=index&fp=0&ie=utf-8"
    headers = {
        'User-Agent': get_user_agent()
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    html = response.text
    match = re.search(r"var PageData = \{\s+'tbs':\s+\"(\w+)\"\s+};", html)
    if match:
        return match.group(1)
    return None


def sign_in(tieba_list=None) -> None:
    """
    贴吧签到
    :param tieba_list: 关注贴吧列表
    """
    if tieba_list is None:
        tieba_list = []
    for ba in tieba_list:
        tbs = get_tbs(ba['name'])
        item = {
            'ie': 'utf-8',
            'kw': ba['name'],
            'tbs': tbs,
        }
        url = 'https://tieba.baidu.com/sign/add'
        cookies = load_cookies()
        headers = {
            'User-Agent': get_user_agent()
        }

        response = requests.post(url, data=item, cookies=cookies, headers=headers)

        if response.status_code == 200:
            print(f"【{item['kw']}吧】签到成功！{response.json()}")
        else:
            print(f"【{item['kw']}吧】签到失败！{response.json()['error']}")


if __name__ == '__main__':
    bduss = load_bduss()
    like_tieba_list = get_like_tieba_list(bduss)
    sign_in(like_tieba_list)
