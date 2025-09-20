# Create your tests here.
import hashlib
import random
from functools import reduce

from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.utils import timezone


def test_file_packet_messages(self, messages):
    for msg in messages:
        digest = hashlib.sha256(msg).hexdigest()
        response = self.client.post(f"/private/ffs/file-packet/{digest}", content_type="text/plain", data=msg)
        self.assertEqual(response.status_code, 200)

    for msg in messages:
        digest = hashlib.sha256(msg).hexdigest()
        response = self.client.get(f"/private/ffs/file-packet/{digest}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reduce(lambda a, b: a + b, response.streaming_content), msg)


class FilePacketTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='Test', password="guenthner.xyz")
        cls.user.user_permissions.add(Permission.objects.get(codename="ffs"))

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)
        self.short_message_length = 100
        self.long_message_length = 1000 * 1000
        self.super_long_message_length = 1000 * 1000
        self.short_messages = [random.randbytes(self.short_message_length) for _ in range(100)]
        self.long_messages = [random.randbytes(self.long_message_length) for _ in range(10)]
        self.super_long_messages = [random.randbytes(self.super_long_message_length) for _ in range(2)]

    def test_timezones(self):
        self.assertTrue(timezone.is_aware(timezone.now()))
        self.assertFalse(timezone.is_naive(timezone.now()))

    def test_auth(self):
        response = self.client.get("/private/ffs/files/")
        self.assertEqual(response.status_code, 200)

    def test_short_msg(self):
        test_file_packet_messages(self, self.short_messages)

    def test_long_msg(self):
        test_file_packet_messages(self, self.long_messages)

    def test_super_long_msg(self):
        test_file_packet_messages(self, self.super_long_messages)
