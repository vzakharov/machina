from django.db import models

from utils.django import SimpleFloatField, DynamicField

class Eloable(models.Model):

    class Meta:
        abstract = True

    DEFAULT_ELO = 1000.0
    K_FACTOR = 32.0

    elo = DynamicField(
        SimpleFloatField, lambda: Eloable,
        lambda Field, Model: Field(default=Model.DEFAULT_ELO)
    )

class TestModel(Eloable):

    DEFAULT_ELO = 1200.0