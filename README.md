# zju-health-report

浙大每日健康打卡自动化小程序。

## 概览

- `errors`: 构造的一些简单错误提示类
- `message.py`: 钉钉机器人，发送每日打卡结果
- `report.py`: 主程序，构造并提交每日打卡表单
- `sample.html`: 打卡表单的源代码，用于程序对比表单是否有更新
- `user_key.py`: 用户自定义数据，包括账号、密码和钉钉机器人 token

## 环境要求

- Python 3.x
  - requests 库

## 部署

1. 将仓库克隆至你的服务器环境
2. 手动填写`user_key.py`中的对应内容，其中钉钉机器人 token 的获取方式很简单，可自行查阅，不再赘述
3. 为`report.py`添加执行权限，在 Linux 环境中如下：

```bash
chmod +x /PATH/TO/zju-health-report/report.py
```

4. 在你的服务器环境设置定时任务，每日自动执行`report.py`脚本，例如，在 Linux 环境下可使用 crontab 工具：

```bash
crontab -e  # 进入编辑界面

# 每天的0分钟、0时执行命令（我的系统中使用UTC时区，相比中国慢8小时）
0 0 * * * /PATH/TO/zju-health-report/report.py >> /PATH/TO/report.log

# 退出编辑界面

crontab -l  # 检查定时任务
service cron restart  # 重启 cron 服务
```

## 说明

未部署 GitHub Actions 服务，一是本人已有现成的校内服务器，省去进一步折腾的麻烦；二是 [GitHub Actions 属于境外 ip](https://github.com/yep96/ZJU_healthreport#zju_healthreport)，需要承担额外的未知风险。当然，如果你手头没有可用的校内/境内服务器，也可以自行尝试搭建基于本仓库代码的 GitHub Actions 服务，本仓库不承担任何责任。另外，GitHub 上其实已有另一个[匿名组织](https://github.com/zju-health-report)提供了该服务，可酌情参考。

## 参考

- [Long0x0/ZJU_nCov](https://github.com/Long0x0/ZJU-nCov-Hitcarder-Sample) (原仓库链接已失效，[此处提供一个备份](https://github.com/XinArkh/ZJU_nCov))
- [yep96/ZJU_healthreport](https://github.com/yep96/ZJU_healthreport)

在此一并感谢。

