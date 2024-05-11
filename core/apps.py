from django.apps import AppConfig


# default_auto_field specifies the default primary key field type to use when creating models in this app.
# In this case, it's set to BigAutoField, which is a field suitable for databases like PostgreSQL
# that support big integers as primary keys and automatically increment them.
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
