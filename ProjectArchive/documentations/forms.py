from django import forms

from .models import Documentation, Programme, Supervisor
from users.models import Student


class DocumentationForm(forms.ModelForm):
    class Meta:
        model = Documentation
        fields = ['title', 'abstract', 'pdf_file', 'supervisor']
        labels = {
            'pdf_file': 'PDF File Upload',
        }
        help_texts = {
            'pdf_file': '• Upload PDFs only.',
        }


class ProgrammeForm(forms.ModelForm):
	class Meta:
		model = Programme
		fields = ['name']

	


