def set_diff(old_set, new_set):
    # returns (deletions, additions, new_set) triple
    return (old_set - new_set, new_set - old_set, new_set)
