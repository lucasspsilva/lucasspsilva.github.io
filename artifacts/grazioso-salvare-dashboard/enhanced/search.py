"""
Binary search for the Grazioso Salvare dashboard.

The dashboard gets the animals from MongoDB as a list of dictionaries. Before,
finding one animal meant looking at every record (linear search, O(n)).
Binary search is faster, O(log n), but it only works on sorted data. So we
sort the records by the field we want to search one time, and then we can
run binary search on that sorted list as many times as we need.

    build_sorted_index : O(n log n) time and O(n) extra space, done one time
    binary_search      : O(log n + k) time, where k is the number of matches
"""


def normalize(value):
    """
    Turns a field value into the key we compare against.

    We remove extra spaces and make everything lowercase, so that searching
    for " a746874 " still finds the animal with the ID "A746874".
    """
    return str(value).strip().lower()


def build_sorted_index(records, field):
    """
    Builds a list of (key, record) pairs sorted by the given field.

    Parameters
    ----------
    records : List of Dict
        The animal records returned by AnimalShelter.read().
    field : str
        The field we want to search on, for example "animal_id" or "name".

    If a record does not have the field, or the field is empty, we skip it,
    because there is nothing to search for in that record.
    """
    if records is None:
        raise Exception("Records parameter must be a list, not None")
    if not field:
        raise Exception("A search field must be provided")

    index = []
    for record in records:
        value = record.get(field)
        # Skip records that are missing the field or have it empty
        if value is None or normalize(value) == "":
            continue
        index.append((normalize(value), record))

    # We sort only by the key. Python's sort is stable, so animals with the
    # same key stay in the same order they came from the database.
    index.sort(key=lambda pair: pair[0])
    return index


def lower_bound(index, target):
    """
    Uses binary search to find the position of the first key that is greater
    than or equal to target. If every key is smaller, it returns len(index).
    """
    low = 0
    high = len(index)
    while low < high:
        mid = (low + high) // 2
        if index[mid][0] < target:
            # The middle key is too small, so the target can only be in the right half
            low = mid + 1
        else:
            # The middle key could be the first match, so we keep it and look in the left half
            high = mid
    return low


def binary_search(index, search_value):
    """
    Finds every record whose key is equal to search_value.

    Parameters
    ----------
    index : List of (str, Dict)
        A sorted list created by build_sorted_index().
    search_value : str
        The value the user typed in the search box.

    Returns a list with the matching records, or an empty list if nothing matches.
    """
    # An empty search does not match anything
    if search_value is None:
        return []
    target = normalize(search_value)
    if target == "":
        return []

    # Find where the first match would be
    first = lower_bound(index, target)

    # More than one animal can have the same key (for example the same name).
    # Since the list is sorted, they are all next to each other, so we keep
    # moving right from the first match until the key is different.
    matches = []
    position = first
    while position < len(index) and index[position][0] == target:
        matches.append(index[position][1])
        position += 1
    return matches
