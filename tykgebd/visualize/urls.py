from django.urls import path

from . import views

urlpatterns = [
    path('mewc/', views.mew, name='mew'),
    path('simpleQ/', views.simple_query, name='simple_query'),
    path('specQ1/', views.special_query1, name='special_query1'),
]
