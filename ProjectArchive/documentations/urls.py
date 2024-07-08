from django.urls import path

from .views import (
        create_programme, upload_documentation,
        HODDocumentationListView, ApprovedDocumentationListView, CheckStatusDocumentationDetailView,
        DocumentationDetailView, ApprovedDocumentationDetailView,
        manage_documentation, bulk_upload_documentations,
        export_csv, export_pdf, export_excel, 
        add_favorite, remove_favorite,
    )

urlpatterns = [
    path('', ApprovedDocumentationListView.as_view(), name='approved_docs'),
    path('all/', HODDocumentationListView.as_view(), name='all_docs'),
    path('detail/<str:username>/', DocumentationDetailView.as_view(), name='doc_detail'),
    path('approved_detail/<str:username>/', ApprovedDocumentationDetailView.as_view(), name='approved_doc_detail'),
    path('check_status/<str:username>/', CheckStatusDocumentationDetailView.as_view(), name='check_status_detail'),

    path('create_prog/', create_programme, name='create_programme'),
    path('upload_doc/', upload_documentation, name='upload_doc'),

    path('manage_documentation/<str:username>/<str:action>/', manage_documentation, name='manage_documentation'),
    
    path('bulk_upload/', bulk_upload_documentations, name='bulk_upload_documentations'),

    path('export_csv/', export_csv, name='export_csv'),
    path('export_pdf/', export_pdf, name='export_pdf'),
    path('export_excel/', export_excel, name='export_excel'),

    path('add_favorite/<str:author_username>/', add_favorite, name='add_favorite'),
    path('remove_favorite/<str:author_username>/', remove_favorite, name='remove_favorite'),

]

