from django.db.models import Model
from django.db.models import CharField, DateTimeField
from jsonfield import JSONField


class Observation(Model):
    category = CharField(max_length=255)
    datetime = DateTimeField()

    # https://github.com/dmkoch/django-jsonfield
    # Provides a field that will save python dictionaries as 'json'. The field
    # actually silently deserializes the 'json' as a python dictionary from a
    # text field when accessed. 
    data = JSONField()
