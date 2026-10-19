---
layout: page
title: Algorithms
subtitle: Artifact 02 · Algorithms and Data Structures
permalink: /artifacts/algorithms/
---

The Grazioso Salvare dashboard from CS 340, with an exact search by Animal ID or Name using binary search.
{: .lead}

[Original notebook]({{ site.repo_url }}/tree/gh-pages/artifacts/grazioso-salvare-dashboard/original)
[Enhanced code]({{ site.repo_url }}/tree/gh-pages/artifacts/grazioso-salvare-dashboard/enhanced)
[Enhancement notes]({{ site.repo_url }}/blob/gh-pages/artifacts/grazioso-salvare-dashboard/enhanced/ENHANCEMENT_NOTES.md)
[Download zip]({{ "/assets/downloads/grazioso-salvare-dashboard.zip" | relative_url }})
{: .actions}

## Narrative

The artifact I selected is my CS 340 final project, a Jupyter Dash dashboard created for Grazioso Salvare. The application uses an AnimalShelter CRUD class to retrieve animal records from MongoDB and display them through a dashboard. Users can filter animals by rescue type, view the results in a data table, and see information through a breed chart and location map. The original artifact was created as part of my CS 340 coursework. For CS 499, I enhanced the application by adding an exact search feature for Animal ID and Name using a binary search algorithm.

I selected this artifact because it gave me a good opportunity to demonstrate my understanding of algorithms and data structures using an application I had already developed. The original application did not have an exact search feature for individual animals. The DataTable provided filtering, but the filtering was essentially a linear search through the available records. I improved the application by creating sorted indexes for Animal ID and Name and implementing binary search to locate matching records. The search values are normalized so that differences in capitalization and extra whitespace do not prevent a match. I also used a lower-bound approach so that the search can find the first matching position and return all records with the same key. The sorted indexes are cached so the application does not have to sort the records every time a user performs a search. I also added automated tests for successful searches, unsuccessful searches, duplicate values, empty collections, boundary conditions, normalization, and randomized comparisons against a linear search.

This enhancement allowed me to meet the course outcome related to designing and evaluating computing solutions using algorithmic principles while managing trade-offs in design choices. Although binary search has an O(log n) search time compared with O(n) for a linear search, it requires the data to be sorted first. Building the sorted index requires O(n log n) time and additional memory. Because of this, binary search is not necessarily more efficient for a single search. I addressed this trade-off by caching the sorted indexes so they could be reused for multiple searches. This allowed the application to benefit from the faster search time without repeatedly paying the cost of sorting the same records.

The enhancement also helped me better understand that selecting an algorithm involves more than comparing Big-O notation. I had to consider how the data was stored, how often searches would occur, how duplicate values should be handled, and how much additional memory the solution would require. One challenge was making sure that duplicate Animal IDs and names were handled correctly instead of returning only the first match. Testing the algorithm against randomized data helped me verify that the binary search returned the same results as a linear search. I also learned that an algorithm that is theoretically faster can still introduce other costs, which need to be considered when designing a practical solution. Overall, this enhancement gave me more experience evaluating algorithmic choices in the context of a real application rather than treating algorithms as isolated programming exercises.

## Pseudocode

Planned before the enhancement:

```text
START
Sort animals by the search field
Get the search input from user
Set first and last data from the dataset
WHILE first data is less than or equal to last data:
    Set middle data
    IF middle value is equal to search input:
        return middle value
    ELSE IF search input value is less than middle value:
        Search left half
    ELSE
        Search right half
    END IF
END WHILE
Return “Animal not found”
END
```

Final version, using a lower bound so every record with the same key is returned:

```text
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

## Complexity

| Operation | Time | Extra space |
|---|---|---|
| Original linear scan (per search) | O(n) | O(k) for results |
| Build sorted index (once per filter/field) | O(n log n) | O(n) references |
| Binary search (per search) | O(log n + k), k = matches | O(k) |

The timing measurements, trade-offs, and the full list of tests are in the [enhancement notes]({{ site.repo_url }}/blob/gh-pages/artifacts/grazioso-salvare-dashboard/enhanced/ENHANCEMENT_NOTES.md).

In the online copy of the original notebook, the course database login is replaced with placeholders.
