def add_with_none(num_1, num_2):
    if num_1 is not None and num_2 is not None:
        return num_1 + num_2
    elif num_1 is None:
        return num_2
    elif num_2 is None:
        return num_1
    else:
        return 0
