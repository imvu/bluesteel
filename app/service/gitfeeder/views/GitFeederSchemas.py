""" Git Feeder Schema """

GIT_FEEDER_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['commits', 'branches', 'diffs'],
    'properties' : {
        'commits' : {
            'type' : 'array',
            'minItems' : 1,
            'items' : {
                'type' : 'object',
                'additionalProperties': False,
                'required': ['commit_hash', 'commit_parents', 'user', 'date_creation', 'date_commit'],
                'properties' : {
                    'commit_hash' : {
                        'type' : 'string',
                        'pattern': '^[0-9a-f]{40}$'
                    },
                    'commit_parents' : {
                        'type' : 'array',
                        'items' : {
                            'type' : 'string',
                            'pattern': '^[0-9a-f]{40}$'
                        }
                    },
                    'user' : {
                        'type' : 'object',
                        'additionalProperties': False,
                        'required': ['name', 'email'],
                        'properties' : {
                            'name' : {
                                'minLength' : 1,
                                'maxLength' : 50,
                            },
                            'email' : {
                                'type' : 'string',
                                'format' : 'email'
                            },
                        }
                    },
                    'date_creation' : {
                        'type' : 'string',
                        'format' : 'date-time'
                    },
                    'date_commit' : {
                        'type' : 'string',
                        'format' : 'date-time'
                    },
                }
            }
        },
        'branches' : {
            'type' : 'array',
            'minItems' : 1,
            'items' : {
                'type' : 'object',
                'additionalProperties': False,
                'required': ['commit_hash', 'branch_name'],
                'properties' : {
                    'commit_hash' : {
                        'type' : 'string',
                        'pattern': '^[0-9a-f]{40}$'
                    },
                    'branch_name' : {
                        'type' : 'string',
                        'items' : {
                            'type' : 'string',
                            'minLength' : 1
                        }
                    },
                    'trail' : {
                        'type' : 'array',
                        'minItems' : 1,
                        'items' : {
                            'type' : 'string',
                            'pattern': '^[0-9a-f]{40}$'
                        }
                    }
                }
            }
        },
        'diffs' : {
            'type' : 'array',
            'items' : {
                'type' : 'object',
                'additionalProperties': False,
                'required': ['commit_hash_son', 'commit_hash_parent', 'diff'],
                'properties' : {
                    'commit_hash_son' : {
                        'type' : 'string',
                        'pattern': '^[0-9a-f]{40}$'
                    },
                    'commit_hash_parent' : {
                        'type' : 'string',
                        'pattern': '^[0-9a-f]{40}$'
                    },
                    'diff' : {
                        'type' : 'string',
                    },
                }
            }
        },
    },
}

# 'project' : {
#     'type' : 'object',
#     'additionalProperties': False,
#     'required': ['url'],
#     'properties' : {
#         'url' : {
#             'type' : 'string',
#             'format': 'uri'
#         },
#     }
# },
