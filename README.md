# 5022CMD Advanced Algorithms: Portfolio

Individual portfolio for 5022CMD Advanced Algorithms (Coventry University, delivered at INTI). It contains three Python programs, one per question. The written report is submitted separately.

| Folder           | Topic                                                         | Entry point                          | Status      |
|------------------|---------------------------------------------------------------|--------------------------------------|-------------|
| `q1_hashing`     | Hash table with linear probing, used for a pharmacy inventory | `inventory_app.py`, `experiment.py`  | Complete    |
| `q2_graph`       | Directed graph of course prerequisites                        | `course_app.py`                      | Complete    |
| `q3_concurrency` | Threaded vs sequential naive recursive Fibonacci              | `fib_threads.py`                     | Complete    |

## Requirements

Python 3.8 or later. Only the standard library is used, so there is nothing to install.

## Layout

```
q1_hashing/
  hash_table.py      # generic HashTable (open addressing, linear probing)
  product.py         # Product and subclasses
  inventory_app.py   # menu program
  experiment.py      # hash table vs 1-D array search timing
q2_graph/
  graph.py           # generic directed Graph
  course.py          # Course entity
  course_app.py      # menu program
q3_concurrency/
  fibonacci.py       # naive recursive fibonacci(n)
  fib_threads.py     # threaded vs sequential timing
tests/               # unittest tests
```

Each data-structure module (`hash_table.py`, `graph.py`) is generic and has no menu or domain code, so it can be tested and reused on its own.

## Q1: Hashing (pharmacy inventory)

```
cd q1_hashing
python inventory_app.py
```

The menu starts with 10 sample products (7 medicines, 3 general items) and offers: add, search, edit, delete, list all and exit. Every product is stored in both the `HashTable` and a plain list (the 1-D array), and every change is made to both. Search shows the record and the average time, over 1,000 searches, to find it in each structure.

Product IDs are 1 to 10 letters or digits and are case-insensitive (`p001` finds `P001`). Prices are entered in RM with at most 2 decimal places and dates as `YYYY-MM-DD`. When editing, pressing Enter keeps the current value.

### Search experiment

```
cd q1_hashing
python experiment.py
```

For N = 100, 1,000, 10,000 and 100,000 the program generates N synthetic products (`P000001`, `P000002`, ...) and stores the same records in a `HashTable` and a plain list. It then times searches in both for the first, middle and last inserted IDs and for an ID that is not present, averaging 1,000 searches per key with `time.perf_counter_ns()`. The results are printed as a table and saved to `q1_hashing/search_results.csv`. The sizes and the number of repeats are set by `SIZES` and `REPEATS` at the top of the file.

## Q2: Graph (course prerequisites)

```
cd q2_graph
python course_app.py
```

The program starts with 10 courses (7 core, 3 elective) and 11 prerequisite links. Each course is a vertex in a directed `Graph`, and each edge points from a prerequisite to the course it unlocks. A course's prerequisites are therefore its incoming vertices, and the courses it unlocks are its outgoing vertices.

Menu options:

1. List all course names.
2. View the full details of a course (every field, whatever its level).
3. View a course's prerequisites.
4. View the courses a course unlocks.
5. Add a course (code, name, credit hours, level and description, each validated; duplicate codes are refused).
6. View a course profile, which respects visibility: a core course shows every field, an elective shows its name only.
7. Add a prerequisite. This is refused if the two courses are the same, if the prerequisite already exists, or if it would create a cycle. The cycle check uses the graph's depth-first `hasPath`: making Y a prerequisite of X adds the edge Y -> X, which closes a cycle exactly when a path from X to Y already exists.
8. Remove a prerequisite.

Course codes are case-insensitive (`cs201` finds `CS201`). The graph stores neighbours in sets, which have no fixed order, so every list is sorted by course code before it is printed and the output is the same on every run.

## Q3: Concurrency

```
cd q3_concurrency
python fib_threads.py
```

The program computes `fibonacci(35)`, `fibonacci(38)` and `fibonacci(40)` in two ways, 10 rounds each:

- **Threaded:** three `threading.Thread` objects, one per call, started together. Each thread records its own start and end time with `time.perf_counter_ns()`. T = latest end - earliest start.
- **Sequential:** the same three calls one after another in the main thread. T = end of the last call - start of the first.

It prints each round's three results and T, then the average T of each run and the percentage difference (threaded relative to sequential).

A full run takes several minutes because `fibonacci` is deliberately the slow recursive version. Close other programs while it runs, as background load affects the timings. Results depend on the machine and the Python build.

## Tests

Run all tests from the repository root:

```
python -m unittest discover -s tests -v
```

The Q3 tests use small inputs (n = 10, 12, 15) so they finish in well under a second.
