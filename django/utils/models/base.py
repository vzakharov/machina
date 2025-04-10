# Base model: uuid as primary key, created_at, updated_at, owner (nullable)

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True
