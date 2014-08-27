from twisted.trial import unittest
from twisted.internet import defer

import txwarmongo


class TestFinding(unittest.TestCase):
    @defer.inlineCallbacks
    def tearDown(self):
        # need to connect + disconnect each time due to twisted weirdness
        yield txwarmongo.disconnect()

    @defer.inlineCallbacks
    def setUp(self):
        self.schema = {
            'name': 'Country',
            'properties': {
                'name': {'type': 'string'},
                'abbreviation': {'type': 'string'},
                'languages': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                }
            },
            'additionalProperties': False,
        }

        # Connect to txwarmongo_test - hopefully it doesn't exist
        yield txwarmongo.connect("txwarmongo_test")
        self.Country = txwarmongo.model_factory(self.schema)

        # Drop all the data in it
        yield self.Country.collection().remove({})

        # Create some defaults
        sweden = self.Country({
            "name": "Sweden",
            "abbreviation": "SE",
            "languages": ["swedish"]
        })
        yield sweden.save()
        usa = self.Country({
            "name": "United States of America",
            "abbreviation": "US",
            "languages": ["english"]
        })
        yield usa.save()

    @defer.inlineCallbacks
    def testFindOne(self):
        ''' Test grabbing a single value the Mongo way '''

        usa = yield self.Country.find_one({"abbreviation": "US"})

        self.assertIsNotNone(usa)
        self.assertEqual("United States of America", usa.name)

    @defer.inlineCallbacks
    def testFind(self):
        ''' Just grab a bunch of stuff '''

        countries = yield self.Country.find()

        # Since find() returns a generator, need to convert to list
        countries = [c for c in countries]

        self.assertEqual(2, len(countries))

    @defer.inlineCallbacks
    def testCount(self):
        ''' See if everything is there '''
        count = yield self.Country.count()
        self.assertEqual(2, count)
        count = yield self.Country.count({"abbreviation": "SE"})
        self.assertEqual(1, count)
        count = yield self.Country.count({"abbreviation": "CA"})
        self.assertEqual(0, count)

    @defer.inlineCallbacks
    def testFindAll(self):
        ''' Test fetching everything the mongo way '''

        countries = yield self.Country.find({"abbreviation": "SE"})

        self.assertEqual(1, len(countries))
        self.assertEqual("Sweden", countries[0].name)
