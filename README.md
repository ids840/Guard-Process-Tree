# Guard-Process-Tree

Guard-Process-Tree is an implementation of a technique for learning **guards** on process trees using evolutionary algorithms. It introduces the concept of a **Guarded Process Tree**—an extension of classical process trees where transitions are equipped with logical conditions (guards) based on event attributes. These guards control the flow of execution, allowing the model to account for data-dependent behavior that is not captured by control-flow alone.

This enhancement enables more precise modeling and conformance checking, particularly in cases where the execution of activities depends on numerical thresholds, categorical values, or complex logical combinations of event attributes.

The learning of guards is performed using [PonyGE2](https://github.com/PonyGE/PonyGE2), a grammatical evolution engine that allows flexible definition and evolution of logical conditions.

For more details, see our paper [here]https://github.com/ids840/Guard-Process-Tree/blob/master/Guarded_Process_Trees%20With%20Appendix.pdf.

---

## Requirements

### 1. Clone and install PonyGE2

```bash
git clone https://github.com/PonyGE/PonyGE2.git
cd PonyGE2
pip install -e .
