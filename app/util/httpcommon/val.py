""" Common code for validation """

from jsonschema import Draft4Validator
import jsonschema
import json

def validate_json_string(text):
    """ Validates a json string, if false, returns error message """
    try:
        data = json.loads(text)
    except ValueError as val_err:
        return (False, {'msg' : str(val_err)})
    except TypeError as type_err:
        return (False, {'msg' : str(type_err)})
    return (True, data)

def validate_obj_schema(obj, schema):
    """ Validate an object with an schema, if false, returns error message """
    try:
        Draft4Validator.check_schema(schema)
        Draft4Validator(schema).validate(obj)
    except jsonschema.ValidationError as val_err:
        return (False, {'msg' : str(val_err)})
    except jsonschema.SchemaError as sch_err:
        return (False, {'msg' : str(sch_err)})
    return (True, obj)
