from urllib import request
import pandas as pd

from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.utils import timezone
from django.db.models import Q

from .forms import StudentForm, InitStudentUpdateForm, StudentUpdateForm, UsersExcelUploadForm
from .models import Student, HOD, AuthUser
from documentations.models import Department, Programme, Faculty, Documentation, Supervisor
from .decorators import (
    deny_user, is_authenticated, is_not_student, is_not_hod
)


def landing_page(request):
    faculties = Faculty.objects.all()
    context = {'faculties': faculties}
    return render(request, 'landing_page.html', context)


def search_bar(request):
    title_or_abstract_contains = request.GET.get('title_or_abstract_contains')
    print("title or abstract contains:", title_or_abstract_contains)
    user = request.user
  
    if title_or_abstract_contains is None or title_or_abstract_contains.strip() == "":
        return redirect('home')
    
    if user.is_authenticated and user.is_hod:
        return HttpResponseRedirect(reverse_lazy('all_docs') + '?title_or_abstract_contains=' + title_or_abstract_contains)
    
    return HttpResponseRedirect(reverse_lazy('approved_docs') + '?title_or_abstract_contains=' + title_or_abstract_contains)
    


def homeview(request):
    if request.user.is_authenticated:
        context = {}
        try:
            student = Student.objects.get(user=request.user)
            context['student'] = student

            try:
                favorite_documentations = student.favorite_documentations.all()
                context['favorite_documentations'] = favorite_documentations

                has_uploaded_documentation = Documentation.objects.filter(author=student).exists()
                context['has_uploaded_documentation'] = has_uploaded_documentation
            except:
                pass

            return render(request, 'studenthome.html', context)
        except Student.DoesNotExist:
            try:
                hod = HOD.objects.get(user=request.user)
                context['hod'] = hod

                try:
                    faculty_documentations = Documentation.objects.filter(faculty=hod.faculty)

                    uploaded_faculty_documentations = faculty_documentations.filter(status='Uploaded')
                    latest_faculty_documentations = uploaded_faculty_documentations.order_by('-created_at')[:3]
                    context['latest_faculty_documentations'] = latest_faculty_documentations

                    context['total_faculty_documentations'] = faculty_documentations.count()

                    total_students = Student.objects.filter(faculty=hod.faculty).count()
                    print(Student.objects.filter(faculty=hod.faculty))
                    context['total_students'] = total_students

                    approved_faculty_documentations = faculty_documentations.filter(status='Approved')
                    if faculty_documentations.count() > 0:
                        percentage_approved = int((approved_faculty_documentations.count() / faculty_documentations.count()) * 100)
                    else:
                        percentage_approved = 0
                    context['percentage_approved'] = percentage_approved

                    latest_documentation = faculty_documentations.latest('created_at')
                    hours_since_creation = (timezone.now() - latest_documentation.created_at).seconds // 3600
                    hours_since_creation = "<1" if hours_since_creation < 1 else hours_since_creation
                    context['hours_since_creation'] = hours_since_creation
                except:
                    pass

                return render(request, 'hodhome.html', context)
                
            except HOD.DoesNotExist:
                logout(request.user)
                return redirect('login')

    return redirect('landing_page')


@deny_user(is_authenticated)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                if request.user.is_superuser or request.user.is_staff:
                    return redirect('admin:index')

                if user.is_student and (user.status == "Created" or user.status is None):
                    return redirect('init_update_student', username=user.username)
                    # return redirect('home')
                    
                else:
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logoutview(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('login'))


class StudentListView(ListView):
    model = Student
    template_name = 'student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_authenticated and current_user.is_hod:
            hod = HOD.objects.get(user=current_user)
            students = Student.objects.filter(faculty=hod.faculty)
        else:
            logout(self.request)
            return redirect('home')
        students = filter_students(self.request, students)
        global global_students
        global_students = students
        return students


class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'create_student.html'

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        username = cleaned_data.get('username')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        department=cleaned_data.get('department')
        programme=cleaned_data.get('programme')
        session=cleaned_data.get('session')
        gender=cleaned_data.get('gender')
        status = "Created"
        password = 'regent123'

        auth_user = AuthUser.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            status=status,
            password=password,
            is_student=True,
            is_hod=False
        )
        auth_user.save()
        
        hod = HOD.objects.get(user=self.request.user)

        student = Student.objects.create(user=auth_user)
        student.faculty = hod.faculty
        student.department = department
        student.programme = programme
        student.session = session
        student.gender = gender
        student.save()
        
        return redirect('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['excel_form'] = UsersExcelUploadForm()
        context['create_form'] = self.get_form()
        return context


class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = 'update_student.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def get_object(self, queryset=None):
        """
        Use <str:username> kwarg from url to identify Student object to be updated.
        """
        username = self.kwargs.get('username')
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(user__username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.object.user.username
        student = Student.objects.get(user=self.object.user)
        has_uploaded_documentation = Documentation.objects.filter(author=student).exists()
        context['has_uploaded_documentation'] = has_uploaded_documentation        
        return context

    def get_success_url(self):
        return reverse_lazy('update_student', kwargs={'username': self.object.user.username})


class InitStudentUpdateView(UpdateView):
    model = Student
    form_class = InitStudentUpdateForm
    template_name = 'Init_update_student.html'

    def form_valid(self, form):
        form.save()
        return redirect('login')
        
    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(user__username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.object.user.username
        student = Student.objects.get(user=self.object.user)
        has_uploaded_documentation = Documentation.objects.filter(author=student).exists()
        context['has_uploaded_documentation'] = has_uploaded_documentation
        return context

    def get_success_url(self):
        return redirect('login')


# def load_departments(request):
#     faculty_name = request.GET.get('faculty_name')
#     departments = Department.objects.filter(faculty__name=faculty_name).all()
#     return render(request, "department_options.html", {'departments': departments})

# def load_programmes(request):
#     department_name = request.GET.get('department_name')
#     programmes = Programme.objects.filter(department__name=department_name).all()
#     return render(request, "programme_options.html", {'programmes': programmes})

# def load_supervisors(request):
#     faculty_name = request.GET.get('faculty_name')
#     supervisors = Supervisor.objects.filter(faculty__name=faculty_name).all()
#     return render(request, "supervisor_options.html", {'supervisors': supervisors})


def load_objects(request, model_name, lookup_field, lookup_value, template_name):
    objects = globals()[model_name].objects.filter(**{str(lookup_field): str(request.GET.get(lookup_value))}).all()    
    return render(request, template_name, {f'{model_name.lower()}s': objects})

def load_departments(request):
    return load_objects(request, 'Department', 'faculty__name', 'faculty_name' ,'department_options.html')

def load_programmes(request):
    return load_objects(request, 'Programme', 'department__name', 'department_name', 'programme_options.html')

def load_supervisors(request):
    return load_objects(request, 'Supervisor', 'faculty__name', 'faculty_name', 'supervisor_options.html')


@deny_user(is_not_hod)
def upload_excel(request):
    if request.method == 'POST':
        hod = HOD.objects.get(user=request.user)
        excel_form = UsersExcelUploadForm(request.POST, request.FILES)
        if excel_form.is_valid():
            excel_file = request.FILES['excel_file']

            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():

                auth_user = AuthUser.objects.create_user(
                    username=row['username'],
                    password='regent123',
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    status="Created",
                    is_student=True,
                    is_hod=False,
                )

                student = Student(user=auth_user)
                student.faculty = hod.faculty
                student.save()

            return redirect('student_list')
    else:
        excel_form = UsersExcelUploadForm()
    return redirect('create_student')


def filter_students(request, queryset):
    queryset = queryset
    search_query = request.GET.get('search_query')
    if search_query:
        queryset = queryset.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(gender__icontains=search_query) |
            Q(user__status__icontains=search_query) |
            Q(programme__name__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    return queryset


