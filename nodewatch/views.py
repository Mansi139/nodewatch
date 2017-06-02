import arrow

from arrow.parser import ParserError
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from nodewatch import stats
from nodewatch.models import Observation
from nodewatch.serializers import ObservationSerializer


# http://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
# Groups a set of related actions on a particular resource into a single class.
# The ModelViewSet in particular implements these actions by deriving them
# from an ORM model.
class ObservationViewSet(ModelViewSet):

    queryset = Observation.objects
    serializer_class = ObservationSerializer
    category = None
    stats_fn = None

    # Dynamically determine the queryset to return based on the class'
    # 'category' property. This is so that in order to create a view that
    # only displays a subset of the observations, you simply have to overwrite
    # 'category' in your subclasses.
    def get_queryset(self):
        # Order by *descending* ids
        return self.queryset.filter(category=self.category).order_by('-id')

    # Create a properly formatted observation
    def create(self, request):
        observation = Observation.objects.create(
            category=self.category,
            datetime=timezone.now(),
            data=self.__class__.stats_fn()
        )

        return Response({
            'id': observation.id,
            'category': observation.category,
            'datetime': observation.datetime,
            'data': observation.data
        }, status=HTTP_201_CREATED)


class LoadAvgViewSet(ObservationViewSet):
    category = 'loadavg'
    stats_fn = stats.loadavg


class CpuViewSet(ObservationViewSet):
    category = 'cpu'
    stats_fn = stats.cpustats


class MemViewSet(ObservationViewSet):
    category = 'mem'
    stats_fn = stats.meminfo


class MountsViewSet(ObservationViewSet):
    category = 'mounts'
    stats_fn = stats.mounts


class IPRouteViewSet(ObservationViewSet):
    category = 'routes'
    stats_fn = stats.ip_route


class UptimeViewSet(ObservationViewSet):
    category = 'uptime'
    stats_fn = stats.uptime


# TODO(heyzoos)
# The blocks view is special in that statistics are recorded about individual
# blocks. You need to be able to specify the block in the 'list', and 'create'
# actions.
# class BlocksViewSet(ObservationViewSet):
#     category = 'blocks'
#     stats_fn = stats.blockinfo


class DevicesViewSet(ObservationViewSet):
    category = 'devices'
    stats_fn = stats.devices


class HostnamectlViewSet(ObservationViewSet):
    category = 'hostnamectl'
    stats_fn = stats.hostnamectl


class DfViewSet(ObservationViewSet):
    category = 'df'
    stats_fn = stats.df


view_sets = [LoadAvgViewSet, CpuViewSet, MemViewSet, MountsViewSet]
view_sets += [IPRouteViewSet, UptimeViewSet, DevicesViewSet]
view_sets += [HostnamectlViewSet, DfViewSet]

# http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
# Provides functionality for automatically mapping view logic to urls. The
# default router in particular includes a generated root view with hyperlinks
# to all its registered views.
router = DefaultRouter()
for view in view_sets:
    router.register(view.category, view, base_name=view.category)


def truncate(request):
    """For datetime-based maintenance of the size of the sqlite database. When
    no datetime is provided to this view, it defauls to dropping observations
    over a week old."""

    errors = []

    datetime = arrow.utcnow().replace(weeks=-1)
    if request.GET.get('datetime'):
        try:
            datetime = arrow.get(request.GET.get('datetime'))
        except ParserError:
            errors.append({'status': 400, 'detail': 'Invalid datetime'})
            return JsonResponse(data={"errors": errors}, status=400)

    Observation.objects.filter(datetime__lt=datetime.datetime).delete()
    count = Observation.objects.count()
    return JsonResponse(data={"current_observation_count": count})
