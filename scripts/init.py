#!/usr/bin/env python

import os
import sys
import random

import django

# 设置环境
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "swiper.settings")
django.setup()


from user.models import User

last_names = (
    '赵钱孙李周吴郑王朱姚曹徐何聂严文'
    '郭刘费项黄廖柳金武邹邓瞿张庄颜谢'
    '宴江袁杨田汪梁蔡雷彭叶詹孙唐陈冯'
)

first_names = {
    '男': [
        '致远', '俊驰', '烨磊', '天佑',
        '文昊', '旭尧', '荣轩', '浩宇',
        '升荣', '圣杰', '晓明', '云龙',
    ],
    '女': [
        '丽娜', '佳琪', '梦洁', '美佳',
        '冰冰', '晗雪', '欢欢', '静静',
        '小雨', '诗诗', '燕婷', '引娣',
    ]
}

def random_name():
    last_name = random.choice(last_names)
    sex = random.choice(list(first_names.keys()))
    first_name = random.choice(first_names[sex])
    return ''.join([last_name, first_name]), sex


# 创建初始用户
for i in range(100):
    name, sex = random_name()
    try:
        User.objects.create(
            phonenum='%s' % random.randrange(13000000000, 13900000000),
            nickname=name,
            sex=sex,
            birth_year=random.randint(1990, 2006),
            birth_month=random.randint(1, 12),
            birth_day=random.randint(1, 28),
            location=random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都', '合肥'])
        )
        print('created:%s %s' % (name, sex))
    except django.db.utils.IntegrityError:
        pass