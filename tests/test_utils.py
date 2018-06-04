# -*- cofing: utf-8 -*-

import pytest

from src.utils import find_item


class TestFindItem:

    @pytest.mark.parametrize('obj, cond, expected', [
        ([1, 2, 3], lambda x: x == 2, 2),
        (tuple([1, 2, 3]), lambda x: x == 2, 2),
        ([1, '2', 3], lambda x: x == '2', '2'),
        (tuple([1, '2', 3]), lambda x: x == '2', '2'),
        ([1, 2, 3], lambda x: x != 2, 1),
        (tuple([1, 2, 3]), lambda x: x != 2, 1),
        ([{'k': 1}, {'k': 2}, {'k': 3}], lambda x: x['k'] > 2, {'k': 3}),
        (tuple([{'k': 1}, {'k': 2}, {'k': 3}]), lambda x: x['k'] > 2, {'k': 3}),
        ([1, 2, 3], lambda x: x > 3, None),
        (tuple([1, 2, 3]), lambda x: x > 3, None),
        (None, lambda x: x == 1, None),
        ('', lambda x: x == 1, None),
        ([1, 2, 3], None, None),
        ([1, 2, 3], '', None),
        ([{'k': 1}, {'k': 2}, {'k': 3}], lambda x: x['y'] > 2, None),
    ])
    def test_found(self, obj, cond, expected):
        item = find_item(obj, cond)
        assert item == expected
