from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings

from .managers import AuthUserManager
from documentations.models import Department, Programme, Faculty, Documentation


class AuthUser(AbstractBaseUser, PermissionsMixin):

	STATUS_CHOICES = (
		('Created', 'Created'),
		('Activated', 'Activated'),
	)

	username = models.CharField(max_length=100, primary_key=True, unique=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_student = models.BooleanField(default=False)
	is_hod = models.BooleanField(default=False)

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS	 = ['first_name', 'last_name']

	objects = AuthUserManager()

	class Meta:
		verbose_name_plural = "Registered Users"

	def __str__(self):
		return self.first_name + " " + self.last_name

	def get_username(self):
		return self.username
 
	def get_first_name(self):
		return self.first_name
	
	def get_last_name(self):
		return self.last_name
 
 
class Student(models.Model):
	
	SESSION_CHOICES = (
		('Morning', 'Morning'),
		('Evening', 'Evening'),
		('Weekend', 'Weekend'),
	)

	GENDER_CHOICES = {
		('Male', 'Male'),
		('Female', 'Female'),
	}

	user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, primary_key=True, null=False)
	username = models.CharField(max_length=100, unique=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
	faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
	department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
	programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, blank=True)
	session = models.CharField(max_length=20, choices=SESSION_CHOICES, null=True, blank=True)
	favorite_documentations = models.ManyToManyField(Documentation, related_name='favorites', blank=True)
 
	def __str__(self):
		return self.first_name + " " + self.last_name

	def get_faculty(self):
		return self.faculty

	def get_department(self):
		return self.department

	def get_programme(self):
		return self.programme

	def save(self, **kwargs):    
		if self.user:
			self.username = self.user.get_username()
			self.first_name = self.user.get_first_name()
			self.last_name = self.user.get_last_name()
			self.user.is_student = True
			super().save(**kwargs)



class HOD(models.Model):
	user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, primary_key=True)
	username = models.CharField(max_length=100, unique=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True, null=True)
	department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
 
	class Meta:
		verbose_name_plural = "HODs"

	def __str__(self):
		return self.first_name + " " + self.last_name

	def get_faculty(self):
		return self.faculty

	def get_department(self):
		return self.department

	def save(self, **kwargs):    
		if self.user:
			self.username = self.user.get_username()
			self.first_name = self.user.get_first_name()
			self.last_name = self.user.get_last_name()
			self.user.is_hod = True
		super().save(**kwargs)



