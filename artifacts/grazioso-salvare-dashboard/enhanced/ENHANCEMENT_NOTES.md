# CS-499 Artifact 2 – Algorithms and Data Structures Enhancement Notes

## Original artifact
A Jupyter Dash dashboard (`ProjectTwoDashboard.ipynb`) for Grazioso Salvare that uses the
`AnimalShelter` CRUD class (`mongo.py`) to read Austin Animal Center records from MongoDB.
Users pick a rescue type (Water, Mountain/Wilderness, Disaster/Tracking, or None); the
callback sends a hard-coded MongoDB filter, rebuilds a pandas DataFrame, and shows the
results in a DataTable with a breed pie chart and a location map.

## Original search behavior
- The only "search" was the rescue-type filter, which re-queried MongoDB on every change.
- The DataTable's built-in `filter_action="native"` let users filter a column, which is a
  linear scan of every row in the browser.
- There was no way to look up one animal by an exact key (such as Animal ID).
- `Pseudocode.txt` already sketched a binary search plan, but it was not implemented.

## What changed
| File | Change |
|---|---|
| `search.py` (new) | `build_sorted_index`, `lower_bound`, `binary_search`, `normalize` |
| `ProjectTwoDashboard.ipynb` | Search field dropdown (Animal ID / Name) and text input; filter queries moved into `load_records()`; records and sorted indexes cached; callback uses binary search; guards for empty results in chart and map |
| `tests/test_search.py` (new) | 18 tests for the algorithm, including a randomized comparison against linear search |
| `tests/test_mongo.py` (new) | 9 regression tests for the existing CRUD module (pymongo stubbed) |
| `ProjectTwoDashboard.original.ipynb` | Unmodified backup of the original notebook |

## Final pseudocode
```
BUILD-SORTED-INDEX(records, field)
    index ← empty list
    FOR EACH record IN records
        IF record has a non-empty value for field
            APPEND (NORMALIZE(record[field]), record) TO index
    STABLE-SORT index BY key                      // O(n log n)
    RETURN index

LOWER-BOUND(index, target)
    low ← 0
    high ← length(index)
    WHILE low < high
        mid ← floor((low + high) / 2)
        IF index[mid].key < target
            low ← mid + 1                         // first match is right of mid
        ELSE
            high ← mid                            // mid may be the first match
    RETURN low                                    // first position with key ≥ target

BINARY-SEARCH(index, searchValue)
    IF searchValue is null OR NORMALIZE(searchValue) is empty
        RETURN empty list
    target ← NORMALIZE(searchValue)               // trim + lowercase
    position ← LOWER-BOUND(index, target)
    matches ← empty list
    WHILE position < length(index) AND index[position].key = target
        APPEND index[position].record TO matches  // duplicates are adjacent
        position ← position + 1
    RETURN matches                                // empty list = "Animal not found"
```
In the dashboard, the index for each (rescue filter, search field) pair is built once and
cached, so later searches only run `BINARY-SEARCH`.

## Why this design
- **Binary search needs sorted, randomly accessible data.** MongoDB returns an unsorted
  list, so the records are copied into a Python list of `(key, record)` pairs sorted by key.
  A list gives O(1) access to `index[mid]`.
- **Lower-bound variant instead of "return the middle".** The original pseudocode stops at
  the first match it finds. Names repeat (many dogs share a name) and the AAC data can have
  multiple outcome records for one Animal ID, so the search finds the *first* matching
  position and collects every adjacent match.
- **Sort on key only.** Sorting the tuples directly would try to compare dictionaries when
  keys tie, which raises a `TypeError` in Python. Python's sort is stable, so ties keep their
  original order.
- **Normalized keys** make searches case- and whitespace-insensitive (`" a746874 "` finds `A746874`).
- **Records with a missing/empty field are skipped** in the index; they cannot match an exact search.

## Complexity
| Operation | Time | Extra space |
|---|---|---|
| Original linear scan (per search) | O(n) | O(k) for results |
| Build sorted index (once per filter/field) | O(n log n) | O(n) references |
| Binary search (per search) | O(log n + k), k = matches | O(k) |

## Trade-offs (honest)
Measured on this machine with synthetic data (`timeit`), not the real database:

| n | Linear scan | Sort once | Binary search | Break-even |
|---|---|---|---|---|
| 100 | 9 µs | 34 µs | 0.6 µs | ~4 searches |
| 10,000 | 868 µs | 6.0 ms | 1.7 µs | ~7 searches |
| 100,000 | 9.6 ms | 66 ms | 1.7 µs | ~7 searches |

- A single search is **slower** with binary search because of the sort. It only pays off
  when the sorted index is reused (several searches on the same dataset), which is why the
  dashboard caches it.
- The cache uses extra memory and can go stale: records inserted into MongoDB after the
  first load are not seen until the notebook is restarted. This is acceptable for a
  read-only, single-user dashboard but would need invalidation in a multi-user system.
- Binary search only supports **exact** matches on one field. Partial matches ("Luc")
  still use the DataTable's built-in column filter.
- For very large data, a MongoDB index on `animal_id` would do the same job (a B-tree
  lookup) on the server. Building the index in Python keeps the algorithm visible and works
  on data already loaded into the dashboard.
- For tiny datasets, the difference is microseconds and not noticeable to a user.

## Testing
`python -m pytest tests` → **27 passed**.
- Successful search, no match, target below/above all keys, first and last keys.
- Empty collection, single-element collection, duplicate keys (all returned, stable order).
- Case/whitespace normalization, partial value not matching, `None`/empty/blank input.
- Numeric field values, missing/empty field values skipped, invalid arguments rejected.
- `lower_bound` boundary positions.
- Randomized test: 1,000 records with many duplicates, all 301 possible IDs searched,
  results must equal a linear search.
- Regression tests for `mongo.py` create/read/update/delete validation.

**Not tested automatically:** the notebook callbacks themselves, since they need the
Apporto MongoDB server and `jupyter_dash`. These should be checked manually in Apporto.

## Running locally (added after the course ended)
Apporto access and the original AAC dataset are no longer available, so:
- `mongo.py` now defaults to a local MongoDB (`localhost:27017`, no authentication);
  credentials, host and port can still be passed in.
- `seed_data.py` inserts **500 synthetic records** into `aac.animals` (fixed random
  seed, same field names and column order as the AAC data, ~2% repeated Animal IDs,
  ~5% unnamed animals). The data is fake; the results below describe this sample only.
- The deprecated `jupyter_dash` package no longer works with current Dash (`run_server`
  was removed), so the notebook now uses `dash.Dash` and `app.run()`.

Verified against the local database: dashboard served HTTP 200; filter row counts
NONE 429 / WTR 18 / MWR 20 / DITR 30; a search for a repeated ID returned both records
through the live callback; for every ID and name in every filter, binary search returned
exactly the same records as a linear scan; empty results render a message instead of crashing.
