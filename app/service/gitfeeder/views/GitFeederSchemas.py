""" Git Feeder Schema """

GIT_FEEDER_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties' : True,
    'required' : ['reports'],
    'properties' : {
        'feed_data' : {
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
                        'required': ['hash', 'parent_hashes', 'author', 'committer'],
                        'properties' : {
                            'hash' : {
                                'type' : 'string',
                                'pattern': '^[0-9a-f]{40}$'
                            },
                            'parent_hashes' : {
                                'type' : 'array',
                                'items' : {
                                    'type' : 'string',
                                    'pattern': '(^[0-9a-f]{40}$)|(^$)'
                                }
                            },
                            'author' : {
                                'type' : 'object',
                                'additionalProperties': False,
                                'required': ['name', 'email', 'date'],
                                'properties' : {
                                    'name' : {
                                        'minLength' : 1,
                                        'maxLength' : 50,
                                    },
                                    'email' : {
                                        'type' : 'string',
                                        'format' : 'email'
                                    },
                                    'date' : {
                                        'type' : 'string',
                                        'format' : 'date-time'
                                    },
                                }
                            },
                            'committer' : {
                                'type' : 'object',
                                'additionalProperties': False,
                                'required': ['name', 'email', 'date'],
                                'properties' : {
                                    'name' : {
                                        'minLength' : 1,
                                        'maxLength' : 50,
                                    },
                                    'email' : {
                                        'type' : 'string',
                                        'format' : 'email'
                                    },
                                    'date' : {
                                        'type' : 'string',
                                        'format' : 'date-time'
                                    },
                                }
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
                        'required': ['commit_hash', 'branch_name', 'trail', 'merge_target'],
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
                            },
                            'merge_target' : {
                                'type' : 'object',
                                'additionalProperties': False,
                                'required': ['name', 'hash', 'diff', 'fork_point'],
                                'properties' : {
                                    'name' : {
                                        'type' : 'string',
                                        'minLength' : 1
                                    },
                                    'hash' : {
                                        'type' : 'string',
                                        'pattern': '^[0-9a-f]{40}$'
                                    },
                                    'fork_point' : {
                                        'type' : 'string',
                                        'pattern': '^[0-9a-f]{40}$'
                                    },
                                    'diff' : {
                                        'type' : 'object',
                                        'additionalProperties': False,
                                        'required': ['commit_hash_son', 'commit_hash_parent', 'content'],
                                        'properties' : {
                                            'commit_hash_son' : {
                                                'type' : 'string',
                                                'pattern': '^[0-9a-f]{40}$'
                                            },
                                            'commit_hash_parent' : {
                                                'type' : 'string',
                                                'pattern': '^[0-9a-f]{40}$'
                                            },
                                            'content' : {
                                                'type' : 'string',
                                            },
                                        }
                                    },

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
                        'required': ['commit_hash_son', 'commit_hash_parent', 'content'],
                        'properties' : {
                            'commit_hash_son' : {
                                'type' : 'string',
                                'pattern': '^[0-9a-f]{40}$'
                            },
                            'commit_hash_parent' : {
                                'type' : 'string',
                                'pattern': '^[0-9a-f]{40}$'
                            },
                            'content' : {
                                'type' : 'string',
                            },
                        }
                    }
                },
            },
        },
        'reports' : {
            'type' : 'array',
            'minItems' : 1,
            'items' : {
                'type' : 'object',
                'additionalProperties' : False,
                'required' : ['commands'],
                'properties' : {
                    'commands' : {
                        'type' : 'array',
                        'minItems' : 1,
                        'items' : {
                            'type' : 'object',
                            'additionalProperties' : False,
                            'required' : ['command', 'out', 'error', 'status'],
                            'properties' : {
                                'command' : {
                                    'type' : 'array',
                                    'items' : {
                                        'type' : 'string'
                                    }
                                },
                                'out' : {
                                    'type' : 'string'
                                },
                                'error' : {
                                    'type' : 'string'
                                },
                                'status' : {
                                    'type' : 'string',
                                    'enum' : ['OK', 'ERROR']
                                }
                            }
                        },
                    },
                }
            }
        }
    }
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