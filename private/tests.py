# Create your tests here.
import hashlib
import os
import random
from functools import reduce
from pathlib import Path
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.utils import timezone

from guenthner_xyz import settings
from private.models import FilePacket


def test_file_packet_messages(self, messages):
    for msg in messages:
        digest = hashlib.sha256(msg).hexdigest()
        response = self.client.post(f"/private/ffs/file-packet/{digest}", content_type="text/plain", data=msg)
        self.assertSuccessful(response)

    for msg in messages:
        digest = hashlib.sha256(msg).hexdigest()
        response = self.client.head(f"/private/ffs/file-packet/{digest}", content_type="text/plain")
        self.assertSuccessful(response)
        self.assertEqual(response["X-File-Packet-Status"], FilePacket.STORED)
        self.assertIn("X-File-Packet-Status", response["vary"].split(","))

    for msg in messages:
        digest = hashlib.sha256(msg).hexdigest()
        response = self.client.get(f"/private/ffs/file-packet/{digest}")
        self.assertSuccessful(response)
        self.assertEqual(response["X-File-Packet-Status"], FilePacket.STORED)
        self.assertEqual(reduce(lambda a, b: a + b, response.streaming_content), msg)


class MyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='Test', password="guenthner.xyz")
        cls.user.user_permissions.add(Permission.objects.get(codename="ffs"))

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)
        self.my_set_up()

    def my_set_up(self):
        pass

    def assertSuccessful(self, response):
        try:
            self.assertEqual(response.status_code, 200, response.content.decode())
        except Exception as e:
            self.assertEqual(response.status_code, 200, f"(No content, {e})")


class FilePacketTests(MyTestCase):

    def my_set_up(self):
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
        self.assertSuccessful(response)

    def test_short_msg(self):
        test_file_packet_messages(self, self.short_messages)

    def test_long_msg(self):
        test_file_packet_messages(self, self.long_messages)

    def test_super_long_msg(self):
        test_file_packet_messages(self, self.super_long_messages)


class FileLedgerTest(MyTestCase):
    def upload_test_frwk(self, file_name, test_data):
        file_path = Path("django-test") / file_name
        actual_file = settings.FFS_FS_ROOT / file_path
        actual_file.unlink(True)

        hashes = []
        overall_hash = hashlib.sha256()

        for data in test_data:
            hashes.append(hashlib.sha256(data).hexdigest())
            overall_hash.update(data)

        result = self.client.post(f"/private/ffs/file-ledger/{file_path}",
                                  content_type="application/json",
                                  data={"hashes": hashes})
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content, f"The files for {len(test_data)} hashes are missing".encode())

        for data, hsh in zip(test_data, hashes):
            result = self.client.post(f"/private/ffs/file-packet/{hsh}",
                                      content_type="text/plain", data=data)
            self.assertSuccessful(result)

        result = self.client.post(f"/private/ffs/file-ledger/{file_path}",
                                  content_type="application/json",
                                  data={"hashes": hashes})
        self.assertSuccessful(result)
        self.assertTrue(actual_file.exists())

        with open(actual_file, "rb") as fp:
            actual_hash = hashlib.file_digest(fp, "sha256")

        self.assertEqual(actual_hash.hexdigest(), overall_hash.hexdigest())

    def test_upload(self):
        test_data = [random.randbytes(settings.FFS_NET_BLOCK_SIZE)]
        self.upload_test_frwk("upload_test", test_data)

    @skipUnless(os.environ.get('S') == '1',
                "Skipping slow tests")
    def test_large_upload(self):
        test_data = []

        print("Generating lots of test data: ", end="")
        for x in range(0, 10 * 1000 * 1000 * 1000, settings.FFS_NET_BLOCK_SIZE):
            print(".", end="", flush=True)
            test_data.append(random.randbytes(settings.FFS_NET_BLOCK_SIZE))
        print()

        self.upload_test_frwk("large_upload_test", test_data)
