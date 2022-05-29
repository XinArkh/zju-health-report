#! /usr/bin/env python3


import re
import time
import json
import random
import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import message
from errors import *


class ZJUHealthReport(object):
    """浙大每日健康打卡"""

    login_url = 'https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%26from%3Dwap'
    index_url = 'https://healthreport.zju.edu.cn/ncov/wap/default/index'
    save_url = 'https://healthreport.zju.edu.cn/ncov/wap/default/save'
    key_url = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'

    def __init__(self, user, passwd, ua):
        self.user = user
        self.passwd = passwd
        self.sess = requests.session()
        self.sess.headers = {'User-Agent': ua}

        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.sess.mount('http://', adapter)
        self.sess.mount('https://', adapter)

        self.res = None
        self.payload = None

    def login(self):
        """登陆页面"""
        res = self.sess.get(self.login_url)
        time.sleep(random.random())
        execution = re.search(r'name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(url=self.key_url).json()
        time.sleep(random.random())
        e_str, m_str = res['exponent'], res['modulus']
        passwd_encrypt = self.rsa_encrypt(self.passwd, e_str, m_str)
        payload = {
            'username': self.user,
            'password': passwd_encrypt,
            'execution': execution,
            '_eventId': 'submit'
        }
        res = self.sess.post(url=self.login_url, data=payload)
        time.sleep(random.random())

        if '统一身份认证' in res.text:
            raise LoginError('登录失败，请核实账号密码重新登录')
        else:
            self.res = res

    def is_reported(self):
        """检查是否已经打卡"""
        if not self.res:
            self.res = self.sess.get(index_url)
            time.sleep(random.random())
        if "hasFlag: '1'" in self.res.text:
            return True
        return False

    def is_form_updated(self):
        """检查打卡表单是否发生变动"""
        if not self.res:
            self.res = self.sess.get(index_url)
            time.sleep(random.random())
        try:
            form_current = re.search(r'<ul>[\s\S]*?</ul>', self.res.text).group()
        except Exception:
            raise RegexMatchError('正则表达式匹配失败，请检查表单是否更新')
        with open('./sample_form.html', 'r', encoding='utf-8') as f:
            if form_current == f.read():
                return False        
        return True

    def get_payload(self):
        """获取旧的打卡记录，并作为新提交表单的信息"""
        if not self.res:
            self.res = self.sess.get(index_url)
            time.sleep(random.random())
        old_info = re.search(r'oldInfo: ({[^\n]+})', self.res.text).group(1)
        # old_info = old_info.encode('utf-8').decode('unicode_escape')  # 不可提前解码中文，否则json失效
        payload = json.loads(old_info)
        magic_codes = re.search(r'"(\w{32})": ?"(\w{10})", ?"(\w{32})": ?"(\w{32})"[\s\S]{1,50}oldInfo', self.res.text).groups()
        magic_codes_dict = {magic_codes[0]: magic_codes[1], 
                            magic_codes[2]: magic_codes[3]}
        payload.update(magic_codes_dict)
        payload['date'] = datetime.datetime.now().strftime('%Y%m%d')
        self.payload = payload

    def post(self):
        """上传打卡信息"""
        if not self.payload:
            self.get_payload()
        time.sleep(random.random())
        res = self.sess.post(self.save_url, data=self.payload)
        return json.loads(res.text)

    @staticmethod
    def rsa_encrypt(passwd_str, e_str, m_str):
        passwd_bytes = bytes(passwd_str, 'ascii')
        passwd_int = int.from_bytes(passwd_bytes, 'big')
        e_int = int(e_str, 16)
        m_int = int(m_str, 16)
        result_int = pow(passwd_int, e_int, m_int)
        return hex(result_int)[2:].rjust(128, '0')


def main(user, passwd, ua):
    msg = None
    reporter = ZJUHealthReport(user, passwd, ua)
    print('[Time] %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('打卡任务启动...')
    reporter.login()
    print('登录成功')
    if reporter.is_reported():
        msg = '今日已打卡，程序中止'
        print(msg)
        return msg
    try:
        if reporter.is_form_updated():
            msg = '表单已更新，请更新程序'
            print(msg)
            return msg
    except Exception as e:
        msg = '表单核对失败,请手动检查: ' + str(e)
        print(msg)
        return msg
    res = reporter.post()
    if res['m'].startswith('操作成功'):
        msg = '打卡成功'
        print(msg)
    elif res['m'].startswith('今天已经填报了'):
        msg = '今日已打卡，提交无效'
        print(msg)
    else:
        msg = '打卡状态异常，请手动检查: %s' % res
        print(msg)
    return msg


if __name__ == '__main__':
    from user_key import user, passwd, ua, dingtalk_access_token
    msg = main(user, passwd, ua)
    message.dingtalk_robot(msg, dingtalk_access_token)
