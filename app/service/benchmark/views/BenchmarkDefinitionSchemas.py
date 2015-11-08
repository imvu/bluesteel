""" Benchmark Definition schemas """

SAVE_BENCHMARK_DEFINITION = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['layout_id', 'project_id', 'command_list'],
    'properties' : {
        'layout_id' : {
            'type' : 'number',
            'min' : 1,
        },
        'project_id' : {
            'type' : 'number',
            'min' : 1,
        },
        'command_list' : {
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
