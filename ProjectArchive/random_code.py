# def get_form(self, form_class=None):
#     form = super().get_form(form_class)
#     if self.request.method in ['POST', 'PUT']:
#         if "faculty" in self.request.POST:
#             department_id = int(self.request.POST.get('faculty'))
#             form.fields['department'].queryset = Department.objects.filter(faculty_id=department_id)
#         if "department" in self.request.POST:
#             programme_id = int(self.request.POST.get('department'))
#             form.fields['programme'].queryset = Programme.objects.filter(department_id=programme_id)
#     return form


# def approve_documentation(request, username):
#     documentation = Documentation.objects.get(author__username=username)
#     documentation.google_drive_id = upload_file_to_drive(
#             documentation.title, 
#             documentation.pdf_file.path
#         )
#     documentation.web_view_link = get_file_link(documentation.google_drive_id)
#     documentation.set_status("approved")
#     documentation.save()
#     return redirect('all_docs')
	
# def disapprove_documentation(request, username):
#     documentation = Documentation.objects.get(author__username=username)
#     documentation.set_status("disapproved")
#     return redirect('all_docs')

# def remove_documentation(request, username):
#     documentation = Documentation.objects.get(author__username=username)
#     remove_file_from_drive(documentation.google_drive_id)
#     documentation.set_status("removed")
#     documentation
#     return redirect("approved_docs")
	
# def delete_documentation(request, username):
#     documentation = Documentation.objects.get(author__username=username)
#     remove_file_from_drive(documentation.google_drive_id)
#     documentation.delete()
#     return redirect('all_docs')


	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)

	# 	Department = apps.get_model('documentations', 'Department')
	# 	Programme = apps.get_model('documentations', 'Programme')

	# 	self.fields['department'].queryset = Department.objects.none()
	# 	self.fields['programme'].queryset = Programme.objects.none()

	# 	if "faculty" in self.data:
	# 		try:
	# 			department_id = int(self.data.get('faculty'))
	# 			self.fields['department'].queryset = Department.objects.filter(faculty_id=department_id)
	# 		except:
	# 			pass
		
	# 	if "department" in self.data:
	# 		try:
	# 			programme_id = int(self.data.get('department'))
	# 			self.fields['programme'].queryset = Programme.objects.filter(department_id=programme_id)
	# 		except:
	# 			pass
 
 
 # class ApprovedDocumentationDetailView(DetailView):
# 	model = Documentation
# 	template_name = "approved_documentation_detail.html"
	
# 	def get_context_data(self, **kwargs):
# 		context = super().get_context_data(**kwargs)
# 		documentation = self.get_object()
# 		filename = documentation.pdf_file.name.split('/')[-1]

# 		student = None
# 		if self.request.user.is_authenticated:
# 			try:
# 				student = Student.objects.get(user=self.request.user)
# 				is_student = True
# 			except Student.DoesNotExist:
# 				pass
		
# 		context['student'] = student
# 		context['filename'] = filename
# 		return context

# 	def get_object(self, queryset=None):
# 		username = self.kwargs.get('username')
# 		if queryset is None:
# 			queryset = self.get_queryset()
# 		return queryset.get(author__username=username)


# def hod_landing_page(request):
#     if request.user.is_authenticated and request.user.is_hod:
#         title_or_abstract_contains = request.GET.get('title_or_abstract_contains')
#         if title_or_abstract_contains is None or title_or_abstract_contains.strip() == "":
#             hod = HOD.objects.get(user=request.user)
#             context = {}
#             latest_documentations = Documentation.objects.filter(status='uploaded', faculty=hod.faculty).order_by('-created_at')[:3]
#             context['latest_documentations'] = latest_documentations
#             return render(request, 'hodhome.html', context)
#         return HttpResponseRedirect(reverse_lazy('all_docs') + '?title_or_abstract_contains=' + title_or_abstract_contains)
#     else:
#         if request.user.is_authenticated:
#             logout(request.user)
#         return redirect('login')