import datetime

from user.models import User
from social.models import Swiped, Friend
from lib.cache import rds
from worker import call_by_worker


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


@call_by_worker
def pre_rcmd(user):
    '''
    推荐预处理

    1. 加载我滑动过的人，到缓存，并添加过期时间
    2. 执行推荐算法，得到一批用户
    3. 再将取到的用户与缓存中被划过的数据进行去重处理
    4. celery 将推荐结果添加到缓存
    '''
    # 将滑动记录添加到 Redis 的 set
    swiped = Swiped.objects.filter(uid=user.id).only('sid')
    swiped_sid_list = {s.sid for s in swiped}
    rds.sadd('Swiped-%s' % user.id, *swiped_sid_list)

    # 取出待推荐的用户 ID
    rcmd_user_id_list = {u.id for u in rcmd_users(user).only('id')}

    # 去重
    rcmd_user_id_list = rcmd_user_id_list - swiped_sid_list
    rds.sadd('RCMD-%s' % user.id, *rcmd_user_id_list)


def get_rcmd_user_from_redis(user):
    rcmd_uid_list = [int(uid) for uid in rds.srandmember('RCMD-%s' % user.id, 10)]
    return User.objects.filter(id__in=rcmd_uid_list)


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
