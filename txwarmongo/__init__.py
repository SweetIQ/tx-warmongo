import warmongo

import database
import twisted_model

connect = database.connect
disconnect = database.disconnect


def model_factory(schema, base_class=twisted_model.TwistedModel):
    return warmongo.model_factory(schema, base_class)
