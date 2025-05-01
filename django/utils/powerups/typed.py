from typing import Generic, TypeVar, cast

from rest_framework.serializers import ModelSerializer
from utils.typing import Jsonable

from django.db import models

TData = TypeVar('TData', bound=Jsonable)

class Typed(models.Model, Generic[TData]):

    class Meta:
        abstract = True

    @classmethod
    def get_serializer_class(cls):
        
        class Serializer(ModelSerializer):

            class Meta(ModelSerializer.Meta):
                model = cls
                fields = '__all__'

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for field in self.Meta.model._meta.fields:
                    field_name = field.name
                    if field.null:
                        self.fields[field_name].allow_null = True
                    if field.blank:
                        self.fields[field_name].allow_blank = True
                        self.fields[field_name].required = False

        return Serializer

    @property
    def Serializer(self):
        return self.get_serializer_class()
    
    @property
    def serializer(self):
        return self.Serializer(instance=self)

    @property
    def data(self) -> TData:
        return cast(TData, self.serializer.data)
    
    @data.setter
    def data(self, value: TData):
        serializer = self.Serializer(instance=self, data=value)
        serializer.is_valid(raise_exception=True)
        serializer.save()
