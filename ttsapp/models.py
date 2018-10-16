from django.db import models
from django.contrib.auth.models import User


class Userkeys(models.Model):
    """
        author: fossbalaji@gmail.com,
        purpose: store user's API key for API level access
    """
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=40, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)


class Uploads(models.Model):
    """
        author: fossbalaji@gmail.com
        purpose: store user's uploaded file path, name info
    """
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_path = models.URLField(null=False, blank=False)
    output_file = models.URLField(null=True, blank=True)
    reason = models.TextField(null=True)
    is_processed = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_email_sent = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)

