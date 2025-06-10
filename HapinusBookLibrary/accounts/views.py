from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile_view(request):
    """
    사용자 프로필 페이지 뷰
    로그인한 사용자만 접근 가능
    """
    return render(request, "registration/profile.html", {"user": request.user})


# Create your views here.
