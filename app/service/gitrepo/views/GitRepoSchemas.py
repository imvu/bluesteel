""" Git Repo Schemas """

# 1.- They can include slash / for hierarchical (directory) grouping, but no slash-separated component can
#     begin with a dot . or end with the sequence .lock.
#   must not contain /.
#       (?!.*/\.)
#   must not end with .lock
#       (?<!\.lock)$

# 2.- They must contain at least one /. This enforces the presence of a category like heads/, tags/ etc.
#     but the actual names are not restricted. If the --allow-onelevel option is used, this rule is waived.
#       .+/.+  # may get more precise later

# 3.- They cannot have two consecutive dots .. anywhere.
#       (?!.*\.\.)

# 4.- They cannot have ASCII control characters (i.e. bytes whose values are lower than \040, or \177 DEL),
#     space, tilde ~, caret ^, or colon : anywhere.
#       [^\040\177 ~^:]+   # pattern for allowed characters

# 5.- They cannot have question-mark ?, asterisk *, or open bracket [ anywhere. See the --refspec-pattern
#     option below for an exception to this rule.
#       [^\040\177 ~^:?*[]+   # new pattern for allowed characters

# 6.- They cannot begin or end with a slash / or contain multiple consecutive slashes
#     (see the --normalize option below for an exception to this rule)
#       ^(?!/)
#       (?<!/)$
#       (?!.*//)

# 7.- They cannot end with a dot ..
#       (?<!\.)$

# 8.- They cannot contain a sequence @{.
#       (?!.*@\{)

# 9.- They cannot contain a \.
#       (?!.*\\)

# Piecing it all together we arrive at the following monstrosity:
# ^(?!.*/\.)(?!.*\.\.)(?!/)(?!.*//)(?!.*@\{)(?!.*\\)[^\040\177 ~^:?*[]+/[^\040\177 ~^:?*[]+(?<!\.lock)(?<!/)(?<!\.)$

# And if you want to exclude those that start with build- then just add another lookahead:
#       ^(?!build-)(?!.*/\.)(?!.*\.\.)(?!/)(?!.*//)(?!.*@\{)(?!.*\\)[^\040\177 ~^:?*[]+/[^\040\177 ~^:?*[]+(?<!\.lock)
#        (?<!/)(?<!\.)$

# This can be optimized a bit as well by conflating a few things that look for common patterns:
#       ^(?!build-|/|.*([/.]\.|//|@\{|\\))[^\040\177 ~^:?*[]+/[^\040\177 ~^:?*[]+(?<!\.lock|[/.])$

#####
#####  !! For now I will let all the branch names to be strings, I need to activate the regex :)
#####

GIT_MERGE_TARGET_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-03/schema#',
    'type' : 'object',
    'additionalProperties': False,
    'required': ['current_branch_name', 'target_branch_name'],
    'properties' : {
        'current_branch_name' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 512,
        },
        'target_branch_name' : {
            'type' : 'string',
            'minLength' : 1,
            'maxLength' : 512,
        },
    },
}
