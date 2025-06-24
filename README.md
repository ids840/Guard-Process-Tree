# Guard-Process-Tree

## Introduction

Guard-Process-Tree is an implementation of a technique for learning **guards** on process trees using evolutionary algorithms. It introduces the concept of a **Guarded Process Tree**—an extension of classical process trees where transitions are equipped with logical conditions (guards) based on event attributes. These guards control the flow of execution, allowing the model to account for data-dependent behavior that is not captured by control-flow alone.

This enhancement enables more precise modeling and conformance checking, particularly in cases where the execution of activities depends on numerical thresholds, categorical values, or complex logical combinations of event attributes.

The learning of guards is performed using [PonyGE2](https://github.com/PonyGE/PonyGE2), a grammatical evolution engine that allows flexible definition and evolution of logical conditions.

For more details, see our paper [here](https://github.com/ids840/Guard-Process-Tree/blob/master/Guarded_Process_Trees%20With%20Appendix.pdf).

---

## Requirements

### 0. Python 3.8+
---

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

### 5. Put the csv file in the project files
Locate the csv file inside the project directory.
---
### 6. Install pm4py
```bash
pip install pm4py
```
---
## Running

### 1. Run `main.py`
Run the main script.
---
### 2. Enter your file name
When prompted, enter the name of your event log file (excluding the .csv extension).
The file should be located inside the project directory.
---
### 3. Choose Miner
Next, choose the process discovery algorithm to apply:

1 - Inductive Miner

2 - Heuristics Miner

3 - Alpha Miner

4 - ILP Miner

Type the corresponding number and press Enter.
