from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('list', views.list, name='list'),
    path('delete%empId=<int:id>', views.delete, name='delete'),
    path('detail', views.detail, name='detail'),
    path('detail%empId=<int:id>', views.update, name='update'),
]
