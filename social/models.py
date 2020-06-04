from django.db import models
from django.db.models import Q


class Swiped(models.Model):
    STATUS = (
        ('superlike', '超级喜欢'),
        ('like', '喜欢'),
        ('dislike', '不喜欢'),
    )

    uid = models.IntegerField(verbose_name='滑动者的 UID')
    sid = models.IntegerField(verbose_name='被滑动者的 UID')
    status = models.CharField(max_length=8, choices=STATUS)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'time'

    @classmethod
    def like(cls, uid, sid):
        obj = cls.objects.create(uid=uid, sid=sid, status='like')
        return obj

    @classmethod
    def superlike(cls, uid, sid):
        obj = cls.objects.create(uid=uid, sid=sid, status='superlike')
        return obj

    @classmethod
    def dislike(cls, uid, sid):
        obj = cls.objects.create(uid=uid, sid=sid, status='disklike')
        return obj

    @classmethod
    def is_liked(cls, uid, sid):
        return cls.objects.filter(uid=uid, sid=sid,
                                  status__in=['superlike', 'like']).exists()

    @classmethod
    def liked_me(cls, uid):
        return cls.objects.filter(sid=uid, status__in=['superlike', 'like'])


class Friend(models.Model):
    uid1 = models.IntegerField()
    uid2 = models.IntegerField()

    @classmethod
    def make_friends(cls, uid1, uid2):
        uid1, uid2 = sorted([uid1, uid2])
        cls.get_or_create(uid1=uid1, uid2=uid2)

    @classmethod
    def is_friends(cls, uid1, uid2):
        uid1, uid2 = sorted([uid1, uid2])
        return cls.objects.filter(uid1=uid1, uid2=uid2).exists()

    @classmethod
    def friend_id_list(cls, uid):
        '''获取好友的 uid 列表'''
        # 查询我的好友关系
        condition = Q(uid1=uid) | Q(uid2=uid)
        relations = cls.objects.filter(condition)

        # 筛选好友的 uid
        id_list = []
        for relation in relations:
            friend_id = relation.uid2 if relation.uid1 == uid else relation.uid1
            id_list.append(friend_id)

        return id_list

    @classmethod
    def break_off(cls, uid1, uid2):
        uid1, uid2 = sorted([uid1, uid2])
        cls.objects.filter(uid1=uid1, uid2=uid2).delete()