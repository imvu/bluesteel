""" Bluesteel schemas """

# Anomalous backslash in string: '\.'. String constant might be missing an r prefix.
# pylint: disable=W1401

# (duplicate-code)
# pylint: disable=R0801

SAVE_LAYOUT = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['name', 'active', 'project_index_path'],
    'properties' : {
        'name' : {
            'type' : 'string',
            'pattern' : '^[^\\/?%*:|"<>\.]+$',
            'minLength' : 1,
            'maxLength' : 50,
        },
        'active' : {
            'type': 'boolean',
        },
        'project_index_path' : {
            'type': 'number',
            'minimum': 0,
            'maximum': 100,
        },
    },
}

SAVE_PROJECT = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['name', 'clone', 'fetch', 'pull'],
    'properties' : {
        'name' : {
            'type' : 'string',
            'pattern' : '^[^\\/?%*:|"<>\.]+$',
            'minLength' : 1,
            'maxLength' : 50,
        },
        'clone' : {
            'type' : 'array',
            'minItems' : 1,
            'items' : {
                'minLength' : 1,
                'type' : 'string',
                'maxLength' : 255,
            },
        },
        'fetch' : {
            'type' : 'array',
            'minItems' : 1,
            'items' : {
                'type' : 'string',
                'minLength' : 1,
                'maxLength' : 255,
            },
        },
        'pull' : {
            'type' : 'array',
            'minItems' : 1,
            'items' : {
                'minLength' : 1,
                'maxLength' : 255,
                'type' : 'string',
            },
        },
    },
}
