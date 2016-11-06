""" Benchmark Definition schemas """

# (duplicate-code)
# pylint: disable=R0801

SAVE_BENCHMARK_DEFINITION = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': [
        'name',
        'layout_id',
        'project_id',
        'active',
        'command_list',
        'max_fluctuation_percent',
        'overrides',
        'max_weeks_old_notify',
        'work_passes'
    ],
    'properties' : {
        'name' : {
            'type' : 'string',
            'maxLength' : 128,
            'minLength' : 1,
        },
        'layout_id' : {
            'type' : 'number',
            'minimum' : 1,
        },
        'project_id' : {
            'type' : 'number',
            'minimum' : 1,
        },
        'active' : {
            'type' : 'boolean',
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
            'minimum' : 0,
            'maximum' : 100,
        },
        'overrides' : {
            'type' : 'array',
            'items' : {
                'type' : 'object',
                'additionalProperties' : False,
                'required': ['result_id', 'override_value'],
                'properties' : {
                    'result_id' : {
                        'type' : 'string',
                        'minLength' : 1,
                        'maxLength' : 255,
                    },
                    'override_value' : {
                        'type' : 'number',
                        'minimum' : 0,
                        'maximum' : 100,
                    },
                }
            }
        },
        'max_weeks_old_notify' : {
            'type' : 'integer',
            'oneOf' : [
                {"type" : "integer", "minimum" : -1, "maximum" : -1},
                {"type" : "number", "minimum" : 0, "maximum" : 0},
                {"type" : "number", "minimum" : 1, "maximum" : 1},
                {"type" : "number", "minimum" : 2, "maximum" : 2},
                {"type" : "number", "minimum" : 3, "maximum" : 3},
                {"type" : "number", "minimum" : 4, "maximum" : 4},
                {"type" : "number", "minimum" : 8, "maximum" : 8},
                {"type" : "number", "minimum" : 12, "maximum" : 12},
                {"type" : "number", "minimum" : 16, "maximum" : 16},
                {"type" : "number", "minimum" : 20, "maximum" : 20},
                {"type" : "number", "minimum" : 24, "maximum" : 24},
                {"type" : "number", "minimum" : 52, "maximum" : 52},
                {"type" : "number", "minimum" : 104, "maximum" : 104},
                {"type" : "number", "minimum" : 156, "maximum" : 156},
                {"type" : "number", "minimum" : 208, "maximum" : 208},
                {"type" : "number", "minimum" : 260, "maximum" : 260},
                {"type" : "number", "minimum" : 520, "maximum" : 520},
            ],
        },
        'work_passes' : {
            'type' : 'array',
            'items' : {
                'type' : 'object',
                'additionalProperties' : False,
                'required' : ['id', 'allowed'],
                'properties' : {
                    'id' : {
                        'type' : 'number',
                        'minimum' : 1
                    },
                    'allowed' : {
                        'type' : 'boolean'
                    },
                },
            }
        },
    },
}
