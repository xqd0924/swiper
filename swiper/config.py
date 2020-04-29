'''
第三方配置
'''


# 互亿无线短信配置
HY_SMS_URL = 'https://106.ihuyi.com/webservice/sms.php?method=Submit'
HY_SMS_PARAMS = {
    'account': 'C60228981',
    'password': '49e7de477fdef6957f8b0bcf1113e71c',
    'content': '您的验证码是：%s。请不要把验证码泄露给其他人。',
    'mobile': None,
    'format': 'json'
}


# 七牛云配置
QN_ACCESSKEY = 'i60FtrMs_5p-Ymi5RL5vuDAx-JWdghU6zsRRD-YF'
QN_SECRETKEY = '7rtfVRKJkZ6XbnG3XK5s3Xe2IgYSHAON5T-MsQja'
QN_BUCKET_NAME = 'xuqidong'
QN_BASE_URL = 'http://q9i2yanet.bkt.clouddn.com'