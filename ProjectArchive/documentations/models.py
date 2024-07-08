from html.entities import name2codepoint
from secrets import choice
from django.db import models
from django.core.validators import FileExtensionValidator
  

class Faculty(models.Model):
 
    DEPARTMENT_CHOICES = (
        ('FECAS', 'Faculty of Engineering, Computing and Allied Sciences'),
        ('SBLL', 'School of Business, Leadership, and Legal Studies'),
        ('FAS', 'Faculty of Arts and Sciences'),
    )
    name = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Faculties"
    
    
class Department(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True)
    
    def __str__(self):
        return self.name
    

class Programme(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True)
    
    def __str__(self):
        return self.name
    
class Supervisor(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.name


class Documentation(models.Model):
    
    STATE_CHOICES = (
		('Uploaded', 'Uploaded'),
		('Approved', 'Approved'),
		('Disapproved', 'Disapproved'),
		('Removed', 'Removed'),
	)
    
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True)
    author = models.OneToOneField('users.Student', on_delete=models.CASCADE, related_name='students', primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATE_CHOICES, null=True, blank=True)
    pdf_file = models.FileField(upload_to='documentations/pdfs/', validators=[FileExtensionValidator(['pdf'])],
                                null=True, blank=True)
    google_drive_id = models.CharField(max_length=255, null=True, blank=True)
    web_view_link = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(blank=True)
    


    def __str__(self):
        return self.title
           
    def set_status(self, status):
        if status not in dict(self.STATE_CHOICES):
            raise ValueError(f"Invalid status: {status}. Must be one of {dict(self.STATE_CHOICES)}")
        self.status = status

    def set_faculty(self, faculty):
        self.faculty = faculty

    def set_department(self, department):
        self.department = department

    def set_programme(self, programme):
        self.programme = programme
    
    def set_supervisor(self, supervisor):
        self.supervisor = supervisor
    
    def save(self, **kwargs):
        # if self.faculty is empty or None
        if self.author:
            if not self.faculty:
                self.faculty = self.author.faculty
            if not self.department:
                self.department = self.author.department
            if not self.programme:
                self.programme = self.author.programme
        super().save(**kwargs)
