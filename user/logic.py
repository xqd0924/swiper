import random
import os
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.cache import cache

from swiper import config
from worker import call_by_worker
from lib.qncloud import async_upload_to_qiniu


def gen_verify_code(length=6):
    '''产生一个验证码'''
    return random.randrange(10 ** (length - 1), 10 ** length)


@call_by_worker
def send_verify_code(phonenum):
    '''异步发送验证码'''
    vcode = gen_verify_code()
    key = 'VerifyCode-%s' % phonenum
    cache.set(key, vcode, 120)
    sms_cfg = config.HY_SMS_PARAMS.copy()
    sms_cfg['content'] = sms_cfg['content'] % vcode
    sms_cfg['mobile'] = phonenum
    response = requests.post(config.HY_SMS_URL, data=sms_cfg)
    return response


def check_vcode(phonenum, vcode):
    '''检查验证码是否正确'''
    key = 'VerifyCode-%s' % phonenum
    saved_vcode = cache.get(key)
    print(type(saved_vcode))
    return saved_vcode == int(vcode)


def save_upload_file(user, upload_file):
    '''保存上传文件，并上传到七牛云'''
    ext_name = os.path.splitext(upload_file.name)[-1]
    filename = 'Avatar-%s%s' % (user.id, ext_name)
    filepath = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, filename)

    with open(filepath, 'wb') as newfile:
        for chunk in upload_file.chunks():
            newfile.write(chunk)

    async_upload_to_qiniu(filepath, filename)

    url = urljoin(config.QN_BASE_URL, filename)
    user.avatar = url
    user.save()