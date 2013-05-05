#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smtplib
from email.mime.text import MIMEText
from email.Header import Header

if os.path.isfile('./config.py'):
    from config import mail_from
    from config import mail_pass
else:
    mail_from = raw_input('请输入邮箱')
    mail_pass = raw_input('请输入密码')

mail_user, mail_host = mail_from.split('@')
mail_host = '.'.join(['smtp', mail_host])

def send_mail(sub, content, to_list=[mail_from]):

    msg = MIMEText(content, _charset='UTF-8')
    msg['Subject'] = Header(sub, charset='UTF-8')
    msg['From'] = '%s<%s>' % (mail_user, mail_from)
    msg['To'] = ";".join(to_list)
    print msg.as_string()
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user, mail_pass)
        s.sendmail(mail_from, to_list, msg.as_string())
        s.quit()
        return True
    except SMTPException, e:
        print e
    return False

if __name__ == '__main__':
    if send_mail("test subject", "This is the test content"):
        print "发送成功"
    else:
        print "发送失败"
