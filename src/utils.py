# -*- coding: utf-8 -*-


def find_item(obj, cond):
    if not isinstance(obj, (tuple, list,)):
        return None
    if not callable(cond):
        return None
    try:
        return next((item for item in obj if cond(item)), None)
    except Exception:
        return None
