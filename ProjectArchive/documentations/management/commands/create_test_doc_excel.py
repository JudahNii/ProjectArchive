from django.core.management.base import BaseCommand
import pandas as pd
from documentations.models import Documentation, Faculty, Department, Programme, Supervisor
from users.models import Student
import random
import lorem
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create an excel file with data for testing documentation bulk upload form'

    def handle(self, *args, **kwargs):
        data = {
            'title': [],
            'abstract': [],
            'pdf_file': [],
            'author': [],
            'faculty': [],
            'department': [],
            'programme': [],
            'supervisor': [],
            'created_at': [],
        }

        students = list(Student.objects.all())
        faculties = list(Faculty.objects.all())
        departments = list(Department.objects.all())
        programmes = list(Programme.objects.all())
        supervisors = list(Supervisor.objects.all())

        for stu in students:
            data['title'].append('Test Documentation' + str(students.index(stu)))
            data['abstract'].append(lorem.text())
            data['pdf_file'].append('Test Documentation' + str(students.index(stu)))
            author = random.choice(students)
            data['author'].append(author.user.username)
            students.remove(author)
            faculty = random.choice(faculties)
            data['faculty'].append(faculty.name)
            department = random.choice([dept for dept in departments if dept.faculty == faculty])
            data['department'].append(department.name)
            programme = random.choice([prog for prog in programmes if prog.department == department])
            data['programme'].append(programme.name)
            supervisor = random.choice([sup for sup in supervisors if sup.faculty == faculty])
            data['supervisor'].append(supervisor.name)
            data['created_at'].append(datetime.now() - timedelta(
                    days=random.randint(0, 8000), 
                    hours=random.randint(0, 24), 
                    minutes=random.randint(0, 60), 
                    seconds=random.randint(0, 60))
                )
        df = pd.DataFrame(data)
        df.to_excel('test_data.xlsx', index=False)
        print('Test data excel file created successfully')
