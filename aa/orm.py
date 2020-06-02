
class ModelMixin:
    def to_dict(self):
        '''将model对象转换成dict'''
        data = {}
        for field in self._meta.fields:
            name = field.attname
            value = getattr(self, name)
            data[name] = value
        return data