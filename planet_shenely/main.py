#!/usr/bin/env python2.7

"""Planet Shenely

Manages a database of users and groups via a REST API.
"""

__author__ = "shenely"
__version__ = "0.1"

## Imports ##
#Built-in
import types
import json

#External
from flask import Flask, g, request, abort
app = Flask(__name__)#get init out of the way

## Exports ##
__all__ = ["app"]

## Constants ##
USER_SCHEMA = set(["first_name",
                   "last_name",
                   "userid",
                   "groups"])


class RestWrapper(object):
    """Wrapper for RESTful API
    
    Combines several functions describing how to response to various
    HTTP request and wraps them with some necessary setup and teardown 
    code. Documention from each function is also combined to describe
    the full REST API.
    
    Arguments:
    func -- function to respond to HTTP GET
    
    Methods:
    get    -- how to respond to HTTP GET
    post   --  "  "    "     "  HTTP POST
    delete --  "  "    "     "  HTTP DELETE
    put    --  "  "    "     "  HTTP PUT
    
    Properties:
    getter  -- HTTP GET function
    poster  -- HTTP POST function
    deleter -- HTTP DELETE function
    putter  -- HTTP PUT function
    """
    
    def __init__(self,func):
        self.get(func)
        self.poster = self.empty
        self.deleter = self.empty
        self.putter = self.empty
        
        #XXX: Flask needs this to work
        self.__name__ = func.__name__
        
    @property
    def __doc__(self):
        return "\n".join([self.getter.__doc__,
                          self.poster.__doc__,
                          self.deleter.__doc__,
                          self.putter.__doc__])
        
    def __call__(self,*args,**kwargs):
        """Handle incoming request"""
        with open(app.config["DATABASE"],"r") as fin:
            data = json.load(fin)
            
        g.users = data["users"]
        g.groups = data["groups"]
        
        if request.method == "GET":
            return self.getter(*args,**kwargs)
        elif request.method == "POST":
            self.poster(*args,**kwargs)
            
            code = 201#Created
        elif request.method == "DELETE":
            self.deleter(*args,**kwargs)
            
            code = 200#OK
        elif request.method == "PUT":
            self.putter(*args,**kwargs)
            
            code = 202#Accepted
        
        with open(app.config["DATABASE"],"w") as fout:
            json.dump(data,fout)
        
        return ("", code)
    
    def empty(self,*args,**kwargs):pass
        
    def get(self,func):
        """Get decorator"""
        self.getter = func
        
        return self
    
    def post(self,func):
        """Post decorator"""
        self.poster = func
        
        return self
    
    def put(self,func):
        """Put decorator"""
        self.putter = func
        
        return self
    
    def delete(self,func):
        """Delete decorator"""
        self.deleter = func
        
        return self

@app.route("/users", methods=["POST"])
@app.route("/users/<userid>", methods=["GET", "DELETE", "PUT"])
@RestWrapper
def users(userid):
    """Manage user records
    
    GET /users/<userid>
    Returns the matching user record or 404 if none exist.
    """
    #Does user exist?
    users = [user for user in g.users \
             if user["userid"] == userid]
    
    #User must exist
    if len(users) > 0:
        user = users[0]
        
        return json.dumps(user)
    else:
        abort(404)#Not Found
        
@users.post
def users():
    """
    POST /users
    Creates a new user record. The body of the request should be a valid user
    record. POSTs to an existing user should be treated as errors and flagged
    with the appropriate HTTP status code.
    """
    user = request.json#application/json
    
    #XXX: User must follow a schema
    if set(user.keys()) != USER_SCHEMA or \
       not isinstance(user["groups"],types.ListType):
        abort(400)#Bad Request
    
    #Do groups exists?
    groups = [group for group in user["groups"] \
              if group not in g.groups]
        
    #Does user exist?
    users = [u for u in g.users \
             if u["userid"] == user["userid"]]
    
    #Groups must exist and user must not exist
    if len(users) == 0:
        if len(groups) == 0:
            g.users.append(user)
        else:
            abort(404)#Not Found
    else:
        abort(409)#Conflict
        
@users.delete
def users(userid):
    """
    DELETE /users/<userid>
    Deletes a user record. Returns 404 if the user doesn't exist.
    """
    #At which index is this user?
    indices = [i for i,user in enumerate(g.users) \
               if user["userid"] == userid]
    
    #User must exist
    if len(indices) > 0:
        i = indices[0]
        
        del g.users[i]
    else:
        abort(404)#Not Found
        
@users.put
def users(userid):
    """
    PUT /users/<userid>
    Updates an existing user record. The body of the request should be a valid
    user record. PUTs to a non-existant user should return a 404.
    """
    user = request.json#application/json
    
    #XXX: Probably not Pythonic, but it salves my conscience
    if set(user.keys()) != USER_SCHEMA or \
       not isinstance(user["groups"],types.ListType):
        abort(400)#Bad Request
        
    #Do groups exists?
    groups = [group for group in user["groups"] \
              if group not in g.groups]
    
    #Does user exist?
    indices = [i for i,u in enumerate(g.users) \
               if u["userid"] == userid]
        
    #Groups must exist and user must exist
    if len(indices) > 0:
        if len(groups) == 0:
            i = indices[0]
            g.users[i] = user
        else:
            abort(404)#Not Found
    else:
        abort(404)#Not Found

@app.route("/groups", methods=["POST"])
@app.route("/groups/<name>", methods=["GET", "DELETE", "PUT"])
@RestWrapper
def groups(name):
    """Manage group records
    
    GET /groups/<group name>
    Returns a JSON list of userids containing the members of that group. Should
    return a 404 if the group doesn't exist.
    """
    #Group must exist
    if name in g.groups:
        #There doesn't have to be anyone in the group
        userids = [user["userid"] for user in g.users \
                   if name in user["groups"]]
        
        return json.dumps(userids)
    else:
        abort(404)#Not Found

@groups.post
def groups():
    """
    POST /groups
    Creates a empty group. POSTs to an existing group should be treated as
    errors and flagged with the appropriate HTTP status code. The body should contain
    a `name` parameter
    """
    #Was a name given?
    if "name" in request.form:
        name = request.form["name"]
    else:
        abort(400)#Bad Request
        
    #Group must not exist
    if name not in g.groups:
        g.groups.append(name)
    else:
        abort(409)#Conflict

@groups.put
def groups(name):
    """
    PUT /groups/<group name>
    Updates the membership list for the group. The body of the request should 
    be a JSON list describing the group's members.
    """
    #Group must exist
    if name in g.groups:
        userids = request.json#application/json
        
        #XXX: Definitely not duck typing
        if isinstance(userids,types.ListType):
            if len(userids) > 0:
                #Users must exist
                users = [user for user in g.users \
                         if user["userid"] in userids]
            else:
                abort(404)#Not Found
        else:
            abort(400)#Bad Request
            
        #Users must exist
        if len(users) > 0:
            for user in users:
                if name not in user["groups"]:
                    user["groups"].append(name)
        else:
            abort(400)#Bad Request
    else:
        abort(404)#Not Found

@groups.delete
def groups(name):
    """
    DELETE /groups/<group name>
    Deletes a group.
    """
    try:
        #Group must exist
        g.groups.remove(name)
        
        #No user can be in the group anymore
        for user in g.users:
            if name in user["groups"]:
                user["groups"].remove(name)
    except ValueError:
        abort(404)#Not Found