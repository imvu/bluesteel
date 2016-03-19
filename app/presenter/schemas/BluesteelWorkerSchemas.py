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
    'required': ['description', 'git_feeder'],
    'properties' : {
        'description' : {
            'type' : 'string',
            'minLength' : 1,
        },
        'git_feeder' : {
            'type': 'boolean',
        },
    },
}
