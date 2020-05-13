from lib.http import render_json

from social import logic
from social.models import Swiped


def get_users(request):
    '''获取推荐列表'''
    page = int(request.GET.get('page', 1))
    per_page = 5

    start = (page - 1) * per_page
    end = start + per_page
    users = logic.rcmd_users(request.user)[start:end]
    result = [u.to_dict() for u in users]
    return render_json(result)


def like(request):
    '''喜欢'''
    sid = int(request.POST.get('sid'))
    is_matched = logic.like_someone(request.user, sid)
    return render_json({'is_matched': is_matched})


def superlike(request):
    '''超级喜欢'''
    sid = int(request.POST.get('sid'))
    is_matched = logic.superlike_someone(request.user, sid)
    return render_json(None)


def dislike(request):
    '''不喜欢'''
    user = request.user
    sid = int(request.POST.get('sid'))
    Swiped.dislike(user.id, sid)
    return render_json(None)


def rewind(request):
    '''反悔'''
    logic.rewind(request.user)
    return render_json(None)


def show_liked_me(request):
    '''查看喜欢过我的人'''
    users = logic.users_liked_me(request.user)
    result = [u.to_dict() for u in users]
    return render_json(result)