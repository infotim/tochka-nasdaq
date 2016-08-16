# coding: utf-8
import uuid


def grouper(it, n):
    for i in range(0, len(it), n):
        yield it[i:i + n]


def uuid5(*args, namespace=uuid.NAMESPACE_OID):
    key = '+'.join([str(i) for i in args])
    return uuid.uuid5(namespace, key)
