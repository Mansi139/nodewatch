from rest_framework.serializers import ModelSerializer, JSONField

from nodewatch.models import Observation


class ObservationSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Observation

    data = JSONField()
