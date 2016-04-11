""" Automatic file """

#Find a better place for this code that will set the cache of Sqlite

from django.db.backends.signals import connection_created

def activate_foreign_keys(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite."""
    del sender
    del kwargs
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA main.cache_size = -1000000;')

connection_created.connect(activate_foreign_keys)
