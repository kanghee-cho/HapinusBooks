"""
URL configuration for HapinusBookLibrary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        "", TemplateView.as_view(template_name="template.html"), name="home"
    ),  # template.html을 기본 페이지로 설정
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # 사용자 관련 URL 포함
    path("books/", include("books.urls")),  # 책 관련 URL 포함
]
