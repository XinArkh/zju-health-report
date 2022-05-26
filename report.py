import re
import time
import random
import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
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

    def login(self):
        """登陆页面"""
        res = self.sess.get(self.login_url)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(url=self.key_url).json()
        e_str, m_str = res['exponent'], res['modulus']
        passwd_encrypt = self.rsa_encrypt(self.passwd, e_str, m_str)
        payload = {
            'username': self.user,
            'password': passwd_encrypt,
            'execution': execution,
            '_eventId': 'submit'
        }
        res = self.sess.post(url=self.login_url, data=payload)

        if '统一身份认证' in res.text:
            raise LoginError('登录失败，请核实账号密码重新登录')

        time.sleep(random.random()*2)


    @staticmethod
    def rsa_encrypt(passwd_str, e_str, m_str):
        passwd_bytes = bytes(passwd_str, 'ascii')
        passwd_int = int.from_bytes(passwd_bytes, 'big')
        e_int = int(e_str, 16)
        m_int = int(m_str, 16)
        result_int = pow(passwd_int, e_int, m_int)
        return hex(result_int)[2:].rjust(128, '0')


def main(user, passwd, ua):
    reporter = ZJUHealthReport(user, passwd, ua)
    print('[Time] %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('打卡任务启动...')
    reporter.login()
    print('成功登录！')


if __name__ == '__main__':
    user = 'xxx'
    passwd = 'xxx'
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'

    main(user, passwd, ua)
