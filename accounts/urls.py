from django.urls import path
from .views import (
    login_view, register_view, logout_view,
    add_to_list, my_list,
    update_status, remove_anime
)

urlpatterns = [
    path("register/", register_view),
    path("login/", login_view),
    path("logout/", logout_view),
    path("add/", add_to_list),
    path("my-list/", my_list),
    path("update/", update_status),
    path("delete/", remove_anime),
]
