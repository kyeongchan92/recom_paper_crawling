from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')  # 파일을 저장할 경로 설정
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 업로드 시간 기록
