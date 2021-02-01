import warnings


def assert_dict_equal(expected: dict, reality: dict, skip_property: list):
    for ek in (k for k in expected.keys() if k not in skip_property):
        ex_val = expected[ek]
        r_val = reality[ek]
        if type(ex_val) == list:
            assert_list_equal(ex_val, r_val, skip_property)
        elif type(ex_val) == dict:
            assert_dict_equal(ex_val, r_val, ['id'])
        else:
            assert ex_val == r_val


def assert_list_equal(expected: list, reality: list, skip_property: list):
    assert len(expected) == len(reality)
    possible_keys = ['name', 'description', 'id']
    if len(expected) > 0:
        sort_by = __first_match(possible_keys, expected[0])
        if sort_by is not None:
            expected.sort(key=lambda x: x[sort_by])
            reality.sort(key=lambda x: x[sort_by])

            for i in range(len(expected)):
                assert_dict_equal(expected[i], reality[i], skip_property)
        else:
            warnings.warn(
                f'list matching skipped. list don\'t have any of the possible keys: {", ".join(possible_keys)}')


def __first_match(match, match_to):
    for m in match:
        if m in match_to:
            return m
