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
def create_watchList(clauses, assigned_sym, num_var):       
    '''
    Initialize watchlist by introducing literal clause lookup table and first sets of watched literals.
    Dictionary and list is the main data structure used.
    '''
def Cheff_BCP(clauses, lite_clause_lookup, watched_literals, assigned_sym, variable): 
    '''
    Cheff's boolean constrained propagation.
    '''
def Analyze_Conflict(assigned_sym, decide_pos):
    '''
    Trivial conflict analysis by adding wrong assigned path to clause set
    '''
def BackTrack(assigned_sym, dec_level, decide_pos, Imp_count):  
    '''
    Backtrack function
    '''
def main():       
    '''
    main function that prints standard output
    '''  
```
### RUN SAT solver
```
python3 mySAT.py benchmark.cnf
```
