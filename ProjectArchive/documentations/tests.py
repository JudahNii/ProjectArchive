from django.test import TestCase
from myapp.models import ProjectDocument


class DocumentationTestCase(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            user=User.objects.create_user(username='testuser', password='password'),
            faculty=Faculty.objects.create(name='Test Faculty'),
            department=Department.objects.create(name='Test Department'),
            programme=Programme.objects.create(name='Test Programme')
        )
        self.documentation = Documentation.objects.create(
            author=self.student,
            title='Test Project',
            abstract='This is a test project document.',
            file='test_file.pdf'
        )

    def documentation_creation(self):
        self.assertTrue(isinstance(self.documentation, Documentation))
        self.assertEqual(self.documentation.title, 'Test Project')
        self.assertEqual(self.documentation.abstract, 'This is a test project document.')
        self.assertEqual(self.documentation.file.name, 'test_file.pdf')

    def documentation_author(self):
        self.assertEqual(self.documentation.author, self.student)

    def documentation_faculty(self):
        self.assertEqual(self.documentation.faculty, self.student.faculty)

    def documentation_department(self):
        self.assertEqual(self.documentation.department, self.student.department)

    def documentation_programme(self):
        self.assertEqual(self.documentation.programme, self.student.programme)

    def documentation_
