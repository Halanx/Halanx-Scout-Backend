from django.contrib import admin


def custom_titled_filter(title):
    """
    :param title: Title that you want to display as title in filter name in list_filter
    :return:
    """
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper