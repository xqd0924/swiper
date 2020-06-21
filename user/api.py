from django.core.cache import cache

from user.logic import send_verify_code, check_vcode, save_upload_file
from lib.http import render_json
from user.models import User
from common import error
from user.forms import ProfileForm
from social.logic import pre_rcmd


def get_verify_code(request):
    '''手机注册'''
    phonenum = request.GET.get('phonenum')
    send_verify_code(phonenum)
    return render_json(None)


def login(request):
    '''短信验证登录'''
    phonenum = request.POST.get('phonenum')
    vcode = request.POST.get('vcode')
    if check_vcode(phonenum, vcode):
        # 获取用户
        user, created = User.get_or_create(phonenum=phonenum)
        # 记录登录状态
        request.session['uid'] = user.id
        pre_rcmd(user)
        return render_json(user.to_dict())
    else:
        raise error.VcodeError


def user_back(request):
    pre_rcmd(request.user)
    return render_json(None)


def get_profile(request):
    '''获取个人资料'''
    user = request.user
    key = f'Profile-{user.id}'
    result = cache.get(key)
    if result is None:
        result = user.profile.to_dict()
        cache.set(key, result)
    return render_json(result)


def modify_profile(request):
    '''修改个人资料'''
    form = ProfileForm(request.POST)
    if form.is_valid():
        user = request.user
        user.profile.__dict__.update(form.cleaned_data)
        user.profile.save()
        result = user.profile.to_dict()

        # 添加缓存
        cache.set(f'Profile-{user.id}', result)
        return render_json(result)
    else:
        print(form.errors)
        raise error.ProfileError


def upload_avatar(request):
    '''头像上传'''
    file = request.FILES.get('avatar')
    if file:
        save_upload_file(request.user, file)
        return render_json(None)
    else:
        return render_json(None, error.FILE_NOT_FOUND)