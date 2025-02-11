from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.file_upload_view, name='file_upload'),
    path("paper_parse/<int:file_id>/", views.paper_parse_file_view, name="parse_file"),
    path('source_parse/', views.source_parse, name='source_parse'),
    path('reference_parse/', views.reference_parse, name='reference_parse'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
