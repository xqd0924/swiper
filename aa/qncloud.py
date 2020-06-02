from qiniu import Auth
from qiniu import put_file

from swiper import config
from worker import call_by_worker


qn = Auth(config.QN_ACCESSKEY, config.QN_SECRETKEY)

def upload_to_qiniu(localfile, key):
    '''
    将本地文件上传到七牛

    Args:
        key: 上传后保存的文件名
        localfile: 要上传文件的本地路径
    '''
    # 要上传的空间
    bucket_name = config.QN_BUCKET_NAME
    # 生成上传 Token，可以指定过期时间等
    token = qn.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, localfile)
    print(info)
    return ret, info


async_upload_to_qiniu = call_by_worker(upload_to_qiniu)
