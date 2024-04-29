from dimacs_parser import parse
import random
import sys
import time

def res_process(x):
    if x < 0:
        sgn = "0"
    else:
        sgn = "1"
    return str(abs(x)) + "=" + sgn

def bcp(formula, unit):
    modified = []
    for clause in formula:
        if unit in clause: continue
        if -unit in clause:
            c = [x for x in clause if x != -unit]
            if len(c) == 0: return -1
            modified.append(c)
        else:
            modified.append(clause)
    return modified


# Count the number of occurences of each litteral in the formula
def get_counter(formula):
    counter = {}
    for clause in formula:
        for literal in clause:
            if literal in counter:
                counter[literal] += 1
            else:
                counter[literal] = 1
    return counter


# Find pure litterals then BCP w.r.t. these pure litterals
# Return a reduced formula after BCP & an assignement for these pure litterals
def pure_literal(formula):
    counter = get_counter(formula)
    assignment = []
    pures = []  # [ x for x,y in counter.items() if -x not in counter ]
    for literal, _ in counter.items():
        if -literal not in counter:
            pures.append(literal)
    for pure in pures:
        formula = bcp(formula, pure)
    assignment += pures
    return formula, assignment


# Unit Propagation (UP)
# Input : a formula F
# Ouput : a modified formula
# Core idea: find unit clauses (with len=1) and BCP w.r.t these unit variables
def unit_propagation(formula):
    assignment = []
    unit_clauses = [c for c in formula if len(c) == 1]
    while len(unit_clauses) > 0:
        unit = unit_clauses[0]
        formula = bcp(formula, unit[0])
        assignment += [unit[0]]
        if formula == -1:
            return -1, []
        if not formula:
            return formula, assignment
        unit_clauses = [c for c in formula if len(c) == 1]
    return formula, assignment


# Variable selection heuristics: Choosing randomly !!!
def variable_selection(formula):
    counter = get_counter(formula)
    return random.choice(list(counter.keys()))


# Backtracking when formula is UNSAT
# This is a recursive function
def backtracking(formula, assignment):
    formula, pure_assignment = pure_literal(formula)
    formula, unit_assignment = unit_propagation(formula)
    assignment = assignment + pure_assignment + unit_assignment
    if formula == - 1:
        return []
    if not formula:
        return assignment

    if len(get_counter(formula)) > 0:
        variable = variable_selection(formula)
        solution = backtracking(bcp(formula, variable), assignment + [variable])
        if not solution:
            solution = backtracking(bcp(formula, -variable), assignment + [-variable])
        return solution
    else:
        return assignment


def solve(input_cnf_file, verbose):
    clauses, nvars = parse(input_cnf_file, verbose)
    startread = time.process_time()
    solution = backtracking(clauses, [])
    endread = time.process_time()
    print("Process time: ", endread-startread)
    if verbose:
        # print('=====================[ Search Statistics  ]=====================')
        # print('|                                                              |')
        pass
    if solution:
        solution += [x for x in range(1, nvars + 1) if x not in solution and -x not in solution]
        solution.sort(key=lambda x: abs(x))
        if verbose:
            # print('=====================[       Result       ]=====================')
            print("RESULT: SAT")
            print('ASSIGNMENT: ' + ' '.join([res_process(x) for x in solution]))
    else:
        if verbose:
            # print('=====================[       Result       ]=====================')
            print('RESULT: UNSAT')