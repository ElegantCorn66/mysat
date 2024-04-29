import os
import sys
import argparse
import random
from dimacs_parser import parse
import time


class implicant_graph:
    def __init__(self):
        self.variable = 0
        self.clause = []
        self.level = 0
        self.score = 0
    
def res_process(x):
    if x < 0:
        sgn = "0"
    else:
        sgn = "1"
    return str(abs(x)) + "=" + sgn


def get_counter(formula):
    """

    :param formula:
    :return: a dictionary counter whose key is literal name while its value is whether it exists in formula
    """
    counter = {}
    if formula == -1:
        return counter
    for clause in formula:
        for literal in clause:
            if literal in counter:
                counter[literal] += 1
            else:
                counter[literal] = 1
    return counter

def bcp(formula, unit, level):
    """
    one time decision module, with passing unit name, delete
    :param formula:
    :param unit:
    :return:
    """
    modified = []
    conflict_induced_clause = implicant_graph()
    # conflict_induced_clause.setdefault(key,[]).append(value)
    if formula == -1:
        return modified, conflict_induced_clause
    for clause in formula:
        if unit in clause:
            conflict_induced_clause.clause.append(clause)
            conflict_induced_clause.variable = unit
            conflict_induced_clause.level = level
            continue
        if -unit in clause:
            c = [x for x in clause if x != -unit]
            if len(c) == 0: return -1, conflict_induced_clause
            modified.append(c)
        else:
            modified.append(clause)
    conflict_induced_clause.score = len(conflict_induced_clause.clause)
    return modified, conflict_induced_clause


def UnitPropagation(formula, var):
    """
    Rewrite formula by deleting unit clauses var
    :param formula:
    :return:
    """
    if formula == -1:
        return -1
    unit_clauses = [c for c in formula if len(c) == 1]
    while len(unit_clauses) > 0:
        unit = unit_clauses[0]
        formula, conflict = bcp(formula, unit[0], 0)
        if formula == -1:
            return -1
        if not formula:
            return formula
        unit_clauses = [c for c in formula if len(c) == 1]
    return formula


def PickBranchingVariable(formula, chosen):
    """
    Branching Heuristic, random picking
    :param formula:
    :return:
    """
    random.seed(1)
    counter = get_counter(formula)
    if counter == {}:
        return []
    while True:
        var = abs(random.choice(list(counter.keys())))
        for item in chosen:
            if var == item:
                continue
        return var

def ConflictAnalysis(formula, chosen, conf_list):
    beta = 1
    if len(conf_list)==0:
        return 1, None
    else:
        max_conf = conf_list[0]
    if max_conf.variable == 0:
        return 1, None
    if len(chosen)>1:
        for item in conf_list:
            if item.score > max_conf.score:
                max_conf = item
        # print("Conflict: ", max_conf.variable, max_conf.clause, max_conf.level, max_conf.score)
        if chosen.index(max_conf.variable) != len(chosen)-1:
            lista = chosen
            learnt_clause = [ -x for x in lista]
            beta = len(chosen) - chosen.index(max_conf.variable) -1
        else:
            learnt_clause = None
            beta = 1
        
        # print("NEXT", learnt_clause, beta, chosen, chosen[:beta])
    # print(beta)
        return beta, learnt_clause
    else:
        return 1, None
#
def pure_literal(formula):
    """

    :param formula:
    :return:
    """
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


def Backtrack(formula, assignment, level):
    for ii in assignment[::-1]:
        if ii <= 0:
            level = level + 1
        else:
            break
        
    if len(assignment)==1:
        return [], assignment[-1]

    # if level>=len(assignment):
        # return [], assignment[0]
    if level>len(assignment):
        return [], PickBranchingVariable(formula, [])
    return assignment[:-level], -assignment[-level]



def CDCL(formula, nvar):
    conflict_list = []
    dl = 1 # decision level
    variable = PickBranchingVariable(formula, [])
    edited_formula, conflict = bcp(formula, variable, dl)
    conflict_list.append(conflict)
    # print("Conflict: ", conflict.variable, conflict.clause, conflict.level, conflict.score)
    chosen = []
    chosen.append(variable)
    sat_flag = UnitPropagation(formula, variable)
    if sat_flag == -1:
        return chosen
    back_flag = False
    sat_flag = 0
    while(len(chosen)<nvar):
        if back_flag:
            conflict_list = []
            variable = enforced_decision
            back_flag = False

            chosen.append(variable)
            edited_formula = formula
            for ii in chosen:
                edited_formula, conflict = bcp(edited_formula, ii, dl)
                # conflict_list.append(conflict)
        else:
            dl = dl + 1
            variable = PickBranchingVariable(edited_formula, chosen)
            chosen.append(variable)
            edited_formula, conflict = bcp(edited_formula, variable, dl)
            conflict_list.append(conflict)
            # print("Conflict: ", conflict.variable, conflict.clause, conflict.level, conflict.score)

        sat_flag = UnitPropagation(edited_formula, variable)
        # print(chosen, conflict.level)
        if sat_flag == -1:
            chosen, enforced_decision = Backtrack(formula, chosen, 1)
            back_flag = True
            continue
    return chosen


def solve(input_cnf_file, verbose=True):
    clauses, nvars = parse(input_cnf_file, verbose)
    
    startread = time.process_time()
    solution = CDCL(clauses, nvars)
    endread = time.process_time()
    print("Process time: ", endread-startread)

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


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Uses vtkWarpScalar')
    parser.add_argument('input', type=str, help='input location')
    args = parser.parse_args()
    solve(args.input)


