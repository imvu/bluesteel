""" Bluesteel schemas """

SAVE_LAYOUT = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['name', 'collect_commits_path'],
    'properties' : {
        'name' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 50,
        },
        'collect_commits_path' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 255,
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
            'minLength' : 1,
            'maxLength' : 50,
        },
        'clone' : {
            'type' : 'array',
            'minItems' : 1,
            'items' : {
                'type' : 'string',
                'minLength' : 1,
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
                'type' : 'string',
                'minLength' : 1,
                'maxLength' : 255,
            },
        },
    },
}
