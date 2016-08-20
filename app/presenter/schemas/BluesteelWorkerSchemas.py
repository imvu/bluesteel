""" Worker schemas """

# (duplicate-code)
# pylint: disable=R0801

CREATE_WORKER_INFO_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['uuid', 'operative_system', 'host_name'],
    'properties' : {
        'uuid' : {
            'type' : 'string',
            'pattern': '(^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$)'
        },
        'operative_system' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 64,
        },
        'host_name' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 64,
        },
    },
}

LOGIN_WORKER_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['username', 'password'],
    'properties' : {
        'username' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 30,
        },
        'password' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 64,
        },
    },
}

SAVE_WORKER_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['description', 'git_feeder', 'max_feed_reports'],
    'properties' : {
        'description' : {
            'type' : 'string',
            'minLength' : 1,
        },
        'git_feeder' : {
            'type': 'boolean',
        },
        'max_feed_reports' : {
            'type' : 'integer',
            'oneOf' : [
                {"type" : "integer", "minimum" : -1, "maximum" : -1},
                {"type" : "number", "minimum" : 1, "maximum" : 1},
                {"type" : "number", "minimum" : 5, "maximum" : 5},
                {"type" : "number", "minimum" : 10, "maximum" : 10},
                {"type" : "number", "minimum" : 20, "maximum" : 20},
                {"type" : "number", "minimum" : 30, "maximum" : 30},
                {"type" : "number", "minimum" : 40, "maximum" : 40},
                {"type" : "number", "minimum" : 50, "maximum" : 50},
                {"type" : "number", "minimum" : 100, "maximum" : 100},
            ],
        },
    },
}
