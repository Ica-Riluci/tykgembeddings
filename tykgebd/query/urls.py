from django.urls import path

from . import views

urlpatterns = [
    path('prototype_worker/', views.prototype_worker),
    path('q0/', views.simpleQ),
    path('q1/', views.specQ1),
]
