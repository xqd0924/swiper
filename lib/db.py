from django.db import models
from django.core.cache import cache


def get(cls, *args, **kwargs):
    '''数据优先从缓存获取，缓存取不到再从数据库获取'''
    # 创建 key
    pk = kwargs.get('pk') or kwargs.get('id')

    # 从缓存获取
    if pk is not None:
        key = 'Model:%s:%s' % (cls.__name__, pk)
        model_obj = cache.get(key)
        print('get from cache: %s' % model_obj)
        if isinstance(model_obj, cls):
            return model_obj

    # 缓存里没有，直接从数据库获取
    model_obj = cls.objects.get(*args, **kwargs)
    print('get from db: %s' % model_obj)
    # 写入缓存，并且缓存一周
    key = 'Model:%s:%s' % (cls.__name__, model_obj.pk)
    cache.set(key, model_obj, 604800)
    print('set to cache')
    return model_obj


def get_or_create(cls, *args, **kwargs):
    # 创建 key
    pk = kwargs.get('pk') or kwargs.get('id')

    # 从缓存获取
    if pk is not None:
        key = 'Model:%s:%s' % (cls.__name__, pk)
        model_obj = cache.get(key)
        if isinstance(model_obj, cls):
            return model_obj, False

    # 执行原生方法
    model_obj, created = cls.objects.get_or_create(*args, **kwargs)

    # 添加缓存，设置过期时间为一周
    key = 'Model:%s:%s' % (cls.__name__, model_obj.pk)
    cache.set(key, model_obj, 604800)

    return model_obj, created


def save_with_cache(model_save_func):
    def save(self, *args, **kwargs):
        '''存入数据库后，同时写入缓存'''
        # 调用原生的 Model.save() 将数据保存到数据库
        model_save_func(self, *args, **kwargs)

        # 添加缓存
        key = 'Model:%s:%s' % (self.__class__.__name__, self.pk)
        cache.set(key, self, 604800)
    return save


def to_dict(self, *ignore_fields):
    '''将model对象转换成dict'''
    attr_dict = {}
    for field in self._meta.fields:
        name = field.attname
        if name not in ignore_fields:
            attr_dict[name] = getattr(self, name)
    return attr_dict


def patch_model():
    '''
    动态更新 Model 方法

    Model 在 Django 中是一个特殊的类，如果通过继承的方式来增加或修改所有方法， Django 会将继承的类识别为
    一个普通的 app.model，所以只能通过 monkey patch 的方式动态修改
    '''
    # 动态添加类方法 get，get_or_create
    models.Model.get = classmethod(get)
    models.Model.get_or_create = classmethod(get_or_create)

    # 修改 save
    models.Model.save = save_with_cache(models.Model.save)

    # 添加 to_dict
    models.Model.to_dict = to_dict