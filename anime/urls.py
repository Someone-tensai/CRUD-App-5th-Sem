from django.urls import path
from .views import anime_list, anime_detail

urlpatterns = [
    path('anime/', anime_list),
    path('anime/<int:anime_id>/', anime_detail),
]
