from django.db import models

from utils.mixins.base import BaseModel
from utils.mixins.triggers import triggers

@triggers('websearch_created', 'AFTER', 'INSERT')
class WebSearch(BaseModel):
    query = models.CharField(max_length=255)