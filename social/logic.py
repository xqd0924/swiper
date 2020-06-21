import datetime

from user.models import User
from social.models import Swiped, Friend
from lib.cache import rds


def rcmd_users(user):
    dating_sex = user.profile.dating_sex
    location = user.profile.location
    min_dating_age = user.profile.min_dating_age
    max_dating_age = user.profile.max_dating_age

    curr_year = datetime.date.today().year
    min_year = curr_year - max_dating_age
    max_year = curr_year - min_dating_age
    users = User.objects.filter(sex=dating_sex,
                                location=location,
                                birth_year__gte=min_year,
                                birth_year__lte=max_year)
    return users


def like_someone(user, sid):
    Swiped.like(user.id, sid)
    if Swiped.is_liked(sid, user.id):  # 检查对方是否喜欢过自己
        Friend.make_friends(user.id, sid)
        return True
    else:
        return False


def superlike_someone(user, sid):
    Swiped.superlike(user.id, sid)
    if Swiped.is_liked(sid, user.id):  # 检查对方是否喜欢过自己
        Friend.make_friends(user.id, sid)
        return True
    else:
        return False


def rewind(user):
    '''反悔'''
    # 取出最后一次滑动记录
    swiped = Swiped.objects.filter(uid=user.id).latest()

    # 删除好友关系
    if swiped.status in ['superlike', 'like']:
        Friend.break_off(user.id, swiped.sid)

    # 删除滑动记录
    swiped.delete()


def users_liked_me(user):
    swipes = Swiped.liked_me(user.id)
    swiper_uid_list = [s.uid for s in swipes]
    return User.objects.filter(id__in=swiper_uid_list)


def add_swipe_score(uid, flag):
    '''添加被滑动的积分记录'''
    score = {'like': 5, 'superlike': 7, 'dislike': -5}[flag]
    rds.zincrby('HotSwiped', score, uid)


def get_top_n_swiped(num=10):
    '''获取 top N 的滑动数据'''
    # 取出并清洗榜单数据
    origin_data = rds.zrevrange('HotSwiped', 0, num - 1, withscores=True)
    cleaned = [[int(uid), int(swiped)] for uid, swiped in origin_data]

    # 取出用户数据
    uid_list = [uid for uid, _ in cleaned]
    users = User.objects.filter(id__in=uid_list)

    # 将 users 按照 uid_list 的顺序进行排序
    users = sorted(users, key=lambda user: uid_list.index(user.id))

    # 整理最终结果
    for item, user in zip(cleaned, users):
        item[0] = user

    return cleaned
