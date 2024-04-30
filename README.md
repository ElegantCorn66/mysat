## Group 36 submission of ECE51216 Spring course project
### Option 1: Implement a basic SAT solver

Input: CNF formula in “DIMACS” format

Several public benchmark repositories (https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html, http://archive.dimacs.rutgers.edu/pub/challenge/sat/benchmarks/cnf/)

Output: Satisfying variable assignment, or assertion that the formula is un-satisfiable 

Heuristics: watched literals and VSIDS

### Directory structure
All functions are contained in mySAT.py file. Since Python is used, there's no need to compile.
#### Key Functions and Data Structures in mySAT.py
```
def VSIDS_init(formula, num_var):
    '''
    Initialize VSIDS
    '''
def CDCL(formula, num_var):
    '''
    Conflict-driven clause learning.
    '''
```
### RUN SAT solver
```
python3 mySAT.py benchmark.cnf
```
