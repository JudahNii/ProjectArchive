from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class AuthUserManager(BaseUserManager):

	def create_user(self, username, first_name, last_name, status, password=None, **extra_fields):

		user = self.model(username=username, first_name=first_name, last_name=last_name,
                status=status, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user


	def create_superuser(self, username, first_name, last_name, password=None, status=None, **extra_fields):

		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("is_active", True)

		if extra_fields.get("is_staff") is not True:
			raise ValueError(_("Superuser must have is_staff=True."))
		if extra_fields.get("is_superuser") is not True:
			raise ValueError(_("Superuser must have is_superuser=True."))

		user = self.create_user(username=username, first_name=first_name, last_name=last_name, 
                status=status, password=password, **extra_fields)
		return user
