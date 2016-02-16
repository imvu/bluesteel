""" Common code for transform objects """


def to_date_obj(date):
    """ Transforms a date into an obj """
    obj = {}
    obj['year'] = date.year
    obj['month'] = date.month
    obj['day'] = date.day
    obj['hour'] = date.hour
    obj['minute'] = date.minute
    obj['second'] = date.second
    obj['microsecond'] = date.microsecond
    obj['tzinfo'] = str(date.tzinfo)
    return obj
