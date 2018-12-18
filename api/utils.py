import random

from django.http import Http404
from django.conf import settings
from django.utils.text import slugify

from rest_framework.exceptions import ErrorDetail
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import exception_handler


def model_to_dict(instance, fields=None, exclude=None):
    from django.db.models.fields.files import ImageField
    from itertools import chain

    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if isinstance(f, ImageField):
            image = f.value_from_object(instance)
            data[f.name] = image.url if image else None
        else:
            data[f.name] = f.value_from_object(instance)
    return data


def combine_multiple(exceptions):
    message = ""
    for key, val in exceptions.items():
        if key == 'non_field_errors':
            key = ''

        if message:
            message += ", '{0}': {1}".format(key, ''.join(val)) if key else ", '{}'".format(''.join(val))
        else:
            message += "'{0}': {1}".format(key, ''.join(val)) if key else "'{}'".format(''.join(val))
    return message


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response:
        response.data = {'code': getattr(settings, 'ERROR_CODE', '0000')}
        if isinstance(exc, Http404):
            response.data['message'] = str(exc)
        elif isinstance(exc.detail, ErrorDetail):
            response.data['message'] = exc.detail
        elif isinstance(exc.detail, ReturnDict):
            response.data['message'] = combine_multiple(exc.detail)
    return response


def unique_slug_generator(instance, field='name'):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a name character (char) field.
    """
    slug = instance.slug
    if not slug:
        slug = slugify(getattr(instance, field))

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    while qs_exists:
        randint = random.randint(100, 1000)
        slug = "{}-{}".format(slug, randint)
        qs_exists = Klass.objects.filter(slug=slug).exists()
    return slug
