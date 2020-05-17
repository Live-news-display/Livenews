import base64
import hashlib
import json
import random

from django.core.cache import cache
from django.http import JsonResponse

from dtoken.views import make_token
from user.models import UserProfile
from .tasks import send_active_email_async


def users(request):
    if request.method != 'POST':
        return JsonResponse({'code': 10100, 'error': 'Please use POST !'})

    json_str = request.body
    data = json.loads(json_str)
    username = data['uname']
    email = data['email']
    password = data['password']
    phone = data['phone']
    old_users = UserProfile.objects.filter(username=username)
    if old_users:
        result = {'code': 10101, 'error': 'Your username is already existed!'}
        return JsonResponse(result)

    m = hashlib.md5()
    m.update(password.encode())

    try:
        UserProfile.objects.create(username=username, password=m.hexdigest(), email=email, phone=phone)
    except Exception as e:
        print('---create error is ---')
        print(e)
        return JsonResponse({'code': 10102, 'error': 'Your username is already existed~~'})

    token = make_token(username)

    send_activation_email(username, email)

    return JsonResponse({'code': 200, 'username': username, 'data': {'token': token.decode()}, 'carts_count': 0})


def send_activation_email(username, email):
    try:
        code = "%s" % (random.randint(1000, 9999))
        code_str = code + '_' + username
        active_code = base64.urlsafe_b64encode(code_str.encode())
        cache.set('email_active_%s' % username, code, 60 * 60 * 24 * 3)
        verify_url = 'http://127.0.0.1:7000/dadashop/templates/active.html?code=%s' % (active_code.decode())
        print(verify_url)
        send_active_email_async.delay(email, verify_url)
    except Exception as e:
        print('---active error---')
        print(e)


def active_view(request):
    if request.method != 'GET':
        return JsonResponse({'code': 10103, 'error': 'Please use GET'})

    code = request.GET.get('code')
    if not code:
        return JsonResponse({'code': 10104, 'error': 'no code'})

    verify_code = base64.urlsafe_b64decode(code.encode()).decode()
    random_code, username = verify_code.split('_')
    old_code = cache.get('email_active_%s' % username)
    if not old_code:
        return JsonResponse({'code': 10105, 'error': 'The link is invalid'})
    if old_code != random_code:
        return JsonResponse({'code': 10106, 'error': 'The link is invalid!!'})

    user = UserProfile.objects.get(username=username)
    user.is_active = True
    user.save()

    cache.delete('email_active_%s' % username)
    return JsonResponse({'code': 200, 'data': 'ok'})
