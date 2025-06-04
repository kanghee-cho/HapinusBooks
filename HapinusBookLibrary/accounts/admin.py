from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """
    UserProfile 모델을 User 모델의 인라인으로 표시하기 위한 클래스.
    User 모델의 상세 페이지에서 프로필 정보를 함께 관리할 수 있도록 합니다.
    """

    model = UserProfile
    can_delete = False  # 사용자와 프로필은 함께 관리되므로 보통 삭제 옵션 비활성화
    verbose_name_plural = _("Profile Details")
    fk_name = "user"  # UserProfile 모델의 user 필드를 지정

    # UserProfile에 정의된 필드들을 어드민 인라인 폼에 표시
    # member_id는 editable=False이므로 readonly_fields에 포함하거나 fields에서 제외
    fields = (
        "member_id",
        "address",
        "phone_number",
        "date_of_birth",
        "memo",
        "membership_start_date",
        "membership_end_date",
    )
    readonly_fields = ("member_id",)  # member_id는 자동 생성되므로 읽기 전용


@admin.register(User)  # admin.site.register(User, UserAdmin) 대신 데코레이터 사용
class UserAdmin(BaseUserAdmin):
    """
    사용자 정의 User 모델을 관리하기 위한 어드민 클래스.
    Django의 기본 UserAdmin을 상속받아 커스터마이징합니다.
    커스텀 User 모델을 사용하기 위해 AUTH_USER_MODEL 설정이 필요합니다.
    """

    # form = CustomUserChangeForm  # 커스텀 User 변경 폼을 사용한다면
    # add_form = CustomUserCreationForm # 커스텀 User 생성 폼을 사용한다면
    inlines = (UserProfileInline,)  # UserProfile 인라인 추가

    # User 목록에 보여줄 필드
    list_display = (
        "email",
        "get_member_id",
        "get_full_uuid",
        "first_name",
        "last_name",
        "membership_level",
        "is_staff_level",
        "is_active",
        "get_membership_status",
    )
    list_select_related = ("profile",)  # UserProfile 정보 N+1 쿼리 방지

    # User 목록에서 필터링할 수 있는 필드
    list_filter = ("is_staff", "is_superuser", "is_active", "membership_level")

    # User 상세 페이지에서 필드 순서 및 그룹화 (UserProfile 필드는 인라인에서 관리)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info (from User model)"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions & Level (from User model)"),
            {
                "fields": (
                    "membership_level",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates (from User model)"),
            {"fields": ("last_login", "date_joined")},
        ),
    )
    # User 모델 자체의 읽기 전용 필드 (UserProfile 필드는 UserProfileInline에서 설정)
    readonly_fields = ("last_login", "date_joined")
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "profile__member_id",
        "profile__phone_number",
    )
    ordering = ("email",)

    # UserProfile의 member_id를 User 목록에 표시하기 위한 메서드
    def get_member_id(self, instance):
        """
        UserProfile의 member_id를 반환합니다.
        """
        try:
            return instance.profile.member_id
        except UserProfile.DoesNotExist:  # pylint: disable=no-member
            return _("N/A")

    get_member_id.short_description = _("Member ID")

    def get_full_uuid(self, instance):
        """
        UserProfile의 full_uuid를 반환합니다.
        """
        try:
            return instance.profile.full_uuid
        except UserProfile.DoesNotExist:  # pylint: disable=no-member
            return _("N/A")

    get_full_uuid.short_description = _("Full UUID")

    # 멤버십 활성 상태를 User 목록에 표시하기 위한 메서드
    def get_membership_status(self, instance):
        """
        UserProfile의 멤버십 상태를 반환합니다.
        - 활성화: 현재 날짜가 시작일과 종료일 사이에 있는 경우
        - 만료: 종료일이 현재 날짜 이전인 경우
        - 비활성화: 시작일이 없거나 종료일이 미래인 경우
        """
        try:
            if instance.profile.is_membership_active:
                return _("Active")
            elif (
                instance.profile.membership_end_date
                and instance.profile.membership_end_date < timezone.now().date()
            ):
                return _("Expired")
            return _("Inactive")
        except UserProfile.DoesNotExist:  # pylint: disable=no-member
            return _("N/A")

    get_membership_status.short_description = _("Membership Status")

    # username 필드를 User 모델에서 제거했으므로, 기본 UserAdmin의 add_fieldsets를 수정해야 함
    # User 생성 폼에 필요한 필드들 (커스텀 폼을 사용하지 않을 경우)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password",
                    "password2",
                    "first_name",
                    "last_name",
                    "membership_level",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )
