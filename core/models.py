from django.db import models
from django.utils.crypto import get_random_string
import mimetypes
import uuid

class File(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    file_name = models.CharField(blank=True,null=True,max_length=100)
    file_path = models.CharField(max_length=255, unique=True)
    file_type = models.CharField(max_length=50, blank=True, null=True) 
    file_size = models.BigIntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.file_type:
            _, self.file_type = mimetypes.guess_type(self.filepath)
        super().save(*args, **kwargs)