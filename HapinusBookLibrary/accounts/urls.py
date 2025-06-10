from django.urls import include, path

from . import views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),  # 인증 관련 URL 포함
    path("profile/", views.profile_view, name="profile"),
]
