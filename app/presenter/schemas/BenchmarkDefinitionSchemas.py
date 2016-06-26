""" Benchmark Definition schemas """

# (duplicate-code)
# pylint: disable=R0801

SAVE_BENCHMARK_DEFINITION = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['name', 'layout_id', 'project_id', 'command_list'],
    'properties' : {
        'name' : {
            'type' : 'string',
            'maxLength' : 128,
            'minLength' : 1,
        },
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
                'maxLength' : 255,
                'minLength' : 1,
            },
        },
        'max_fluctuation_percent' : {
            'type' : 'number',
            'min' : 0,
            'max' : 100,
        },
    },
}
