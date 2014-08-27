# Copyright 2014 Rob Britton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from twisted.internet import defer
from txmongo._pymongo.objectid import ObjectId  # needed for validation

from warmongo.model import ModelBase
from warmongo.exceptions import ValidationError, InvalidReloadException

import database


class TwistedModel(ModelBase):
    @classmethod
    def collection(cls):
        ''' Get the pymongo collection object for this model. Useful for
        features not supported by Warmongo like aggregate queries and
        map-reduce. '''
        return database.get_collection(collection=cls.collection_name(),
                                       database=cls.database_name())

    @defer.inlineCallbacks
    def save(self, *args, **kwargs):
        ''' Saves an object to the database. '''
        self.validate()
        self._id = yield self.collection().save(self._fields, *args, **kwargs)

    @defer.inlineCallbacks
    def delete(self):
        if self._id:
            yield self.collection().remove({"_id": ObjectId(str(self._id))})

    @defer.inlineCallbacks
    def reload(self):
        ''' Reload this object's data from the DB. '''
        result = yield self.__class__.find_by_id(self._id)

        # result will be None in the case that this object hasn't yet been
        # saved to the DB, or if the object has been deleted since it was
        # fetched
        if result:
            self._fields = self.cast(result._fields)
        else:
            raise InvalidReloadException("No object in the database with ID %s" % self._id)

    @classmethod
    @defer.inlineCallbacks
    def find_or_create(cls, query, *args, **kwargs):
        ''' Retrieve an element from the database. If it doesn't exist, create
        it.  Calling this method is equivalent to calling find_one and then
        creating an object. Note that this method is not atomic.  '''
        result = yield cls.find_one(query, *args, **kwargs)

        if result is None:
            default = cls._schema.get("default", {})
            default.update(query)

            result = cls(default, *args, **kwargs)

        defer.returnValue(result)

    @classmethod
    def bulk_create(cls, objects, *args, **kwargs):
        docs = [obj._fields for obj in objects]
        return cls.collection().insert(docs)

    @classmethod
    def find_by_id(cls, id, **kwargs):
        ''' Finds a single object from this collection. '''
        if isinstance(id, basestring):
            id = ObjectId(id)

        return cls.find_one({"_id": id})

    @classmethod
    @defer.inlineCallbacks
    def find_latest(cls, *args, **kwargs):
        kwargs["limit"] = 1
        kwargs["sort"] = [("_id", DESCENDING)]

        result = yield cls.collection().find(*args, **kwargs)

        if len(result) > 0:
            defer.returnValue(cls(result[0], from_find=True))
        defer.returnValue(None)

    @classmethod
    @defer.inlineCallbacks
    def update(cls, *args, **kwargs):
        ''' Do an update query. Uses pymongo's arguments. '''
        yield cls.collection().update(*args, **kwargs)

    @classmethod
    @defer.inlineCallbacks
    def remove(cls, *args, **kwargs):
        ''' Do a remove query. Uses pymongo's arguments. '''
        yield cls.collection().remove(*args, **kwargs)

    @classmethod
    @defer.inlineCallbacks
    def find_one(cls, *args, **kwargs):
        result = yield cls.collection().find_one(*args, **kwargs)
        if result is not None:
            defer.returnValue(cls(result, from_find=True))
        defer.returnValue(None)

    @classmethod
    @defer.inlineCallbacks
    def find(cls, *args, **kwargs):
        elems = yield cls.collection().find(*args, **kwargs)
        defer.returnValue([cls(elem, from_find=True) for elem in elems])

    @classmethod
    def count(cls, *args, **kwargs):
        return cls.collection().count(*args, **kwargs)

    def validate_simple(self, key, value_type, value):
        ''' Validate a simple field (not an object or array) against a schema. '''
        if value_type == "object_id":
            # can be anything
            if not isinstance(value, ObjectId):
                raise ValidationError("Field '%s' is of type '%s', received '%s' (%s)" %
                                      (key, value_type, str(value), type(value)))
        else:
            ModelBase.validate_simple(self, key, value_type, value)
