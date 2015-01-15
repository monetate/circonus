#!/usr/bin/env python

# pylint: disable=W0212

from datetime import datetime, timedelta
from time import sleep
from uuid import uuid4

import json
import unittest

from circonus import CirconusClient, tag, util
from circonus.annotation import Annotation
from circonus.client import API_BASE_URL, get_api_url
from mock import patch, MagicMock
from requests.exceptions import HTTPError

import responses


class CirconusClientTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_app_name = "TEST"
        cls.api_token = str(uuid4())
        cls.c = CirconusClient(cls.api_app_name, cls.api_token)

    def test_api_headers(self):
        expected = {
            "Accept": "application/json",
            "X-Circonus-App-Name": self.api_app_name,
            "X-Circonus-Auth-Token": self.api_token
        }
        actual = self.c.api_headers
        self.assertEqual(expected, actual)

    def test_get_api_url(self):
        expected = API_BASE_URL + "/path/to/resource"
        self.assertEqual(expected, get_api_url("path/to/resource"))
        self.assertEqual(expected, get_api_url("path/to/resource/"))
        self.assertEqual(expected, get_api_url("/path/to/resource"))
        self.assertEqual(expected, get_api_url("/path/to/resource/"))

    def test_annotation_context_manager(self):
        a = self.c.annotation(self.c, "title", "category")
        with patch("circonus.client.CirconusClient.create") as create_patch:
            create_patch.return_value = MagicMock()
            with a:
                self.assertIsNotNone(a.start)
                self.assertIsNone(a.stop)
            self.assertIsNotNone(a.stop)
            create_patch.assert_called()

    def test_create_annotation(self):
        with self.assertRaises(HTTPError):
            self.c.create_annotation("title", "category")

        with patch("circonus.client.CirconusClient.create") as create_patch:
            create_patch.return_value = MagicMock()
            a = self.c.create_annotation("title", "category")
            self.assertEqual("title", a.title)
            self.assertEqual("category", a.category)
            self.assertEqual("", a.description)
            self.assertEqual([], a.rel_metrics)
            self.assertEqual(a.start, a.stop)

            start = datetime.utcnow()
            a = self.c.create_annotation("title", "category", start)
            self.assertEqual("title", a.title)
            self.assertEqual("category", a.category)
            self.assertEqual("", a.description)
            self.assertEqual([], a.rel_metrics)
            self.assertEqual(start, a.start)
            self.assertEqual(a.start, a.stop)

            stop = start + timedelta(seconds=1)
            a = self.c.create_annotation("title", "category", start, stop)
            self.assertEqual("title", a.title)
            self.assertEqual("category", a.category)
            self.assertEqual("", a.description)
            self.assertEqual([], a.rel_metrics)
            self.assertEqual(start, a.start)
            self.assertEqual(stop, a.stop)

    def test_get(self):
        with patch("circonus.client.requests.get") as get_patch:
            get_patch.return_value = MagicMock()
            cid = "/user"
            self.c.get(cid)
            get_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, params=None)

            params = {"f_email": "test@example.com"}
            self.c.get(cid, params)
            get_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, params=params)

    def test_delete(self):
        with patch("circonus.client.requests.delete") as delete_patch:
            delete_patch.return_value = MagicMock()
            cid = "/user/12345"
            self.c.delete(cid)
            delete_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, params=None)

    def test_update(self):
        with patch("circonus.client.requests.put") as update_patch:
            update_patch.return_value = MagicMock()
            cid = "/user/12345"
            data = {"email": "test@example.com"}
            self.c.update(cid, data)
            update_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, data=json.dumps(data))

    def test_update_with_tags_only_acts_on_taggable_resources(self):
        self.assertFalse(self.c.update_with_tags("/account", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/alert", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/annotation", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/broker", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/check", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/data", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/rebuild_broker", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/rule_set", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/rule_set_group", ["cat:tag"]))
        self.assertFalse(self.c.update_with_tags("/user", ["cat:tag"]))

    @responses.activate
    def test_update_with_tags(self):
        cid = "/check_bundle/70681"
        existing_tags = ["environment:development", "region:us-east-1"]
        new_tags = ["new:tag"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": cid,
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        responses.add(responses.GET, get_api_url(cid), body=json.dumps(check_bundle), status=200,
                      content_type="application/json")
        with patch("circonus.client.requests.put") as put_patch:
            self.c.update_with_tags(cid, new_tags)
            data = json.dumps({"tags": tag.get_tags_with(check_bundle, new_tags)})
            put_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, data=data)

        new_tags = ["newer:tag", "newest:tag"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": cid,
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        responses.add(responses.GET, get_api_url(cid), body=json.dumps(check_bundle), status=200,
                      content_type="application/json")
        with patch("circonus.client.requests.put") as put_patch:
            self.c.update_with_tags(cid, new_tags)
            data = json.dumps({"tags": tag.get_tags_with(check_bundle, new_tags)})
            put_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, data=data)


class AnnotationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_app_name = "TEST"
        cls.api_token = str(uuid4())
        cls.c = CirconusClient(cls.api_app_name, cls.api_token)

    def test_create(self):
        a = Annotation(self.c, "title", "category")
        self.assertEqual("title", a.title)
        self.assertEqual("category", a.category)
        self.assertEqual("", a.description)
        self.assertEqual([], a.rel_metrics)
        self.assertIsNone(a.start)
        self.assertIsNone(a.stop)
        self.assertIsNone(a.response)

        with patch("circonus.client.CirconusClient.create") as create_patch:
            create_patch.return_value = MagicMock()
            a.start = datetime.utcnow()
            a.stop = a.start + timedelta(seconds=1)
            expected_data = {
                "title": a.title,
                "category": a.category,
                "start": a.datetime_to_int(a.start),
                "stop": a.datetime_to_int(a.stop),
                "description": a.description,
                "rel_metrics": a.rel_metrics
            }
            a.create()
            create_patch.assert_called_with(Annotation.RESOURCE_PATH, expected_data)


    def test_decorator(self):
        a = Annotation(self.c, "title", "category")

        @a
        def short_nap():
            """Sleep for a little while."""
            sleep(0.1)

        with patch("circonus.client.CirconusClient.create") as create_patch:
            create_patch.return_value = MagicMock()
            short_nap()
            self.assertIsNotNone(a.start)
            self.assertIsNotNone(a.stop)
            self.assertTrue(a.start < a.stop)
            self.assertGreaterEqual(a.stop - a.start, timedelta(seconds=0.1))
            self.assertLess(a.stop - a.start, timedelta(seconds=0.2))

    def test_context_manager(self):
        a = Annotation(self.c, "title", "category")

        with patch("circonus.client.CirconusClient.create") as create_patch:
            create_patch.return_value = MagicMock()
            with a:
                self.assertIsNotNone(a.start)
                self.assertIsNone(a.stop)
            self.assertIsNotNone(a.stop)
            create_patch.assert_called()


class UtilTestCase(unittest.TestCase):

    def test_get_resource_from_cid(self):
        expected = "check"
        cid = "%s/123456" % expected
        self.assertEqual(expected, util.get_resource_from_cid(cid))
        cid = "/%s/123456" % expected
        self.assertEqual(expected, util.get_resource_from_cid(cid))
        cid = "/%s/123456/" % expected
        self.assertEqual(expected, util.get_resource_from_cid(cid))

    def test_get_check_id_from_cid(self):
        expected = 123456
        cid = "/check_bundle/%d" % expected
        self.assertEqual(expected, util.get_check_id_from_cid(cid))
        cid = "check_bundle/%d" % expected
        self.assertEqual(expected, util.get_check_id_from_cid(cid))
        cid = "check_bundle/%d/" % expected
        self.assertEqual(expected, util.get_check_id_from_cid(cid))


class TagTestCase(unittest.TestCase):

    def test_is_taggable(self):
        self.assertTrue(tag.is_taggable("/check_bundle/12345"))
        self.assertTrue(tag.is_taggable("/contact_group/12345"))
        self.assertTrue(tag.is_taggable("/graph/12345"))
        self.assertTrue(tag.is_taggable("/maintenance/12345"))
        self.assertTrue(tag.is_taggable("/metric_cluster/12345"))
        self.assertTrue(tag.is_taggable("/template/12345"))
        self.assertTrue(tag.is_taggable("/worksheet/12345"))

        self.assertFalse(tag.is_taggable("/account"))
        self.assertFalse(tag.is_taggable("/alert"))
        self.assertFalse(tag.is_taggable("/annotation"))
        self.assertFalse(tag.is_taggable("/broker"))
        self.assertFalse(tag.is_taggable("/check"))
        self.assertFalse(tag.is_taggable("/data"))
        self.assertFalse(tag.is_taggable("/rebuild_broker"))
        self.assertFalse(tag.is_taggable("/rule_set"))
        self.assertFalse(tag.is_taggable("/rule_set_group"))
        self.assertFalse(tag.is_taggable("/user"))

    def test_get_tag_string(self):
        t = "tag"
        c = "category"
        expected = c + tag.TAG_SEP + t
        self.assertEqual(expected, tag._get_tag_string(t, c))
        expected = t
        self.assertEqual(expected, tag._get_tag_string(t))

    def test_get_telemetry_tag(self):
        t = "collectd"
        c = "telemetry"
        cb = {"type": t}
        expected = c + tag.TAG_SEP + t
        self.assertEqual(expected, tag._get_telemetry_tag(cb))

    def test_get_updated_tags(self):
        existing_tags = ["environment:development", "region:us-east-1"]
        new_tags = ["cat:tag"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": "/check_bundle/70681",
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        self.assertItemsEqual(existing_tags + new_tags, tag._get_updated_tags(set.union, check_bundle, new_tags))
        self.assertItemsEqual(new_tags, tag._get_updated_tags(set.union, {"tags": []}, new_tags))
        self.assertIsNone(tag._get_updated_tags(set.union, check_bundle, existing_tags))
        self.assertIsNone(tag._get_updated_tags(set.union, check_bundle, [existing_tags[0]]))
        self.assertIsNone(tag._get_updated_tags(set.union, check_bundle, []))
        self.assertIsNone(tag._get_updated_tags(set.union, {"tags": []}, []))
        self.assertIsNone(tag._get_updated_tags(set.union, {}, new_tags))
        self.assertIsNone(tag._get_updated_tags(set.union, {}, []))

        remove_tags = ["environment:development"]
        expected = ["region:us-east-1"]
        self.assertItemsEqual(expected, tag._get_updated_tags(set.difference, check_bundle, remove_tags))
        self.assertItemsEqual([existing_tags[1]], tag._get_updated_tags(set.difference, check_bundle,
                                                                        [existing_tags[0]]))
        self.assertEqual([], tag._get_updated_tags(set.difference, check_bundle, existing_tags))
        self.assertIsNone(tag._get_updated_tags(set.difference, check_bundle, []))
        self.assertIsNone(tag._get_updated_tags(set.difference, check_bundle, ["test:new"]))
        self.assertIsNone(tag._get_updated_tags(set.difference, {"tags": []}, ["test:new"]))
        self.assertIsNone(tag._get_updated_tags(set.difference, {"tags": []}, []))
        self.assertIsNone(tag._get_updated_tags(set.difference, {}, remove_tags))
        self.assertIsNone(tag._get_updated_tags(set.difference, {}, []))
        self.assertIsNone(tag._get_updated_tags(set.difference, {}, ["test:new"]))

    def test_get_tags_with(self):
        existing_tags = ["environment:development", "region:us-east-1"]
        tags = ["cat:tag"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": "/check_bundle/70681",
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        self.assertItemsEqual(existing_tags + tags, tag.get_tags_with(check_bundle, tags))
        self.assertItemsEqual(tags, tag.get_tags_with({"tags": []}, tags))
        self.assertIsNone(tag.get_tags_with(check_bundle, existing_tags))
        self.assertIsNone(tag.get_tags_with(check_bundle, [existing_tags[0]]))
        self.assertIsNone(tag.get_tags_with(check_bundle, []))
        self.assertIsNone(tag.get_tags_with({"tags": []}, []))
        self.assertIsNone(tag.get_tags_with({}, tags))
        self.assertIsNone(tag.get_tags_with({}, []))

    def test_get_tags_without(self):
        existing_tags = ["environment:development", "region:us-east-1"]
        tags = ["environment:development"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": "/check_bundle/70681",
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        expected = ["region:us-east-1"]
        self.assertItemsEqual(expected, tag.get_tags_without(check_bundle, tags))
        self.assertItemsEqual([existing_tags[1]], tag.get_tags_without(check_bundle, [existing_tags[0]]))
        self.assertEqual([], tag.get_tags_without(check_bundle, existing_tags))
        self.assertIsNone(tag.get_tags_without(check_bundle, []))
        self.assertIsNone(tag.get_tags_without(check_bundle, ["test:new"]))
        self.assertIsNone(tag.get_tags_without({"tags": []}, ["test:new"]))
        self.assertIsNone(tag.get_tags_without({"tags": []}, []))
        self.assertIsNone(tag.get_tags_without({}, tags))
        self.assertIsNone(tag.get_tags_without({}, []))
        self.assertIsNone(tag.get_tags_without({}, ["test:new"]))

    def test_with_tags(self):
        @tag.with_tags()
        def noop(_, cid, data):
            pass

        cid = "/check_bundle/12345"
        data = {}
        noop(None, cid, data)
        expected = {"tags": []}
        self.assertEqual(expected, data)

        common_tags = ["category:tag", "global"]
        @tag.with_tags(common_tags)
        def noop(_, cid, data):
            pass
        noop(None, cid, data)
        expected = common_tags
        self.assertItemsEqual(expected, data["tags"])

        data["tags"].append("new:another")
        noop(None, cid, data)
        expected = ["category:tag", "global", "new:another"]
        self.assertItemsEqual(expected, data["tags"])

        data["type"] = "collectd"
        noop(None, cid, data)
        expected = ["category:tag", "global", "new:another", "telemetry:collectd"]
        self.assertItemsEqual(expected, data["tags"])

        @tag.with_tags(["common:new"])
        def noop(_, cid, data):
            pass

        cid = "/check_bundle/12345"
        data = {}
        noop(None, cid, data)
        expected = {"tags": ["common:new"]}
        self.assertEqual(expected, data)

        cid = "/check_bundle/12345"
        data = {"tags": ["existing:tag"]}
        noop(None, cid, data)
        expected = {"tags": ["existing:tag", "common:new"]}
        self.assertEqual(expected, data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
