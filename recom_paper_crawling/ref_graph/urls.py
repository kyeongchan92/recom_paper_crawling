from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.file_upload_view, name='file_upload'),
    path("paper_parse/<int:file_id>/", views.peper_parse_file_view, name="parse_file"),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
