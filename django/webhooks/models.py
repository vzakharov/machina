from django.db import models

class WebhookTarget(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    version = models.IntegerField(default=1)