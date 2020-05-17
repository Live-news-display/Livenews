from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.users),
    url(r'^/activation$', views.active_view)
]
