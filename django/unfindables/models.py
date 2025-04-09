from django.db import models

from utils.models.base import BaseModel

# web search model
class WebSearch(BaseModel):
    query = models.CharField(max_length=255)