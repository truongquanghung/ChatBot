from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('get', views.Get.as_view(), name='get'),
    path('build', views.Build.as_view(), name='build'),
    path('reload', views.Reload.as_view(), name='reload'),
]
