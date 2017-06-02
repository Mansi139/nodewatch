import json

from datetime import timedelta
from django.utils import timezone
from django.test import TestCase

from nodewatch.models import Observation


class TestViews(TestCase):

    def test_index_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_truncate_returns_200(self):
        response = self.client.get('/truncate')
        self.assertEqual(response.status_code, 200)

    def test_truncate_drops_rows_older_than_datetime(self):
        seed(14)
        datetime_filter = timezone.now() - timedelta(days=10)
        response = self.client.get('/truncate?datetime=%s' % datetime_filter)
        remaining_observations_count = len(Observation.objects.all())
        self.assertEqual(remaining_observations_count, 10)

    def test_truncate_drops_rows_older_than_a_week_by_default(self):
        seed(14)
        response = self.client.get('/truncate')
        remaining_observations_count = len(Observation.objects.all())
        self.assertEqual(remaining_observations_count, 7)

    def test_truncate_reports_how_many_rows_remain(self):
        seed(14)
        datetime_filter = timezone.now() - timedelta(days=4)
        response = self.client.get('/truncate?datetime=%s' % datetime_filter)
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content.get('current_observation_count'), 4)

    def test_truncate_handles_bad_datetimes(self):
        seed(14)
        response = self.client.get('/truncate?datetime=%s' % 'why')
        content = json.loads(response.content.decode('utf-8'))
        self.assertTrue(content['errors'][0]['detail'])


def seed(n):
    """Seed the database with n observations, where each row is one day older
    than the last."""

    for i in range(0, n):
        dt = timezone.now() - timedelta(days=i)
        Observation.objects.create(datetime=dt)
