from django import forms
from django.forms import Select


from .models import Student, HOD
from documentations.models import Faculty, Department, Programme


class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		fields = ['username', 'first_name', 'last_name', 'department', 'programme', 'session', 'gender']
  
		labels = {
			'username': 'Student ID',
		}
		

class CustomSelectWidget(Select):
	def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
		# Call the original method to get the default option
		option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
		# Modify the 'value' to use the 'name' attribute of the Department model
		option['value'] = str(label)
		return option


class StudentUpdateForm(forms.ModelForm):
	department = forms.ModelChoiceField(queryset=Department.objects.none(), widget=CustomSelectWidget())
	
	class Meta:
		model = Student
		fields = ['department', 'programme', 'session', 'gender']
  
	def __init__(self, *args, **kwargs):
			super(StudentUpdateForm, self).__init__(*args, **kwargs)
			if self.instance and self.instance.pk:
				student = Student.objects.get(pk=self.instance.pk)
				self.fields['department'].queryset = Department.objects.filter(faculty=student.faculty)
				self.fields['programme'].queryset = Programme.objects.filter(department=student.department)

	def save(self, commit=True):
		student = super().save(commit=False)
		if commit:
			student.save()
		return student


class InitStudentUpdateForm(StudentUpdateForm):
	new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')

	class Meta:
		model = Student
		fields = ['department', 'programme', 'session', 'gender', 'new_password']
 
	def save(self, commit=True):
		student = super().save(commit=False)

		if self.cleaned_data.get('new_password'):
			user = student.user
			user.status = "Activated"
			user.set_password(self.cleaned_data['new_password'])
			user.save()

		if commit:
			student.save()
		return student


class UsersExcelUploadForm(forms.Form):
	excel_file = forms.FileField()
