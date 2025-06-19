# Guard-Process-Tree

## Introduction

Guard-Process-Tree is an implementation of a technique for learning **guards** on process trees using evolutionary algorithms. It introduces the concept of a **Guarded Process Tree**—an extension of classical process trees where transitions are equipped with logical conditions (guards) based on event attributes. These guards control the flow of execution, allowing the model to account for data-dependent behavior that is not captured by control-flow alone.

This enhancement enables more precise modeling and conformance checking, particularly in cases where the execution of activities depends on numerical thresholds, categorical values, or complex logical combinations of event attributes.

The learning of guards is performed using [PonyGE2](https://github.com/PonyGE/PonyGE2), a grammatical evolution engine that allows flexible definition and evolution of logical conditions.

For more details, see our paper [here](https://github.com/ids840/Guard-Process-Tree/blob/master/Guarded_Process_Trees%20With%20Appendix.pdf).

---

## Requirements

### 1. Clone and install PonyGE2

```bash
git clone https://github.com/PonyGE/PonyGE2.git
cd PonyGE2
pip install -e .
```

---
### 2. Set PonyGE2 Parameters

Configure the parameters of PonyGE2 to align with the structure of your process tree in order to achieve optimal results. This involves:

- Adjusting the grammar files to reflect the format of guarded expressions.
- Tuning evolutionary operators and settings (e.g., selection, crossover, mutation).
- Setting an appropriate population size, number of generations, and other relevant hyperparameters.

These settings should reflect the specific structure and constraints of the guarded model you're working with.

---

### 3. Update `semantics.py` and `token_replay.py`

Replace the following files in your local project with the custom versions provided:

- [semantics.py](https://github.com/ids840/Guard-Process-Tree/blob/master/semantics.py).
- [token_reply.py](https://github.com/ids840/Guard-Process-Tree/blob/master/token_reply.py).


These custom modules enable **Conformance Checking for Guarded Models**. Specifically:

- The token replay is applied to the guarded Petri net using the test event log.
- Tokens left in the additional places (added only to evaluate guard conjunctions) are **ignored**, as they reflect the truth value of conjunctions and do not indicate behavioral deviations.

  ---
## Running

#### 1. Clone the repository

```bash
git clone https://github.com/ids840/Guard-Process-Tree.git
cd Guard-Process-Tree
```
### 2. Prepare your input event log

Your log must be in `.csv` format.

**Required columns:**
- `activity`
- `timestamp`
- `case ID`

Additional columns (e.g., `amount`, `region`, etc.) are optional and will be used for learning guard conditions.

### 3. Update file paths 

Update file paths in `main.py` and `LogSplit.py`.

### 4. Run `main.py`
