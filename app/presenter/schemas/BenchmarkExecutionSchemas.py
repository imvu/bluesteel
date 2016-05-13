""" Benchmark Execution schemas """

# (duplicate-code)
# pylint: disable=R0801

SAVE_BENCHMARK_EXECUTION = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['command_set'],
    'properties' : {
        'command_set' : {
            'type' : 'array',
            'min' : 1,
            'items' : {
                'type' : 'object',
                'additionalProperties' : False,
                'required' : ['command', 'result'],
                'properties' : {
                    'command' : {
                        'type' : 'string',
                        'minLength' : 1,
                        'maxLength' : 255
                    },
                    'result' : {
                        'type' : 'object',
                        'additionalProperties' : False,
                        'required' : ['status', 'out', 'error'],
                        'properties' : {
                            'status' : {
                                'type' : 'number'
                            },
                            'out' : {
                                'type' : 'array',
                                'min' : 1,
                                'items' : {
                                    'type' : 'object',
                                    'oneOf' : [{
                                        'type' : 'object',
                                        'additionalProperties': False,
                                        'required': ['id', 'visual_type', 'data'],
                                        'properties' : {
                                            'visual_type' : {
                                                'type' : 'string',
                                                'enum' : ['text'],
                                            },
                                            'id' : {
                                                'type' : 'string',
                                                'minLength' : 1,
                                                'maxLength' : 32,
                                            },
                                            'data' : {
                                                'type' : 'string',
                                                'minLength' : 1,
                                            },
                                        },
                                    }, {
                                        'type' : 'object',
                                        'additionalProperties': False,
                                        'required': ['id', 'visual_type', 'data'],
                                        'properties' : {
                                            'visual_type' : {
                                                'type' : 'string',
                                                'enum' : ['unknown'],
                                            },
                                            'id' : {
                                                'type' : 'string',
                                                'minLength' : 1,
                                                'maxLength' : 32,
                                            },
                                            'data' : {
                                                'type' : 'string',
                                                'minLength' : 1,
                                            },
                                        },
                                    }, {
                                        'type' : 'object',
                                        'additionalProperties': False,
                                        'required': ['id', 'visual_type', 'data'],
                                        'properties' : {
                                            'visual_type' : {
                                                'type' : 'string',
                                                'enum' : ['vertical_bars'],
                                            },
                                            'id' : {
                                                'type' : 'string',
                                                'minLength' : 1,
                                                'maxLength' : 32,
                                            },
                                            'data' : {
                                                'type' : 'array',
                                                'min' : 1,
                                                'items' : {
                                                    'type' : 'number'
                                                },
                                            },
                                        },
                                    }]
                                }
                            },
                            'error' : {
                                'type' : 'string',
                            },
                            'start_time' : {
                                'format' : 'date-time',
                                'type' : 'string',
                            },
                            'finish_time' : {
                                'type' : 'string',
                                'format' : 'date-time',
                            },
                        },
                    },
                },
            },
        },
    },
}
