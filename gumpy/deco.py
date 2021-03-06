# -*- coding: utf-8 -*-
__author__ = 'chinfeng'

import functools

from .framework import (
    Consumer, Annotation, ServiceAnnotation, Task,
    EventSlot, Activator, Deactivator, Requirement)


class _RequirementHepler(object):
    def __init__(self, fn, args, kwargs):
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self._requirements = {}

    def __get__(self, instance, owner):
        return Requirement(instance or owner, self._fn, self._args, self._kwargs)


require = lambda *args, **kwargs: functools.partial(_RequirementHepler, args=args, kwargs=kwargs)


class _ConsumerHelper(object):
    def __init__(self, fn, resource_uri, cardinality):
        assert (cardinality in ('0..1', '0..n', '1..1', '1..n'))
        self._fn = fn
        self._resource_uri = resource_uri
        self._cardinality = cardinality
        self._unbind_fn = lambda instance, service: None
        self._consumers = {}

    def __get__(self, instance, owner):
        _inst = instance or owner
        _id = id(_inst)
        if _id not in self._consumers:
            self._consumers[_id] = Consumer(_inst, self._fn, self._unbind_fn, self._resource_uri, self._cardinality)
        return self._consumers[_id]

    def unbind(self, fn):
        self._unbind_fn = fn
        return self


bind = lambda resource, cardinality='1..n': functools.partial(_ConsumerHelper, resource_uri=resource,
                                                              cardinality=cardinality)


class _EventHepler(object):
    def __init__(self, fn):
        self._fn = fn

    def __get__(self, instance, owner):
        if instance:
            return EventSlot(instance, self._fn)
        else:
            return self._fn


event = _EventHepler


def configuration(**config_map):
    def deco(func):
        def configuration_injected_func(self, *args, **kwargs):
            _kwargs = kwargs.copy()
            config = self.__reference__.__context__.configuration
            for p, c in config_map.items():
                try:
                    if isinstance(c, str):
                        ck, default = c, None
                    elif isinstance(c, (tuple, list)) and isinstance(c[0], str):
                        ck, default = c[0], c[1] if len(c) > 1 else None
                    else:
                        break
                    _kwargs[p] = config.get(ck, default)
                except KeyError:
                    pass
            return func(self, *args, **_kwargs)

        return configuration_injected_func

    return deco


class activate(Annotation):
    @property
    def subject(self):
        return Activator(self._subject)


class deactivate(Annotation):
    @property
    def subject(self):
        return Deactivator(self._subject)


provide = lambda provides: functools.partial(Annotation, provides=provides)
service = lambda name: ServiceAnnotation(name) if not isinstance(name, str) else functools.partial(ServiceAnnotation,
                                                                                                   name=name)


class _TaskHelper(object):
    def __init__(self, fn):
        self._fn = fn

    def __get__(self, instance, owner):
        if instance:
            return Task(self._fn, instance)
        else:
            return self._fn


task = _TaskHelper