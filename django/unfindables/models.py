from django.db import models

from utils.powerups.base import BaseModel
from utils.powerups.triggers import triggers

@triggers('websearch_created', 'AFTER', 'INSERT')
class WebSearch(BaseModel):
    query = models.CharField(max_length=255)