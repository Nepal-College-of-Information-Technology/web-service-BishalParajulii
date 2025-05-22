from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView




urlpatterns = [
    path("index/" , views.users_list , name='index'),
    path("home/", views.chatPage, name="chat-page"),
    path("", LoginView.as_view(template_name="app/LoginPage.htm"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(), name="logout-user"),
    path("chat/<int:user_id>/", views.private_chat_view, name="private-chat"),
    path("api/users/" , views.user_list , name="user-list"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)