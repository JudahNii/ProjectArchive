import csv, datetime, xlwt, os
import pandas as pd


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.conf import settings

from .forms import ProgrammeForm, DocumentationForm
from users.models import Student, HOD
from .models import Documentation, Programme, Faculty, Department, Supervisor
from google_drive_utils import upload_file_to_drive, get_file_link, remove_file_from_drive
from weasyprint import HTML



def create_programme(request):
	if request.method == 'POST':
		form = ProgrammeForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('programme_list')
	else:
		form = ProgrammeForm()
	return render(request, 'create_programme.html', {'form': form})

def update_programme(request, programme_id):
	programme = Programme.objects.get(id=programme_id)
	if request.method == 'POST':
		form = ProgrammeForm(request.POST, instance=programme)
		if form.is_valid():
			form.save()
			return redirect('programme_list')
	else:
		form = ProgrammeForm(instance=programme)
	return render(request, 'create_programme.html', {'form': form})

def delete_programme(request, programme_id):
	Programme.objects.get(id=programme_id).delete()
	return redirect('programme_list')

def upload_documentation(request):
	
	student = Student.objects.get(user=request.user)
	if not student:
		return redirect('logout')
	
	if request.method == 'POST':
		form = DocumentationForm(request.POST, request.FILES)
		if form.is_valid():
			documentation = form.save(commit=False)
			documentation.author = student
			documentation.set_status("Uploaded")
			documentation.save()
			return redirect('home')

	form = DocumentationForm()
	form.fields['supervisor'].queryset = Supervisor.objects.filter(faculty=student.faculty)
	has_uploaded_documentation = Documentation.objects.filter(author=student).exists()
	context = {'form': form, 'has_uploaded_documentation': has_uploaded_documentation}
	return render(request, 'upload_documentation.html', context)


class HODDocumentationListView(ListView):
	model = Documentation
	template_name = "documentation_list.html"
	paginate_by = 4
	context_object_name = "documentations"
	
	def get_queryset(self):
		documentation_list = Documentation.objects.all()
		if self.request.user.is_authenticated and self.request.user.is_hod:
			hod = self.request.user.hod
			documentation_list = documentation_list.filter(faculty=hod.faculty)
		else:
			if self.request.user.is_authenticated:
				logout(self.request.user)
				return redirect('login')
    
		documentation_list = filter(self.request, documentation_list)
		global global_documentations
		global_documentations = documentation_list
		return documentation_list

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		hod = HOD.objects.get(user=self.request.user)

		context['departments'] = Department.objects.filter(faculty=hod.faculty)
		context['programmes'] = Programme.objects.filter(faculty=hod.faculty)
		context['supervisors'] = Supervisor.objects.filter(faculty=hod.faculty)
		return context

   
class ApprovedDocumentationListView(ListView):
	model = Documentation
	template_name = "approved_documentation_list.html"
	context_object_name = "documentations"
	
	def get_queryset(self):
		documentation_list = Documentation.objects.filter(status="Approved")
		documentation_list = filter(self.request, documentation_list)
		return documentation_list

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['departments'] = Department.objects.all()
		context['faculties'] = Faculty.objects.all()
		context['programmes'] = Programme.objects.all()
		context['supervisors'] = Supervisor.objects.all() 
		return context


class DocumentationDetailView(DetailView):
	model = Documentation
	template_name = "documentation_detail.html"
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		documentation = self.get_object()
		filename = documentation.pdf_file.name.split('/')[-1]

		student = None
		if self.request.user.is_authenticated:
			try:
				student = Student.objects.get(user=self.request.user)
				is_student = True
			except Student.DoesNotExist:
				pass
		
		context['student'] = student
		context['filename'] = filename
  
		has_uploaded_documentation = Documentation.objects.filter(author=student).exists()
		context['has_uploaded_documentation'] = has_uploaded_documentation
		return context
	
	def get_object(self, queryset=None):
		username = self.kwargs.get('username')
		if queryset is None:
			queryset = self.get_queryset()
		return queryset.get(author__username=username)
	

class ApprovedDocumentationDetailView(DocumentationDetailView):
	model = Documentation
	template_name = "approved_documentation_detail.html"

 
class CheckStatusDocumentationDetailView(DocumentationDetailView):
	model = Documentation
	template_name = "check_status_documentation_detail.html"


def manage_documentation(request, username, action):
	documentation = Documentation.objects.get(author__username=username)
	
	if action == 'approve':
		documentation.google_drive_id = upload_file_to_drive(
			documentation.author.username, 
			documentation.pdf_file.path,
			request
		)
		documentation.web_view_link = get_file_link(documentation.google_drive_id)
		documentation.set_status("Approved")
		documentation.comment = "Documentation Approved! Well done."
  
	elif action == 'disapprove':
		documentation.set_status("Disapproved")
		documentation.comment = request.POST['comment']
  
	elif action == 'remove':
		remove_file_from_drive(documentation.google_drive_id)
		documentation.set_status("Removed")
	documentation.save()
	
	if action == 'delete':
		if documentation.google_drive_id:
			remove_file_from_drive(documentation.google_drive_id)
		documentation.delete()
	
	return redirect('all_docs')


def pdf_view(request, filename):
	pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentations', 'pdfs', f'{filename}.pdf')

	# Check if the PDF file exists
	if os.path.exists(pdf_path):
		with open(pdf_path, 'rb') as pdf_file:
			response = HttpResponse(pdf_file.read(), content_type='application/pdf')
			response['Content-Disposition'] = f'inline; filename="{filename}"'

			# Set X-Content-Type-Options header to 'nosniff'
			response['X-Content-Type-Options'] = 'nosniff'

			return response

	# Return a 404 response if the file doesn't exist
	return HttpResponse('PDF file not found', status=404)


def is_valid_queryparam(param):
	return param != '' and param is not None

def filter(request, queryset):
	qs = queryset

	title_or_abstract_contains = request.GET.get('title_or_abstract_contains')
	title_contains = request.GET.get('title_contains')
	abstract_contains = request.GET.get('abstract_contains')
	faculty = request.GET.get('faculty')
	department = request.GET.get('department')
	programme = request.GET.get('programme')
	supervisor = request.GET.get('supervisor')
	date_min = request.GET.get('date_min')
	date_max = request.GET.get('date_max')
	uploaded = request.GET.get('uploaded')
	approved = request.GET.get('approved')
	disapproved = request.GET.get('disapproved')

	if is_valid_queryparam(title_or_abstract_contains):
		qs = qs.filter(
					Q(title__icontains=title_or_abstract_contains) | 
					Q(abstract__icontains=title_or_abstract_contains)
				).distinct()

	if is_valid_queryparam(title_contains) and is_valid_queryparam(abstract_contains):
		qs = qs.filter(
				Q(title__icontains=title_contains) | Q(abstract__icontains=abstract_contains)
			).distinct()

	elif is_valid_queryparam(title_contains):
		qs = qs.filter(title__icontains=title_contains)

	elif is_valid_queryparam(abstract_contains):
		qs = qs.filter(abstract__icontains=abstract_contains)
	
	if is_valid_queryparam(faculty) and faculty != 'Choose...':
		qs = qs.filter(faculty__name=faculty)

	if is_valid_queryparam(department) and department != 'Choose...':
		qs = qs.filter(department__name=department)

	if is_valid_queryparam(programme) and programme != 'Choose...':
		qs = qs.filter(programme__name=programme)

	if is_valid_queryparam(supervisor) and supervisor != 'Choose...':
		qs = qs.filter(supervisor__name=supervisor)

	if is_valid_queryparam(date_min):
		qs = qs.filter(publish_date__gte=date_min)

	if is_valid_queryparam(date_max):
		qs = qs.filter(publish_date__lt=date_max)

	if is_valid_queryparam(uploaded) or is_valid_queryparam(approved) or is_valid_queryparam(disapproved):
		status_filters = []
		if is_valid_queryparam(uploaded):
			status_filters.append('Uploaded')
		if is_valid_queryparam(approved):
			status_filters.append('Approved')
		if is_valid_queryparam(disapproved):
			status_filters.append('Disapproved')
		qs = qs.filter(status__in=status_filters)

	return qs



def bulk_upload_documentations(request):
	if request.method == 'POST':
		uploaded_files = request.FILES.getlist('upload_files')

		# check if one of the uploaded files is an excel file
		excel_file = None
		for file in uploaded_files:
			if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
				excel_file = file
				break

		if not excel_file:
			return render(request, 'bulk_upload_documentations.html', {'error': 'No Excel file found.'})

		df = pd.read_excel(excel_file)

		hod = HOD.objects.get(user=request.user)

		for _, row in df.iterrows():

			author_username = row['username']
			department_name = row['department']
			programme_name = row['programme']
			supervisor_name = row['supervisor']

			author = Student.objects.get(user__username=author_username)
			faculty = hod.faculty
			department = Department.objects.get(name=department_name)
			programme = Programme.objects.get(name=programme_name)
			supervisor = Supervisor.objects.get(name=supervisor_name)

			documentation = Documentation.objects.create(
				author = author,
				title = row['title'],
				abstract = row['abstract'],
				created_at = row['created_at'],
				status = 'Uploaded',
				faculty = faculty,
			)

			documentation.set_department(department)
			documentation.set_programme(programme)
			documentation.set_supervisor(supervisor)

			for pdf_file in uploaded_files:
				if pdf_file.name == f"{row['username']}.pdf":
					documentation.pdf_file = pdf_file

			documentation.save()
		return redirect('all_docs')
	else:
		return render(request, 'bulk_upload_documentations.html')


def export_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="documentations_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv"'
	writer = csv.writer(response)
	writer.writerow(['Title', 'Abstract', 'Author', 'Faculty', 'Department', 'Programme', 'Supervisor', 'Created At'])

	if global_documentations:
		for documentation in global_documentations:
			writer.writerow([documentation.title, documentation.abstract, documentation.author.user.username, 
			documentation.faculty.name, documentation.department.name, documentation.programme.name, 
			documentation.supervisor.name, documentation.created_at.strftime("%Y-%m-%d")])
	else:
		return None

	return response


def export_excel(request):
	response = HttpResponse(content_type='application/ms_excel')
	response['Content-Disposition'] = f'attachment; filename="documentations_{datetime.datetime.now().strftime("%Y-%m-%d")}.xls"'
	workbook = xlwt.Workbook(encoding='utf-8')
	worksheet = workbook.add_sheet('Documentations')
	row_num = 0
	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Title', 'Abstract', 'Author', 'Faculty', 'Department', 'Programme', 'Supervisor', 'Created At']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num], font_style)

	font_style = xlwt.XFStyle()

	if global_documentations:
		rows = global_documentations.values_list(
			'title', 'abstract', 'author__user__username', 'faculty__name', 
			'department__name', 'programme__name', 'supervisor__name', 'created_at'
		)

		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				worksheet.write(row_num, col_num, str(row[col_num]), font_style)
		workbook.save(response)
	else:
		return None

	return response


def export_pdf(request):
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="documentations_{}.pdf"'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
	response['Content-Transfer-Encoding'] = 'binary'

	if global_documentations:
		html_string = render_to_string('pdf-output.html', {'documentations': global_documentations})
		html = HTML(
			string=html_string, 
			base_url='http://localhost:8000',
		)
		result = html.write_pdf()

		response.write(result)
	else:
		return HttpResponse('No documentations available.', status=404)

	return response


def add_favorite(request, author_username):
	try:
		student = Student.objects.get(user=request.user)
		documentation = Documentation.objects.get(author__username=author_username)
		if documentation not in student.favorite_documentations.all():
			student.favorite_documentations.add(documentation)
		return redirect('approved_doc_detail', username=author_username)
		
	except Exception as e:
		print(e)
		return redirect('home')

def remove_favorite(request, author_username):
	try:
		student = Student.objects.get(user=request.user)
		documentation = Documentation.objects.get(author__username=author_username)
		if documentation in student.favorite_documentations.all():
			student.favorite_documentations.remove(documentation)
		return redirect('approved_doc_detail', username=author_username)
		
	except Exception as e:
		print(e)
		return redirect('home')