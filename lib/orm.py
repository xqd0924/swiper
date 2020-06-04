
class ModelMixin:
    def to_dict(self, ignore_fields=()):
        '''将model对象转换成dict'''
        data = {}
        for field in self._meta.fields:
            name = field.attname
            if name not in ignore_fields:
                data[name] = getattr(self, name)
        return data