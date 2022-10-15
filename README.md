# XMU-autocheck
厦门大学疫情自动打卡

## Python环境
`pip3 install pycryptodome`

## 配置文件
修改`config_template.yaml`另存为`config.yaml`
```yaml
enable_email: True # 开启邮件通知功能
sender: xxx@xx.com # 发信邮箱，需开启smtp功能
receivers: xxx@xx.com # 收信邮箱
mail_id: # 发信邮箱账号
mail_pwd: # 发信邮箱密码
mail_server: smtp.xx.com # 发信邮箱smtp服务地址
mail_port: 465 # 发信邮箱smtp服务端口
xmu_id: # 厦门大学统一登录账号
xmu_pwd: # 厦门大学统一登录密码
log_file: auto_check.log # 日志保存文件
```

## 手动运行
`python3 auto_check.py` 随机延迟0-10分钟运行  
`python3 auto_check.py $S` 等待$S秒运行

## 定时运行
`crontab -e`设置定时任务  
`0 10 * * * /usr/bin/python3 /<your_path>/auto_check.py` 每天十点定时运行
