import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from search import binary_search, build_sorted_index, lower_bound


# A few records that look like the ones in the AAC "animals" collection
RECORDS = [
    {"animal_id": "A746874", "name": "Lucy", "breed": "Labrador Retriever Mix"},
    {"animal_id": "A725717", "name": "Rex", "breed": "German Shepherd"},
    {"animal_id": "A733653", "name": "Lucy", "breed": "Newfoundland"},
    {"animal_id": "A664290", "name": "Max", "breed": "Rottweiler"},
    {"animal_id": "A798500", "name": "", "breed": "Bloodhound"},
    {"animal_id": "A691584", "breed": "Siberian Husky"},  # no name field
]


def linear_search(records, field, value):
    """Simple linear search, O(n). We use it to check that binary search gives the same answer."""
    target = str(value).strip().lower()
    return [r for r in records
            if r.get(field) is not None and str(r[field]).strip().lower() == target]


# ---------- build_sorted_index ----------

def test_index_is_sorted_by_key():
    index = build_sorted_index(RECORDS, "animal_id")
    keys = [key for key, _ in index]
    assert keys == sorted(keys)
    assert len(index) == len(RECORDS)


def test_index_skips_missing_and_empty_values():
    index = build_sorted_index(RECORDS, "name")
    names = [record.get("name") for _, record in index]
    assert "" not in names and None not in names
    assert len(index) == 4


def test_index_of_empty_collection():
    assert build_sorted_index([], "animal_id") == []


def test_index_rejects_invalid_input():
    with pytest.raises(Exception):
        build_sorted_index(None, "animal_id")
    with pytest.raises(Exception):
        build_sorted_index(RECORDS, "")


def test_index_does_not_modify_original_records():
    original = list(RECORDS)
    build_sorted_index(RECORDS, "animal_id")
    assert RECORDS == original


# ---------- binary_search ----------

def test_successful_search():
    index = build_sorted_index(RECORDS, "animal_id")
    result = binary_search(index, "A725717")
    assert result == [RECORDS[1]]


def test_search_with_no_match():
    index = build_sorted_index(RECORDS, "animal_id")
    assert binary_search(index, "A000001") == []


def test_target_smaller_and_larger_than_all_keys():
    index = build_sorted_index(RECORDS, "animal_id")
    assert binary_search(index, "A000000") == []
    assert binary_search(index, "Z999999") == []


def test_first_and_last_values():
    index = build_sorted_index(RECORDS, "animal_id")
    assert binary_search(index, "A664290") == [RECORDS[3]]  # smallest ID
    assert binary_search(index, "A798500") == [RECORDS[4]]  # largest ID


def test_empty_collection():
    assert binary_search([], "A746874") == []


def test_single_element_collection():
    index = build_sorted_index([RECORDS[0]], "animal_id")
    assert binary_search(index, "A746874") == [RECORDS[0]]
    assert binary_search(index, "A746875") == []


def test_duplicate_keys_return_all_matches():
    index = build_sorted_index(RECORDS, "name")
    result = binary_search(index, "Lucy")
    # Both dogs named Lucy should come back, in the same order as before
    assert result == [RECORDS[0], RECORDS[2]]


def test_search_is_case_and_whitespace_insensitive():
    index = build_sorted_index(RECORDS, "animal_id")
    assert binary_search(index, "  a746874 ") == [RECORDS[0]]


def test_partial_value_does_not_match():
    index = build_sorted_index(RECORDS, "animal_id")
    assert binary_search(index, "A7468") == []


def test_invalid_search_values():
    index = build_sorted_index(RECORDS, "animal_id")
    assert binary_search(index, None) == []
    assert binary_search(index, "") == []
    assert binary_search(index, "   ") == []


def test_numeric_field_values_are_searchable():
    records = [{"age": 52}, {"age": 104}, {"age": 26}]
    index = build_sorted_index(records, "age")
    assert binary_search(index, "104") == [{"age": 104}]


def test_lower_bound_positions():
    index = [("b", {}), ("d", {}), ("d", {}), ("f", {})]
    assert lower_bound(index, "a") == 0
    assert lower_bound(index, "d") == 1
    assert lower_bound(index, "e") == 3
    assert lower_bound(index, "z") == 4
    assert lower_bound([], "a") == 0


def test_matches_linear_search_on_random_data():
    # Binary search should always return the same records as linear search
    rng = random.Random(499)
    records = [{"animal_id": f"A{rng.randint(0, 300):06d}", "row": i}
               for i in range(1000)]
    index = build_sorted_index(records, "animal_id")
    for n in range(0, 301):
        target = f"A{n:06d}"
        assert binary_search(index, target) == linear_search(records, "animal_id", target)
