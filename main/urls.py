from django.urls import path
from . import views
urlpatterns = [
    path('', views.main, name='main'),
    path('systemstock', views.systemstock, name='systemstock'),
]
