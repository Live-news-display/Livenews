from django.shortcuts import render

# Create your views here.
from django.views import View

from tools.login_decorator import login_check


class FavView(View):
    @login_check
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def merge_favs(self, uid, fav_info):
        pass
