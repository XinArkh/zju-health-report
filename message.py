import json
import requests


def dingtalk_robot(msg, access_token):
    headers = {'Content-Type': 'application/json'}
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=' + access_token
    message = '[浙大健康打卡] ' + msg
    payload = {
        'msgtype': 'text', 
        'text': {
            'content': message
        }
    }
    requests.post(webhook, data=json.dumps(payload), headers=headers)
    print('钉钉机器人发送成功:', message)


if __name__ == '__main__':
    dingtalk_robot('test', 'xxx')
