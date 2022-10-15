import requests
import time
import random
import sys
import re
from encrypt import AESEncrypt

import traceback
import smtplib
from email.mime.text import MIMEText
from email.header import Header

import yaml
config = yaml.safe_load(open('/home/lt/XMU-autocheck/config.yaml'))
import logging
logging.basicConfig(filename=config['log_file'],level='INFO',format='[%(asctime)s %(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class AutoChecker(object):
    def __init__(self,config):
        self.session = requests.Session()
        self.enable_email = config['enable_email']
        self.sender = config['sender']
        self.receivers = config['receivers']
        self.mail_id = config['mail_id']
        self.mail_pwd = config['mail_pwd']
        self.mail_server = config['mail_server']
        self.mail_port = config['mail_port']
        self.xmu_id = config['xmu_id']
        self.xmu_pwd = config['xmu_pwd']

    def run(self):
        try:
            self.login()
            business_id = self.get_business_id()
            data_id, formData = self.get_data(business_id)
            formData = self.change_form()
            state = self.check(data_id,formData)
            return state
        except:
            traceback.print_exc()
            logger.error(traceback.format_exc())
            print('打卡失败')
            self.send_email()
            return False

    def login(self):
        print('Login......')
        url = 'https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu'
        data = {'username': self.xmu_id,
                'password': '',
                'lt': '',
                'dllt': 'userNamePasswordLogin',
                'execution': 'e1s1',
                '_eventId': 'submit',
                'rmShown': '1'}

        ret = self.session.get(url)
        lt = re.findall(r'name="lt" value="(.*)"',ret.text)[0]
        key = re.findall(r'id="pwdDefaultEncryptSalt" value="(.*)"',ret.text)[0]
        data['password'] = AESEncrypt(self.xmu_pwd,key)
        data['lt'] = lt
        ret = self.session.post(url,data=data)


    def get_business_id(self):
        url ='https://xmuxg.xmu.edu.cn/api/app/214/business/now?getFirst=true'
        ret = self.session.get(url)
        business_id = ret.json()['data'][0]['business']['id']
        print(f'Get business id {business_id}')
        return business_id

    def get_data(self,business_id):
        url = f'https://xmuxg.xmu.edu.cn/api/formEngine/business/{business_id}/myFormInstance'
        ret = self.session.get(url)
        data = ret.json()['data']
        data_id = data['id']
        print(f'Get data id {data_id}')
        formData = data['formData']
        return data_id, formData

    def change_form(self):
        formData = [
                {"name": "select_1582538796361", "title": "今日体温 Body temperature today （℃）",
                 "value": {"stringValue": "37.3以下 Below 37.3 degree celsius"}, "hide": False},
                {"name": "select_1582538846920",
                 "title": "是否出现发热或咳嗽或胸闷或呼吸困难等症状？Do you have sypmtoms such as fever, coughing, chest tightness or breath difficulties?",
                 "value": {"stringValue": "否 No"}, "hide": False},
                {"name": "select_1582538939790",
                 "title": "Can you hereby declare that all the information provided is all true and accurate and there is no concealment, false information or omission. 本人是否承诺所填报的全部内容均属实、准确，不存在任何隐瞒和不实的情况，更无遗漏之处。",
                 "value": {"stringValue": "是 Yes"}, "hide": False},
                {"name": "input_1582538924486", "title": "备注 Notes", "value": {"stringValue": ""},
                 "hide": False},
                {"name": "datetime_1611146487222", "title": "打卡时间（无需填写，保存后会自动更新）",
                 "value": {"dateValue": time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}, "hide": False,
                 "readonly": False},
                {"name": "select_1584240106785", "title": "学生本人是否填写",
                 "value": {"stringValue": "是"}, "hide": False, "readonly": False}
            ]
        return formData

    def check(self,data_id,formData):
        url = f'https://xmuxg.xmu.edu.cn/api/formEngine/formInstance/{data_id}'
        ret = self.session.post(url,json={'formData':formData,'playerId':'owner'})
        state = ret.json()['state']
        print(state)
        if not state:
            print(ret.json())
            print('打卡失败')
        return state

    def send_email(self):
        if not self.enable_email:
            return

        mail_msg = '打卡失败，请手动打卡'
        message = MIMEText(mail_msg, 'plain', 'utf-8')
        message['From'] = Header("Server", 'utf-8')
        message['To'] =  Header("Admin", 'utf-8')
        subject = 'Server error message'
        message['Subject'] = Header(subject, 'utf-8')
        smtpObj = smtplib.SMTP_SSL(self.mail_server,self.mail_port)
        smtpObj.login(self.mail_id,self.mail_pwd)
        smtpObj.sendmail(self.sender, self.receivers, message.as_string())
        smtpObj.quit()

def main():
    debug_flag = len(sys.argv) > 1
    if not debug_flag:
        sleep_time = int(random.random()*600)
        print(f'Wait random time: {sleep_time}s')
        time.sleep(sleep_time)
    else:
        # debug mode
        config['enable_email'] = False
        print(f'Wait time: {sleep_time}s')
        time.sleep(int(sys.argv[1]))
    logger.info('Start auto check')
    auto_checker = AutoChecker(config)
    state = False
    retry = 3
    while not state and retry > 0:
        state = auto_checker.run()
        if state:
            logger.info('SUCCESS')
        else:
            logger.warning(f'FAIL, retry: {retry}')
            retry -= 1
            if not debug_flag:
                time.sleep(sleep_time)
    if not state:
        logger.warning('Send mail')
        auto_checker.send_email()


if __name__ == '__main__':
    main()
