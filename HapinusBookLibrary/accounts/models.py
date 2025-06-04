import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    사용자 모델을 위한 커스텀 매니저.
    이메일을 기본 사용자 식별자로 사용합니다.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        이메일과 비밀번호로 새로운 사용자 생성.
        """
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        슈퍼유저 생성.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("membership_level", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("슈퍼유저는 is_staff=True이어야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("슈퍼유저는 is_superuser=True이어야 합니다.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    사용자 모델. 이메일을 기본 식별자로 사용하며, 회원 등급과 프로필 정보를 포함합니다.
    """

    username = None  # username 필드 제거
    email = models.EmailField(unique=True, verbose_name=_("email address"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class MembershipLevel(models.TextChoices):
        """
        회원 등급을 정의하는 클래스.
        각 등급은 텍스트 선택 옵션으로 정의됩니다.
        """

        BASIC = "BASIC", _("Basic")
        STANDARD = "STANDARD", _("Standard")
        PLUS = "PLUS", _("Plus")
        STAFF = "STAFF", _("Staff")
        ADMIN = "ADMIN", _("Admin")

    membership_level = models.CharField(
        max_length=20,
        choices=MembershipLevel.choices,
        default=MembershipLevel.BASIC,
        verbose_name=_("membership level"),
    )

    objects = UserManager()

    def __str__(self):
        """
        사용자 객체의 문자열 표현.
        이메일을 반환합니다.
        """
        return self.email

    @property
    def is_staff_level(self):
        """
        사용자가 STAFF 등급인지 확인합니다.
        - STAFF 등급이면 True, 아니면 False를 반환합니다.
        """
        return self.membership_level == User.MembershipLevel.STAFF


class UserProfile(models.Model):
    """
    사용자 프로필 모델. User와 1:1 관계를 가지며, 추가적인 프로필 정보를 저장합니다.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
    )
    memeber_id = models.UUIDField(
        _("member ID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique member ID for the user"),
    )
    address = models.TextField(_("address"), blank=True, null=True)
    phone_number = models.CharField(
        _("phone number"), max_length=20, blank=True, null=True
    )
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    memo = models.TextField(_("memo"), blank=True, null=True)

    membership_start_date = models.DateField(
        _("membership start date"), blank=True, null=True
    )
    membership_end_date = models.DateField(
        _("membership end date"), blank=True, null=True
    )

    def __str__(self):
        """
        사용자 프로필의 문자열 표현.
        - 사용자 이메일과 멤버 ID를 포함합니다.
        """
        return f"{self.user.email}'s Profile (Member ID: {self.member_id})"  # pylint: disable=no-member

    @property
    def is_membership_active(self):
        """
        회원의 멤버십이 활성 상태인지 확인합니다.
        - 시작일과 만료일이 모두 설정되어 있고, 현재 날짜가 그 범위 내에 있는 경우 활성으로 간주합니다.
        - 시작일만 설정되어 있고 만료일이 없으면 항상 활성으로 간주합니다.
        - 둘 다 설정되어 있지 않거나 시작일이 미래인 경우 비활성으로 간주합니다.
        """
        if self.membership_start_date and self.membership_end_date:
            today = timezone.now().date()
            return self.membership_start_date <= today <= self.membership_end_date
        elif (
            self.membership_start_date
        ):  # 시작일만 있고 만료일이 없으면 항상 유효한 것으로 간주
            return self.membership_start_date <= timezone.now().date()
        return False  # 둘 다 없거나 시작일이 미래면 비활성


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    사용자 모델이 저장될 때마다 UserProfile을 생성하거나 업데이트합니다.
    - 새 사용자가 생성되면 UserProfile을 생성합니다.
    - 기존 사용자의 경우 UserProfile을 업데이트합니다.
    """
    if created:
        UserProfile.objects.create(user=instance)  # pylint: disable=no-member
    else:
        instance.profile.save()
