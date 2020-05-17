import hashlib
import json
import time

import jwt
from django.conf import settings
from django.http import JsonResponse


# Create your views here.
from favorites.views import FavView
from user.models import UserProfile


def tokens(request):
    if request.method != 'POST':
        return JsonResponse({'code': 10200, 'error': 'Please use POST instead.'})

    json_str = request.body
    data = json.loads(json_str)
    username = data['username']
    password = data['password']

    old_users = UserProfile.objects.filter(username=username)
    if not old_users:
        return JsonResponse({'code': 10201, 'error': 'Username or password is wrong.'})

    user = old_users[0]
    m = hashlib.md5()
    m.update(password.encode())
    if user.password != m.hexdigest():
        return JsonResponse({'code': 10202, 'error': 'Username or password is wrong.'})

    token = make_token(username)

    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}, 'fav_count': 0}

    carts_data = data.get('carts')
    carts_obj = FavView()
    carts_len = carts_obj.merge_favs(user.id, carts_data)
    result['fav_count'] = carts_len
    return JsonResponse(result)


def make_token(username, exp=3600 * 24):
    now = time.time()
    payload = {'username': username, 'exp': now + exp}
    return jwt.encode(payload, settings.JWT_TOKEN_KEY, algorithm='HS256')
