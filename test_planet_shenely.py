#!/usr/bin/env python2.7

"""Behavior factory

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   24 July 2015

TBD.

Classes:
BehaviorFactory -- TBD
"""

import os
import json
import unittest
import tempfile

import planet_shenely

JSON_HASH = {
    "users": [
        {
            "first_name": "Joe",
            "last_name": "Smith",
            "userid": "jsmith",
            "groups": ["admins", "users"]
        }
    ],
    "groups": [ "admins", "users" ]
}

jsmith = {
    "first_name": "Joe",
    "last_name": "Smith",
    "userid": "jsmith",
    "groups": ["admins", "users"]
}

jdoe = {
    "first_name": "John",
    "last_name": "Doe",
    "userid": "jdoe",
    "groups": ["admins", "users"]
}

shenely = {
    "first_name": "Sean",
    "last_name": "Henely",
    "userid": "shenely",
    "groups": ["users"]
}

armstrong = {
    "first_name": "Neil",
    "middle_name": "Alden",
    "last_name": "Armstrong",
    "userid": "armstrong",
    "groups": ["admins","users"]
}

buzz = {
    "first_name": "Michael",
    "last_name": "",
    "userid": "shenely",
    "groups": "users"
}

mcollins = {
    "first_name": "Michael",
    "last_name": "Collins",
    "userid": "mcollins",
    "groups": ["users","moon"]
}

admins = [ "jsmith" ]

class RestTestCase(unittest.TestCase):

    def setUp(self):
        self.temp, planet_shenely.app.config["DATABASE"] = tempfile.mkstemp()
        self.app = planet_shenely.app.test_client()
        
        with os.fdopen(self.temp,"w") as fin:
            json.dump(JSON_HASH,fin)

    def tearDown(self):
        os.unlink(planet_shenely.app.config["DATABASE"])

class UserGetTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.get("/users/jsmith")
        
        assert rv.status_code == 200
        assert json.loads(rv.data) == jsmith

    def test_no_userid(self):
        rv = self.app.get("/users")
        
        assert rv.status_code == 405

    def test_bad_userid(self):
        rv = self.app.get("/users/shenely")
        
        assert rv.status_code == 404

class UserPostTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.post("/users",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(shenely))
        
        assert rv.status_code == 201
        
        rv = self.app.get("/users/shenely")
        
        assert rv.status_code == 200
        assert json.loads(rv.data) == shenely

    def test_bad_repeat(self):
        rv = self.app.post("/users",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(jsmith))
        
        assert rv.status_code == 409

    def test_bad_data(self):
        rv = self.app.post("/users",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(armstrong))
        
        assert rv.status_code == 400

    def test_bad_group(self):
        rv = self.app.post("/users",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(buzz))
        
        assert rv.status_code == 400

    def test_fake_group(self):
        rv = self.app.post("/users",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(mcollins))
        
        assert rv.status_code == 404

class UserDeleteTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.delete("/users/jsmith")
        
        assert rv.status_code == 200

    def test_no_userid(self):
        rv = self.app.delete("/users")
        
        assert rv.status_code == 405

    def test_bad_userid(self):
        rv = self.app.delete("/users/shenely")
        
        assert rv.status_code == 404

class UserPutTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.put("/users/jsmith",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps(jdoe))
        
        assert rv.status_code == 202
        
        rv = self.app.get("/users/jdoe")
        
        assert rv.status_code == 200
        assert json.loads(rv.data) == jdoe

    def test_no_userid(self):
        rv = self.app.put("/users",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps(shenely))
        
        assert rv.status_code == 405

    def test_bad_userid(self):
        rv = self.app.put("/users/shenely",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps(shenely))
        
        assert rv.status_code == 404

    def test_bad_data(self):
        rv = self.app.post("/users",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(shenely))
        
        rv = self.app.put("/users/shenely",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps(armstrong))
        
        assert rv.status_code == 400

    def test_bad_group(self):
        rv = self.app.post("/users",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(shenely))
        
        rv = self.app.put("/users/shenely",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps(buzz))
        
        assert rv.status_code == 400

    def test_fake_group(self):
        rv = self.app.post("/users/shenely",
                           headers=[("Content-Type","application/json")],
                           data=json.dumps(shenely))
        
        rv = self.app.put("/users/shenely",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps(mcollins))
        
        assert rv.status_code == 404

class GroupGetTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.get('/groups/admins')
        
        assert rv.status_code == 200
        assert json.loads(rv.data) == admins
        
    def test_no_name(self):
        rv = self.app.get('/groups')
        
        assert rv.status_code == 405

    def test_bad_name(self):
        rv = self.app.get('/groups/sudoers')

class GroupPostTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.post("/groups",
                           data={ "name": "moon" })
        
        assert rv.status_code == 201
        
        rv = self.app.get("/groups/moon")
        
        assert rv.status_code == 200
        assert json.loads(rv.data) == []

    def test_bad_repeat(self):
        rv = self.app.post("/groups",
                           data={ "name": "users" })
        
        assert rv.status_code == 409

    def test_bad_data(self):
        rv = self.app.post("/groups",
                           data={ "planet": "moon" })
        
        assert rv.status_code == 400

class GroupDeleteTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.delete("/groups/admins")
        
        assert rv.status_code == 200
        
        rv = self.app.get("/users/jsmith")
        user = json.loads(rv.data)
        
        assert "admins" not in user["groups"]

    def test_no_name(self):
        rv = self.app.delete("/groups")
        
        assert rv.status_code == 405

    def test_bad_name(self):
        rv = self.app.delete("/groups/moon")
        
        assert rv.status_code == 404

class GroupPutTestCase(RestTestCase):

    def test_good(self):
        rv = self.app.post("/groups",
                          data={ "name": "moon" })
        
        rv = self.app.put("/groups/moon",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps([ "jsmith" ]))
        
        assert rv.status_code == 202
        
        rv = self.app.get("/users/jsmith")
        user = json.loads(rv.data)
        
        assert "moon" in user["groups"]

    def test_no_name(self):
        rv = self.app.post("/groups",
                           data={ "name": "moon" })
        
        rv = self.app.put("/groups",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps([ "jsmith" ]))
        
        assert rv.status_code == 405

    def test_bad_name(self):
        rv = self.app.put("/groups/sudoers",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps([ "jsmith" ]))
        
        assert rv.status_code == 404

    def test_bad_userid(self):
        rv = self.app.put("/groups/users",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps([ "shenely" ]))
        
        assert rv.status_code == 400

    def test_bad_data(self):
        rv = self.app.post("/groups",
                           data={ "name": "moon" })
        
        rv = self.app.put("/groups/users",
                          headers=[("Content-Type","application/json")],
                          data=json.dumps("jsmith"))
        
        assert rv.status_code == 400


if __name__ == '__main__':
    unittest.main()