# Guard-Process-Tree

## Introduction

Guard-Process-Tree is an implementation of a technique for learning **guards** on process trees using evolutionary algorithms. It introduces the concept of a **Guarded Process Tree**—an extension of classical process trees where transitions are equipped with logical conditions (guards) based on event attributes. These guards control the flow of execution, allowing the model to account for data-dependent behavior that is not captured by control-flow alone.

This enhancement enables more precise modeling and conformance checking, particularly in cases where the execution of activities depends on numerical thresholds, categorical values, or complex logical combinations of event attributes.

The learning of guards is performed using [PonyGE2](https://github.com/PonyGE/PonyGE2), a grammatical evolution engine that allows flexible definition and evolution of logical conditions.

For more details, see our paper [here](https://github.com/ids840/Guard-Process-Tree/blob/master/Guarded_Process_Trees%20With%20Appendix.pdf).

---

## Requirements

#### 1. Clone the repository

```bash
git clone https://github.com/ids840/Guard-Process-Tree.git
cd Guard-Process-Tree
```

---

### 2. Clone and install PonyGE2

```bash
git clone https://github.com/PonyGE/PonyGE2.git
cd PonyGE2
pip install -e .
```

---
### 3. Set PonyGE2 Parameters

Configure the parameters of PonyGE2 to align with the structure of your process tree in order to achieve optimal results. This involves:

- Adjusting the grammar files to reflect the format of guarded expressions.
- Tuning evolutionary operators and settings (e.g., selection, crossover, mutation).
- Setting an appropriate population size, number of generations, and other relevant hyperparameters.

These settings should reflect the specific structure and constraints of the guarded model you're working with.

---

### 4. Prepare your input event log 

Your log must be in `.csv` format.

**Required columns:**
- `activity`
- `timestamp`
- `case ID`

Additional columns (e.g., `amount`, `region`, etc.) are optional and will be used for learning guard conditions.

---

### 5. Put the file in the project files

---

## Running

### 1. Run `main.py`
---
### 1. Enter your file name
---
### 1. Choose Miner
