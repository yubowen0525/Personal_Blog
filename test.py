# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test
   Description :
   Author :       ybw
   date：          2020/8/18
-------------------------------------------------
   Change Activity:
                   2020/8/18:
-------------------------------------------------
"""

import re
from unidecode import unidecode

_punct_re = re.compile(r'[\t !""]')

def slugify(text,delim=u'-'):
    """

    :param text:
    :param delim:
    :return:
    """
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).lower().split())
    return unicode()