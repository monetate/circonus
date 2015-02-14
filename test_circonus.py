#!/usr/bin/env python

# pylint: disable=W0212

from datetime import datetime, timedelta
from time import sleep
from uuid import uuid4

import json
import re
import types
import unittest

from colour import Color
from circonus import CirconusClient, graph, metric, tag, util
from circonus.annotation import Annotation
from circonus.client import API_BASE_URL, get_api_url
from circonus.collectd import cpu, df, interface, memory
from circonus.collectd.graph import get_collectd_graph_data
from mock import patch, MagicMock
from requests.exceptions import HTTPError

import requests
import responses


check_bundle = {"_checks": ["/check/123456"],
                "_cid": "/check_bundle/12345",
                "_created": 1417807923,
                "_last_modified": 1417807952,
                "_last_modified_by": "/user/1234",
                "brokers": ["/broker/123"],
                "config": {"asynch_metrics": "false",
                           "security_level": "0",
                           "submission_target": "10.0.0.2:25826"},
                "display_name": "10.0.0.1 collectd",
                "metrics": [{"name": "interface`eth0`if_packets`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdj`disk_octets`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`eth0`if_octets`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`lo`if_errors`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`1`cpu`idle", "status": "active", "type": "numeric"},
                            {"name": "cpu`1`cpu`user", "status": "active", "type": "numeric"},
                            {"name": "load`load`1min", "status": "active", "type": "numeric"},
                            {"name": "df`mnt-mysql`df_complex`used",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-mysql`df_complex`free",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-mysql`df_complex`reserved",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-mysql`percent_bytes`used",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-mysql`percent_bytes`free",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-mysql`percent_bytes`reserved",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-solr-home`df_complex`free",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-solr-home`df_complex`reserved",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt-solr-home`df_complex`used",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt`df_complex`free",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`eth0`if_octets`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sda1`disk_octets`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`0`cpu`steal", "status": "active", "type": "numeric"},
                            {"name": "cpu`1`cpu`interrupt", "status": "active", "type": "numeric"},
                            {"name": "swap`swap_io`in", "status": "active", "type": "numeric"},
                            {"name": "df`root`df_complex`reserved",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`lo`if_packets`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`dm-0`disk_time`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "load`load`15min", "status": "active", "type": "numeric"},
                            {"name": "cpu`0`cpu`idle", "status": "active", "type": "numeric"},
                            {"name": "disk`sdb`disk_ops`1", "status": "active", "type": "numeric"},
                            {"name": "disk`sdk`disk_ops`0", "status": "active", "type": "numeric"},
                            {"name": "disk`sdj`disk_ops`1", "status": "active", "type": "numeric"},
                            {"name": "disk`sda1`disk_ops`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "swap`swap_io`out", "status": "active", "type": "numeric"},
                            {"name": "disk`sdb`disk_merged`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdj`disk_ops`0", "status": "active", "type": "numeric"},
                            {"name": "cpu`0`cpu`wait", "status": "active", "type": "numeric"},
                            {"name": "interface`eth0`if_errors`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`dev-shm`df_complex`used",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`dm-0`disk_merged`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sda1`disk_time`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`1`cpu`steal", "status": "active", "type": "numeric"},
                            {"name": "interface`sit0`if_octets`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`dm-0`disk_time`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`dm-0`disk_merged`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`lo`if_octets`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "memory`memory`buffered",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdb`disk_octets`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`sit0`if_octets`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdb`disk_merged`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`eth0`if_packets`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdk`disk_time`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdk`disk_octets`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`sit0`if_errors`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdk`disk_merged`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`1`cpu`nice", "status": "active", "type": "numeric"},
                            {"name": "disk`dm-0`disk_octets`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt`df_complex`reserved",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdb`disk_octets`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`1`cpu`system", "status": "active", "type": "numeric"},
                            {"name": "disk`sdj`disk_octets`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sda1`disk_time`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdk`disk_time`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`lo`if_octets`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`0`cpu`softirq", "status": "active", "type": "numeric"},
                            {"name": "df`root`df_complex`free",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`root`df_complex`used",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdb`disk_time`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdk`disk_octets`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`dm-0`disk_octets`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`dm-0`disk_ops`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sda1`disk_merged`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`sit0`if_errors`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "memory`memory`free", "status": "active", "type": "numeric"},
                            {"name": "cpu`0`cpu`nice", "status": "active", "type": "numeric"},
                            {"name": "disk`sdb`disk_time`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`dev-shm`df_complex`free",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdb`disk_ops`0", "status": "active", "type": "numeric"},
                            {"name": "interface`sit0`if_packets`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sda1`disk_octets`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdj`disk_merged`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`1`cpu`softirq", "status": "active", "type": "numeric"},
                            {"name": "disk`dm-0`disk_ops`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdj`disk_merged`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdj`disk_time`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`0`cpu`user", "status": "active", "type": "numeric"},
                            {"name": "disk`sdj`disk_time`1",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`dev-shm`df_complex`reserved",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "interface`sit0`if_packets`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "memory`memory`cached",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sda1`disk_merged`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "load`load`5min", "status": "active", "type": "numeric"},
                            {"name": "interface`lo`if_packets`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "df`mnt`df_complex`used",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`0`cpu`system", "status": "active", "type": "numeric"},
                            {"name": "interface`eth0`if_errors`tx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdk`disk_ops`1", "status": "active", "type": "numeric"},
                            {"name": "cpu`1`cpu`wait", "status": "active", "type": "numeric"},
                            {"name": "interface`lo`if_errors`rx",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "memory`memory`used", "status": "active", "type": "numeric"},
                            {"name": "disk`sda1`disk_ops`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "disk`sdk`disk_merged`0",
                             "status": "active",
                             "type": "numeric"},
                            {"name": "cpu`0`cpu`interrupt",
                             "status": "active",
                             "type": "numeric"}],
                "notes": None,
                "period": 60,
                "status": "active",
                "tags": [],
                "target": "10.0.0.1",
                "timeout": 59,
                "type": "collectd"}


class CirconusClientTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_app_name = "TEST"
        cls.api_token = str(uuid4())
        cls.c = CirconusClient(cls.api_app_name, cls.api_token)

    @responses.activate
    def test_common_tags(self):
        self.assertEqual([], self.c.common_tags)

        common_tags = ["cat:tag", "global"]
        c = CirconusClient(self.c.api_app_name, self.c.api_token, common_tags)
        self.assertEqual(common_tags, c.common_tags)

        cid = "/check_bundle/12345"
        data = json.dumps({"tags": common_tags})
        with patch("circonus.client.requests.put") as put_patch:
            c.update(cid, {})
            put_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, data=data)

        tags_with_telemetry = common_tags + ["telemetry:collectd"]
        data = json.dumps({"type": "collectd", "tags": tags_with_telemetry})
        with patch("circonus.client.requests.put") as put_patch:
            c.update(cid, {"type": "collectd"})
            put_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, data=data)
            self.assertItemsEqual(common_tags, c.common_tags)

        tags_with_telemetry = common_tags + ["telemetry:collectd"]
        data = {"type": "collectd", "tags": ["existing:tag"]}
        expected_data = json.dumps({"type": "collectd", "tags": tag.get_tags_with(data, tags_with_telemetry)})
        with patch("circonus.client.requests.put") as put_patch:
            c.update(cid, data)
            put_patch.assert_called_with(get_api_url(cid), headers=self.c.api_headers, data=expected_data)
            self.assertItemsEqual(common_tags, c.common_tags)

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

    @responses.activate
    def test_log_http_error_raises_http_error(self):
        cid = "graph/12345"
        responses.add(responses.GET, get_api_url(cid),
                      body=json.dumps({"message": "test", "code": "test", "explanation": "test"}),
                      status=500,
                      content_type="application/json")
        with self.assertRaises(HTTPError):
            self.c.get(cid)

    def test_annotation_context_manager(self):
        a = self.c.annotation(self.c, "title", "category")
        with patch("circonus.client.CirconusClient.create") as create_patch:
            create_patch.return_value = MagicMock()
            with a:
                self.assertIsNotNone(a.start)
                self.assertIsNone(a.stop)
            self.assertIsNotNone(a.stop)
            create_patch.assert_called()

    @responses.activate
    def test_create_annotation(self):
        responses.add(responses.POST, get_api_url(Annotation.RESOURCE_PATH),
                      body=json.dumps({"message": "test", "code": "test", "explanation": "test"}), status=403,
                      content_type="application/json")
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

    def test_create_collectd_cpu_graph_no_metrics(self):
        target = "10.0.0.1"
        check_bundle = {"status": "active",
                        "_last_modified_by": "/user/1234",
                        "display_name": "%s collectd" % target,
                        "target": target,
                        "type": "collectd",
                        "notes": None,
                        "period": 60,
                        "metrics": [],
                        "brokers": ["/broker/123"],
                        "timeout": 59,
                        "_cid": "/check_bundle/12345",
                        "_created": 1413988231,
                        "_checks": ["/check/12345"],
                        "config": {"asynch_metrics": "false",
                                   "submission_target": "10.0.0.2:25826",
                                   "security_level": "0"},
                        "_last_modified": 1416618604}
        data = {}
        with patch("circonus.client.requests.post") as post_patch:
            self.assertIsNone(self.c.create_collectd_cpu_graph(check_bundle))
            post_patch.assert_not_called()

    def test_create_collectd_cpu_graph(self):
        target = "10.0.0.1"
        cb = {"_checks": ["/check_bundle/12345"],
              "target": target,
              "type": "collectd",
              "metrics": [{'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                          {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'}]}
        expected = {"max_left_y": 100,
                    "datapoints": [{"derive": "counter", "name": "cpu`0`cpu`steal", "color": "#ff0000", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "cpu`0`cpu`steal"},
                                   {"derive": "counter", "name": "cpu`0`cpu`interrupt", "color": "#f72100", "legend_formula": None,"check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "cpu`0`cpu`interrupt"},
                                   {"derive": "counter", "name": "cpu`0`cpu`softirq", "color": "#ee3f00", "legend_formula":None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "cpu`0`cpu`softirq"},
                                   {"derive": "counter", "name": "cpu`0`cpu`system", "color": "#e65c00", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "cpu`0`cpu`system"},
                                   {"derive": "counter", "name": "cpu`0`cpu`wait", "color": "#dd7600", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "cpu`0`cpu`wait"},
                                   {"derive": "counter", "name": "cpu`0`cpu`user", "color": "#d58e00", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "cpu`0`cpu`user"},
                                   {"derive": "counter", "name": "cpu`0`cpu`nice", "color": "#cca300", "legend_formula":None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack":0, "metric_name": "cpu`0`cpu`nice"},
                                   {"derive": "counter", "name": "cpu`0`cpu`idle", "color": "#c4b700", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": True, "axis": "l", "stack": 0,"metric_name": "cpu`0`cpu`idle"},
                                   {"derive": "counter", "name": "cpu`1`cpu`steal", "color": "#afbb00", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 1,"metric_name": "cpu`1`cpu`steal"},
                                   {"derive": "counter", "name": "cpu`1`cpu`interrupt", "color": "#8fb300", "legend_formula":None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack":1, "metric_name": "cpu`1`cpu`interrupt"},
                                   {"derive": "counter", "name": "cpu`1`cpu`softirq", "color": "#72aa00", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 1, "metric_name": "cpu`1`cpu`softirq"},
                                   {"derive": "counter", "name": "cpu`1`cpu`system", "color": "#56a200", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l","stack": 1, "metric_name": "cpu`1`cpu`system"},
                                   {"derive": "counter", "name": "cpu`1`cpu`wait", "color": "#3d9900", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l","stack": 1, "metric_name": "cpu`1`cpu`wait"},
                                   {"derive": "counter", "name": "cpu`1`cpu`user", "color": "#279100", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 1, "metric_name": "cpu`1`cpu`user"},
                                   {"derive": "counter", "name": "cpu`1`cpu`nice", "color": "#128800", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 1, "metric_name": "cpu`1`cpu`nice"},
                                   {"derive": "counter", "name": "cpu`1`cpu`idle", "color": "#008000", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": True, "axis": "l", "stack": 1, "metric_name": "cpu`1`cpu`idle"}],
                    "tags": ["telemetry:collectd"],
                    "title": "10.0.0.1 cpu"}
        with patch("circonus.client.requests.post") as post_patch:
            self.assertIsNotNone(self.c.create_collectd_cpu_graph(cb))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(expected, actual)

            title = "test title"
            self.assertIsNotNone(self.c.create_collectd_cpu_graph(cb, title))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(title, actual["title"])

    def test_create_collectd_memory_graph_no_memory_metrics(self):
        target = "10.0.0.1"
        cb = {"target": target, "type": "collectd"}
        with patch("circonus.client.requests.post") as post_patch:
            self.assertIsNone(self.c.create_collectd_memory_graph(cb))
            post_patch.assert_not_called()

    def test_create_collectd_memory_graph_too_few_metrics(self):
        target = "10.0.0.1"
        cb = {"_checks": ["/check_bundle/12345"],
              "target": target,
              "type": "collectd",
              "metrics": [{"status": "active", "type": "numeric", "name": "memory`memory`cached"}]}
        expected = {"min_left_y": 0, "datapoints": [], "tags": ["telemetry:collectd"], "min_right_y": 0, "title": "10.0.0.1 memory"}
        with patch("circonus.client.requests.post") as post_patch:
            self.assertIsNotNone(self.c.create_collectd_memory_graph(cb))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(expected, actual)

    def test_create_collectd_memory_graph(self):
        target = "10.0.0.1"
        cb = {"_checks": ["/check_bundle/12345"],
              "target": target,
              "type": "collectd",
              "metrics": [{"status": "active", "type": "numeric", "name": "memory`memory`cached"},
                          {"status": "active", "type": "numeric", "name": "memory`memory`free"},
                          {"status": "active", "type": "numeric", "name": "memory`memory`used"},
                          {"status": "active", "type": "numeric", "name": "memory`memory`buffered"}]}
        expected = {"min_left_y": 0,
                    "datapoints": [{"color": "#ff0000", "legend_formula": None, "derive": "gauge", "metric_type": "numeric", "alpha": None, "stack": 0, "name": "memory`memory`used", "data_formula": None, "metric_name": "memory`memory`used", "check_id": 12345, "hidden": False, "axis": "l"},
                                   {"color": "#d58e00", "legend_formula": None, "derive": "gauge", "metric_type": "numeric", "alpha": None, "stack": 0, "name": "memory`memory`buffered", "data_formula": None,"metric_name": "memory`memory`buffered", "check_id": 12345, "hidden": False, "axis": "l"},
                                   {"color": "#72aa00", "legend_formula": None, "derive": "gauge", "metric_type": "numeric", "alpha": None, "stack": 0, "name": "memory`memory`cached", "data_formula": None, "metric_name": "memory`memory`cached", "check_id": 12345, "hidden": False, "axis": "l"},
                                   {"color": "#008000", "legend_formula": None, "derive": "gauge", "metric_type": "numeric", "alpha": None, "stack": 0, "name":"memory`memory`free", "data_formula": None, "metric_name": "memory`memory`free", "check_id": 12345, "hidden": False, "axis": "l"}],
                    "tags": ["telemetry:collectd"],
                    "min_right_y": 0,
                    "title": "10.0.0.1 memory"}
        with patch("circonus.client.requests.post") as post_patch:
            self.assertIsNotNone(self.c.create_collectd_memory_graph(cb))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(expected, actual)

            title = "test title"
            self.assertIsNotNone(self.c.create_collectd_memory_graph(cb, title))
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(title, actual["title"])

    def test_create_collectd_interface_graph(self):
        target = "10.0.0.1"
        cb = {"_checks": ["/check_bundle/12345"],
              "target": target,
              "type": "collectd",
              "metrics": [{"name": "interface`eth0`if_octets`rx", "status": "active", "type": "numeric"},
                          {"name": "interface`eth0`if_octets`tx", "status": "active", "type": "numeric"},
                          {"name": "interface`eth0`if_errors`rx", "status": "active", "type": "numeric"},
                          {"name": "interface`eth0`if_errors`tx", "status": "active", "type": "numeric"}]}
        expected = {"title": "10.0.0.1 interface eth0 bit/s",
                    "datapoints": [
                        {"derive": "counter", "name": "interface`eth0`if_octets`tx", "color": "#ff0000", "legend_formula":None, "check_id": 12345, "data_formula": "=8*VAL", "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": None, "metric_name": "interface`eth0`if_octets`tx"},
                        {"derive": "counter", "name": "interface`eth0`if_octets`rx", "color": "#008000", "legend_formula": None, "check_id": 12345, "data_formula": "=-8*VAL","metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": None, "metric_name": "interface`eth0`if_octets`rx"},
                        {"derive": "counter", "name": "interface`eth0`if_errors`tx", "color": "#ff0000", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "r", "stack": None, "metric_name": "interface`eth0`if_errors`tx"},
                        {"derive": "counter", "name": "interface`eth0`if_errors`rx", "color": "#008000", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "r", "stack": None, "metric_name": "interface`eth0`if_errors`rx"}],
                    "tags": ["telemetry:collectd"]}
        with patch("circonus.client.requests.post") as post_patch:
            self.assertIsNotNone(self.c.create_collectd_interface_graph(cb))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(expected, actual)

            title = "test title"
            expected = title + " eth0 bit/s"
            self.assertIsNotNone(self.c.create_collectd_interface_graph(cb, title=title))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(expected, actual["title"])

    def test_create_collectd_df_graph(self):
        target = "10.0.0.1"
        cb = {"_checks": ["/check_bundle/12345"],
              "target": target,
              "type": "collectd",
              "metrics": [{"name": "df`mnt-mysql`df_complex`used", "status": "active", "type": "numeric"},
                          {"name": "df`mnt-mysql`df_complex`free", "status": "active", "type": "numeric"},
                          {"name": "df`mnt-mysql`df_complex`reserved", "status": "active", "type": "numeric"},
                          {"name": "df`mnt-solr-home`df_complex`free", "status": "active", "type": "numeric"},
                          {"name": "df`mnt-solr-home`df_complex`reserved", "status": "active", "type": "numeric"},
                          {"name": "df`mnt-solr-home`df_complex`used", "status": "active", "type": "numeric"},
                          {"name": "df`mnt`df_complex`free", "status": "active", "type": "numeric"}]}
        expected = {"min_right_y": 0,
                    "title": "10.0.0.1 df /mnt/mysql",
                    "min_left_y": 0,
                    "tags": ["telemetry:collectd"],
                    "datapoints": [{"derive": "gauge", "name": "df`mnt-mysql`df_complex`reserved", "color": "#ff0000", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "df`mnt-mysql`df_complex`reserved"},
                                   {"derive": "gauge", "name": "df`mnt-mysql`df_complex`used", "color": "#bfbf00", "legend_formula":None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis":"l", "stack": 0, "metric_name": "df`mnt-mysql`df_complex`used"},
                                   {"derive": "gauge", "name": "df`mnt-mysql`df_complex`free", "color": "#008000", "legend_formula": None, "check_id": 12345, "data_formula": None, "metric_type": "numeric", "alpha": None, "hidden": False, "axis": "l", "stack": 0, "metric_name": "df`mnt-mysql`df_complex`free"}]}
        with patch("circonus.client.requests.post") as post_patch:
            self.assertIsNotNone(self.c.create_collectd_df_graph(cb, "/mnt/mysql"))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(expected, actual)

            title = "test title"
            mount_dir = "/mnt/mysql"
            expected = "%s %s" % (title, mount_dir)
            self.assertIsNotNone(self.c.create_collectd_df_graph(cb, mount_dir, title))
            post_patch.assert_called()
            actual = json.loads(post_patch.call_args[-1]["data"])
            self.assertEqual(expected, actual["title"])

    def test_create_collectd_graphs_log_error(self):
        target = "10.0.0.1"
        responses.add(responses.POST, get_api_url("graph"),
                      body=json.dumps({"message": "test", "code": "test", "explanation": "test"}),
                      status=500,
                      content_type="application/json")
        with patch("circonus.client.log") as log_patch:
            self.c.create_collectd_graphs(check_bundle)
            self.assertEqual("collectd graphs could not be created: %s", log_patch.error.call_args[0][0])

    def test_create_collectd_graphs_no_metrics(self):
        target = "10.0.0.1"
        cb = {"_checks": ["/check_bundle/12345"],
              "target": target,
              "type": "collectd",
              "metrics": []}
        with patch("circonus.client.requests.post") as post_patch:
            post_patch.return_value = response_mock = MagicMock()
            response_mock.status_code = 200
            success, rs = self.c.create_collectd_graphs(cb)
            post_patch.assert_called()
            self.assertTrue(success)
            self.assertIsInstance(rs, types.ListType)
            self.assertEqual(1, len(rs))
            self.assertEqual(1, post_patch.call_count)

    @responses.activate
    def test_create_collectd_graphs_logs_http_error(self):
        responses.add(responses.GET, get_api_url("check_bundle"),
                      body=json.dumps({"message": "test", "code": "test", "explanation": "test"}),
                      status=500,
                      content_type="application/json")
        with patch("circonus.client.log") as log_patch:
            success, rs = self.c.create_collectd_graphs(check_bundle)
            self.assertFalse(success)
            self.assertEqual([], rs)
            self.assertEqual("collectd graphs could not be created: %s", log_patch.error.call_args[0][0])

    def test_create_collectd_graphs(self):
        target = "10.0.0.1"
        with patch("circonus.client.requests.post") as post_patch:
            post_patch.return_value = response_mock = MagicMock()
            response_mock.status_code = 200
            success, rs = self.c.create_collectd_graphs(check_bundle)
            post_patch.assert_called()
            self.assertTrue(success)
            self.assertEqual(4, len(rs))
            self.assertEqual(4, post_patch.call_count)


class AnnotationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_app_name = "TEST"
        cls.api_token = str(uuid4())
        cls.c = CirconusClient(cls.api_app_name, cls.api_token)

    def test_create_raises_http_error(self):
        a = Annotation(self.c, "title", "category")
        a.start = datetime.utcnow()
        a.stop = a.start + timedelta(seconds=1)
        responses.add(responses.GET, get_api_url(Annotation.RESOURCE_PATH),
                      body=json.dumps({"message": "test", "code": "test", "explanation": "test"}),
                      status=500,
                      content_type="application/json")
        with self.assertRaises(HTTPError):
            a.create()

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
                "start": util.datetime_to_int(a.start),
                "stop": util.datetime_to_int(a.stop),
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

    def test_colors(self):
        items = ["one"]
        self.assertIsInstance(util.colors(items), types.GeneratorType)

        expected = [Color("red")]
        actual = list(util.colors(items))
        self.assertEqual(expected, actual)

        items = ["one", "two"]
        expected = [Color("red"), Color("green")]
        actual = list(util.colors(items))
        self.assertEqual(expected, actual)


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
        self.assertEqual(expected, tag.get_tag_string(t, c))
        expected = t
        self.assertEqual(expected, tag.get_tag_string(t))

    def test_get_telemetry_tag(self):
        t = "collectd"
        c = "telemetry"
        cb = {"type": t}
        expected = c + tag.TAG_SEP + t
        self.assertEqual(expected, tag.get_telemetry_tag(cb))

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


class MetricTestCase(unittest.TestCase):

    def test_get_metrics(self):
        self.assertEqual([], metric.get_metrics({}, cpu.CPU_METRIC_RE))

        expected = [{'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'}]
        actual = metric.get_metrics(check_bundle, cpu.CPU_METRIC_RE)
        self.assertEqual(expected, actual)

    def test_get_metrics_sorted_by_suffix(self):
        unsorted_metrics = metric.get_metrics(check_bundle, cpu.CPU_METRIC_RE)
        sorted_metrics = metric.get_metrics_sorted_by_suffix(unsorted_metrics, cpu.CPU_METRIC_SUFFIXES)
        actual = [m["name"].rpartition("`")[-1] for m in sorted_metrics]
        self.assertEqual(cpu.CPU_METRIC_SUFFIXES, actual)

    def test_get_metrics_sorted_by_suffix_too_few_metrics(self):
        unsorted_metrics = []
        sorted_metrics = metric.get_metrics_sorted_by_suffix(unsorted_metrics, cpu.CPU_METRIC_SUFFIXES)
        self.assertEqual([], sorted_metrics)

        unsorted_metrics = metric.get_metrics(check_bundle, cpu.CPU_METRIC_RE)[:1]
        sorted_metrics = metric.get_metrics_sorted_by_suffix(unsorted_metrics, cpu.CPU_METRIC_SUFFIXES)
        self.assertEqual([], sorted_metrics)

    def test_get_datapoints(self):
        metrics = metric.get_metrics(check_bundle, cpu.CPU_METRIC_RE)
        check_id = util.get_check_id_from_cid(check_bundle["_cid"])
        datapoints = metric.get_datapoints(check_id, metrics)
        for dp in datapoints:
            self.assertIn("color", dp)
            self.assertIsInstance(dp["color"], types.StringType)

        datapoints = metric.get_datapoints(check_id, metrics, {"custom": "attribute"})
        for dp in datapoints:
            self.assertIn("custom", dp)
            self.assertEqual("attribute", dp["custom"])

    def test_get_metrics_with_status(self):
        metrics = [{'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'}]
        expected = [{'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'}]
        actual = metric.get_metrics_with_status(metrics, "active")
        self.assertEqual(expected, actual)
        self.assertNotEqual(expected, metrics)

        metrics = [{'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                   {'status': 'available', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'}]
        expected = [{'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'},
                    {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                    {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                    {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                    {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                    {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                    {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                    {'status': 'available', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'}]
        active_metric_re = re.compile(r"^cpu`0")
        actual = metric.get_metrics_with_status(metrics, "active", active_metric_re)
        self.assertEqual(expected, actual)
        self.assertNotEqual(expected, metrics)


class CollectdCpuTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.metrics = [{'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                       {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'}]

    def test_get_cpus(self):
        expected = ['cpu`0`', 'cpu`1`']
        actual = cpu._get_cpus(self.metrics)
        self.assertEqual(expected, actual)

    def test_get_cpu_metrics(self):
        expected = [{'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`steal'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`interrupt'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`system'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`wait'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`nice'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`0`cpu`idle'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`steal'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`interrupt'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`softirq'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`system'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`wait'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`user'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`nice'},
                    {'status': 'active', 'type': 'numeric', 'name': 'cpu`1`cpu`idle'}]
        actual = cpu.get_cpu_metrics(self.metrics)
        self.assertEqual(expected, actual)

    def test_get_stacked_cpu_metrics(self):
        self.assertEqual([], cpu.get_stacked_cpu_metrics([]))
        stacked_metrics = cpu.get_stacked_cpu_metrics(self.metrics)
        for m in stacked_metrics:
            self.assertIn(str(m["stack"]), m["name"])
            if m["name"].endswith("idle"):
                self.assertTrue(m["hidden"])
        self.assertNotEqual(self.metrics, stacked_metrics)

        stacked_metrics = cpu.get_stacked_cpu_metrics(self.metrics, hide_idle=False)
        for m in stacked_metrics:
            self.assertIn(str(m["stack"]), m["name"])
            self.assertNotIn("hidden", m)
        self.assertNotEqual(self.metrics, stacked_metrics)

    def test_get_cpu_datapoints(self):
        self.assertEqual([], cpu.get_cpu_datapoints({}, []))
        metrics = cpu.get_stacked_cpu_metrics(self.metrics)
        datapoints = cpu.get_cpu_datapoints(check_bundle, metrics)
        self.assertIsInstance(datapoints, types.ListType)

    def test_get_cpu_graph_data(self):
        self.assertEqual({}, cpu.get_cpu_graph_data({}))
        data = cpu.get_cpu_graph_data(check_bundle)
        self.assertIn("tags", data)
        self.assertEqual(["telemetry:collectd"], data["tags"])
        self.assertIn("datapoints", data)
        self.assertIsInstance(data["datapoints"], types.ListType)
        self.assertIn("title", data)
        self.assertEqual("%s cpu" % check_bundle["target"], data["title"])
        self.assertEqual(100, data["max_left_y"])

        expected = "test cpu"
        data = cpu.get_cpu_graph_data(check_bundle, expected)
        actual = data["title"]
        self.assertEqual(expected, actual)


class CollectdMemoryTestCase(unittest.TestCase):

    def test_get_sorted_memory_metrics(self):
        expected = [{"status": "active", "type": "numeric", "name": "memory`memory`used"},
                    {"status": "active", "type": "numeric", "name": "memory`memory`buffered"},
                    {"status": "active", "type": "numeric", "name": "memory`memory`cached"},
                    {"status": "active", "type": "numeric", "name": "memory`memory`free"}]
        actual = memory.get_sorted_memory_metrics(metric.get_metrics(check_bundle, memory.MEMORY_METRIC_RE))
        self.assertEqual(expected, actual)

    def test_get_memory_datapoints(self):
        metrics = memory.get_sorted_memory_metrics(metric.get_metrics(check_bundle, memory.MEMORY_METRIC_RE))
        datapoints = memory.get_memory_datapoints(check_bundle, metrics)
        for dp in datapoints:
            self.assertEqual("gauge", dp["derive"])
            self.assertEqual(0, dp["stack"])

    def test_get_memory_graph_data(self):
        self.assertEqual({}, memory.get_memory_graph_data({}))

        data = memory.get_memory_graph_data(check_bundle)
        self.assertIn("title", data)
        self.assertEqual("%s memory" % check_bundle["target"], data["title"])
        self.assertEqual(0, data["min_left_y"])
        self.assertEqual(0, data["min_right_y"])
        self.assertIn("datapoints", data)
        for dp in data["datapoints"]:
            self.assertEqual("gauge", dp["derive"])
            self.assertEqual(0, dp["stack"])

        expected = "test title"
        data = memory.get_memory_graph_data(check_bundle, expected)
        actual = data["title"]
        self.assertEqual(expected, actual)


class CollectdInterfaceTestCase(unittest.TestCase):

    def test_get_interface_metrics(self):
        self.assertEqual([], interface.get_interface_metrics({}))

        expected = [m for m in check_bundle["metrics"] if m["name"].startswith("interface`eth0")]
        actual = interface.get_interface_metrics(check_bundle["metrics"])
        self.assertItemsEqual(expected, actual)

        expected = [m for m in check_bundle["metrics"] if m["name"].startswith("interface`eth0")]
        actual = interface.get_interface_metrics(check_bundle["metrics"], "eth0")
        self.assertItemsEqual(expected, actual)

        expected = [m for m in check_bundle["metrics"] if m["name"].startswith("interface`eth0") and "octets" in m["name"]]
        actual = interface.get_interface_metrics(check_bundle["metrics"], "eth0", "octets")
        self.assertItemsEqual(expected, actual)

    def test_get_interface_datapoints(self):
        self.assertEqual([], interface.get_interface_datapoints({}))

        datapoints = interface.get_interface_datapoints(check_bundle)
        self.assertIsInstance(datapoints, types.ListType)
        self.assertTrue(len(datapoints) > 0)
        for dp in datapoints:
            self.assertIsInstance(dp, types.DictType)
            self.assertIn("metric_name", dp)
            self.assertTrue(dp["metric_name"].startswith("interface`eth0"))
            self.assertIn("data_formula", dp)
            if "octets" in dp["metric_name"]:
                if dp["metric_name"].endswith("tx"):
                    self.assertEqual("=8*VAL", dp["data_formula"])
                elif dp["metric_name"].endswith("rx"):
                    self.assertEqual("=-8*VAL", dp["data_formula"])
            if "errors" in dp["metric_name"]:
                self.assertIn("axis", dp)
                self.assertEqual("r", dp["axis"])
            self.assertIn("derive", dp)
            self.assertEqual("counter", dp["derive"])
        self.assertTrue([dp for dp in datapoints if "octets" in dp["metric_name"]])
        self.assertTrue([dp for dp in datapoints if "errors" in dp["metric_name"]])

        interface_name = "eth1"
        datapoints = interface.get_interface_datapoints(check_bundle, interface_name)
        self.assertEqual([], datapoints)

    def test_is_transmitter(self):
        self.assertTrue(interface.is_transmitter({"name": "tx"}))
        self.assertTrue(interface.is_transmitter({"name": "test tx"}))
        self.assertFalse(interface.is_transmitter({"name": "rx"}))
        self.assertFalse(interface.is_transmitter({"name": "test rx"}))
        self.assertFalse(interface.is_transmitter({"name": "test"}))
        self.assertFalse(interface.is_transmitter({}))

    def test_is_receiver(self):
        self.assertTrue(interface.is_receiver({"name": "rx"}))
        self.assertTrue(interface.is_receiver({"name": "test rx"}))
        self.assertFalse(interface.is_receiver({"name": "tx"}))
        self.assertFalse(interface.is_receiver({"name": "test tx"}))
        self.assertFalse(interface.is_receiver({"name": "test"}))
        self.assertFalse(interface.is_receiver({}))

    def test_get_interface_graph_data(self):
        data = interface.get_interface_graph_data({"target": "10.0.0.1", "type": "collectd"})
        self.assertEqual([], data["datapoints"])

        data = interface.get_interface_graph_data(check_bundle)
        self.assertIn("datapoints", data)
        self.assertIn("title", data)
        self.assertEqual("%s interface eth0 bit/s" % check_bundle["target"], data["title"])

        title = "test title"
        expected = title + " eth0 bit/s"
        data = interface.get_interface_graph_data(check_bundle, title=title)
        actual = data["title"]
        self.assertEqual(expected, actual)


class CollectdDfTestCase(unittest.TestCase):

    def test_is_mount_dir(self):
        metric_name = "df`root`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "root"))
        metric_name = "df`root`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "/root"))
        metric_name = "df`root`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "/root/"))

        metric_name = "df`mnt-mysql`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "mnt/mysql"))
        metric_name = "df`mnt-mysql`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "/mnt/mysql"))
        metric_name = "df`mnt-mysql`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "/mnt/mysql/"))

        metric_name = "df`mnt-solr-home`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "mnt/solr-home"))
        metric_name = "df`mnt-solr-home`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "/mnt/solr-home"))
        metric_name = "df`mnt-solr-home`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "/mnt/solr-home/"))

        metric_name = u"df`mnt-solr-home`df_complex`free"
        self.assertTrue(df.is_mount_dir(metric_name, "/mnt/solr-home/"))

        metric_name = ""
        self.assertFalse(df.is_mount_dir(metric_name, ""))
        self.assertFalse(df.is_mount_dir(metric_name, "/root"))

    def test_get_df_metrics(self):
        self.assertEqual([], df.get_df_metrics({}, "/"))

        expected = [m for m in check_bundle["metrics"] if m["name"].startswith("df`")]
        expected = [m for m in expected if "`root`" in m["name"]]
        actual = df.get_df_metrics(check_bundle["metrics"], "root")
        self.assertItemsEqual(expected, actual)
        actual = df.get_df_metrics(check_bundle["metrics"], "/root")
        self.assertItemsEqual(expected, actual)
        actual = df.get_df_metrics(check_bundle["metrics"], "/root/")
        self.assertItemsEqual(expected, actual)

        expected = [m for m in check_bundle["metrics"] if m["name"].startswith("df`")]
        expected = [m for m in expected if "`mnt-mysql`" in m["name"] and "`df_complex" in m["name"]]
        actual = df.get_df_metrics(check_bundle["metrics"], "mnt/mysql")
        self.assertEqual(3, len(actual))
        self.assertItemsEqual(expected, actual)
        actual = df.get_df_metrics(check_bundle["metrics"], "/mnt/mysql")
        self.assertItemsEqual(expected, actual)
        actual = df.get_df_metrics(check_bundle["metrics"], "/mnt/mysql/")
        self.assertItemsEqual(expected, actual)

        expected = [m for m in check_bundle["metrics"] if m["name"].startswith("df`")]
        expected = [m for m in expected if "`mnt-solr-home`" in m["name"]]
        actual = df.get_df_metrics(check_bundle["metrics"], "mnt/solr-home")
        self.assertItemsEqual(expected, actual)
        actual = df.get_df_metrics(check_bundle["metrics"], "/mnt/solr-home")
        self.assertItemsEqual(expected, actual)
        actual = df.get_df_metrics(check_bundle["metrics"], "/mnt/solr-home/")
        self.assertItemsEqual(expected, actual)

    def test_get_sorted_df_metrics(self):
        expected = [m for m in check_bundle["metrics"] if m["name"].startswith("df`")]
        expected = [m for m in expected if "`mnt-solr-home`" in m["name"]]
        actual = df.get_sorted_df_metrics(check_bundle["metrics"])
        self.assertEqual(3, len(actual))
        self.assertTrue(actual[0]["name"].endswith("reserved"))
        self.assertTrue(actual[1]["name"].endswith("used"))
        self.assertTrue(actual[2]["name"].endswith("free"))

    def test_get_df_datapoints(self):
        self.assertEqual([], df.get_datapoints(check_bundle, []))
        self.assertEqual([], df.get_datapoints({}, []))
        metrics = df.get_sorted_df_metrics(check_bundle["metrics"])
        datapoints = df.get_df_datapoints(check_bundle, metrics)
        self.assertIsInstance(datapoints, types.ListType)
        self.assertTrue(len(datapoints) > 0)
        for dp in datapoints:
            self.assertIn("derive", dp)
            self.assertEqual("gauge", dp["derive"])
            self.assertIn("stack", dp)

    def test_get_df_graph_data(self):
        self.assertEqual({}, df.get_df_graph_data({}, ""))

        mount_dir = "root"
        data = df.get_df_graph_data(check_bundle, mount_dir)
        self.assertIn("title", data)
        self.assertEqual("%s df %s" % (check_bundle["target"], mount_dir), data["title"])
        self.assertEqual(0, data["min_left_y"])
        self.assertEqual(0, data["min_right_y"])
        self.assertIn("datapoints", data)
        for dp in data["datapoints"]:
            self.assertEqual("gauge", dp["derive"])
            self.assertEqual(0, dp["stack"])

        mount_dir = "/mnt/solr-home"
        data = df.get_df_graph_data(check_bundle, mount_dir)
        self.assertIn("title", data)
        self.assertEqual("%s df %s" % (check_bundle["target"], mount_dir), data["title"])
        self.assertEqual(0, data["min_left_y"])
        self.assertEqual(0, data["min_right_y"])
        self.assertIn("datapoints", data)
        for dp in data["datapoints"]:
            self.assertEqual("gauge", dp["derive"])
            self.assertEqual(0, dp["stack"])

        title = "test title df"
        expected = "%s %s" % (title, mount_dir)
        data = df.get_df_graph_data(check_bundle, mount_dir, title)
        actual = data["title"]
        self.assertEqual(expected, actual)


class CollectdGraphTestCase(unittest.TestCase):

    def test_get_collectd_graph_data(self):
        data = get_collectd_graph_data({}, [], [])
        self.assertIsInstance(data, types.ListType)
        self.assertEqual([], data)

        data = get_collectd_graph_data(check_bundle, [], [])
        self.assertIsInstance(data, types.ListType)
        self.assertEqual(2, len(data))

        data = get_collectd_graph_data(check_bundle, ["eth0"], ["root"])
        self.assertIsInstance(data, types.ListType)
        self.assertEqual(4, len(data))
        for d in data:
            self.assertIn("title", d)

        titles = {"cpu": "cpu test", "memory": "memory test", "interface": "interface test", "df": "df test"}
        data = get_collectd_graph_data(check_bundle, ["eth0"], ["root"], titles)
        self.assertIsInstance(data, types.ListType)
        self.assertEqual(4, len(data))
        for d in data:
            self.assertIn("title", d)
            for dp in d["datapoints"]:
                if cpu.CPU_METRIC_RE.match(dp["name"]):
                    self.assertEqual(titles["cpu"], d["title"])
                elif memory.MEMORY_METRIC_RE.match(dp["name"]):
                    self.assertEqual(titles["memory"], d["title"])
                elif dp["name"].startswith("interface"):
                    self.assertEqual(titles["interface"] + " eth0 bit/s", d["title"])
                elif df.DF_METRIC_RE.match(dp["name"]):
                    self.assertEqual("%s root" % titles["df"], d["title"])


class GraphTestCase(unittest.TestCase):

    def test_get_graph_data(self):
        metrics = cpu.get_stacked_cpu_metrics(cpu.get_cpu_metrics(metric.get_metrics(check_bundle, cpu.CPU_METRIC_RE)))
        check_id = util.get_check_id_from_cid(check_bundle["_cid"])
        data = graph.get_graph_data(check_bundle, metric.get_datapoints(check_id, metrics))
        self.assertIn("tags", data)
        self.assertEqual(["telemetry:collectd"], data["tags"])
        self.assertIn("datapoints", data)
        self.assertIsInstance(data["datapoints"], types.ListType)

        custom_data = {"title": "%s cpu" % check_bundle["target"], "max_left_y": 100}
        data = graph.get_graph_data(check_bundle, metric.get_datapoints(check_id, metrics), custom_data)
        self.assertIn("title", data)
        self.assertEqual(custom_data["title"], data["title"])
        self.assertEqual(custom_data["max_left_y"], data["max_left_y"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
