import os
import time
import random
import argparse

def res_process(x):
    if x < 0:
        sgn = "0"
    else:
        sgn = "1"
    return str(abs(x)) + "=" + sgn


def read_clause (filename):
    initial_time = time.time()
    clauses = []

    for line in open(filename):
        if line.startswith('c'): continue
        if line.startswith('p'):
            nvars, nclauses = line.split()[2:4]
            continue
        clause = [int(x) for x in line[:-2].split()]
        clauses.append(clause)
    
    end_time = time.time()
    return 1,int(nvars),len(clauses),clauses


def VSIDS_init(formula, num_var):
    '''
    Initialize VSIDS
    '''
    counter = {}
    for x in range(-num_var, num_var+1):
        counter[x]=0
    for clause in formula:
        for literal in clause:
            counter[literal] += 1
    return counter


def VSIDS_update(counter, conflictClause):
    '''
    Update counts
    '''
    for literal in conflictClause:
        counter[literal]+=1
    return counter


def VSIDS_decay(counter,num_var):
    for i in range(-num_var,num_var+1):
        counter[i]=counter[i]*95/100
    return counter


def VSIDS_decide(counter,M,num_var):
    max=0
    var=0
    for x in range(-num_var,num_var+1):
        if counter[x]>=max and x not in M and -x not in M:
                max=counter[x]
                var=x
    return var


def bcp(formula, unit):
    """
    one time decision module, with passing unit name, delete
    :param formula:
    :param unit:
    :return:
    """
    modified = []
    if formula == -1:
        return modified
    for clause in formula:
        if unit in clause:
            continue
        if -unit in clause:
            c = [x for x in clause if x != -unit]
            if len(c) == 0: return -1
            modified.append(c)
        else:
            modified.append(clause)
    return modified


def unit_propagation(formula):      
    assignment = []
    flag=1
    while flag!=0:                          
        flag=0
        for x in formula:                  
            if len(x) == 1 :                
                unit=x[0]
                formula = bcp(formula, unit) 
                assignment += [unit]
                flag=1
            if formula == -1:           
                return -1, []
            if not formula:                   
                return formula, assignment
    return formula, assignment


def CDCL(formula, num_var):
    '''
    Conflict-driven clause learning.
    '''
    decide_pos = []                            
    assigned_literals = []                                     
    formula,assigned_literals = unit_propagation(formula)                       
    if formula == -1 :
        return -1,0,0,0,0                                  
    back=assigned_literals[:]                                      
    counter = VSIDS_init(formula,num_var)                    
    
    literal_watch,clauses_literal_watched = create_watchList(formula,assigned_literals,num_var)

    probability=0.9                                           
    Restart_count = learned_count = Decide_count = Imp_count = 0
    
    while not all_vars_assigned(num_var , len(assigned_literals)) :            
        variable = VSIDS_decide(counter,assigned_literals,num_var)               
        Decide_count += 1
        assign(variable,assigned_literals,decide_pos)
        conflict,literal_watch = Cheff_BCP(formula,literal_watch,clauses_literal_watched,assigned_literals,variable)        
        
        
        while conflict != -1 :
            VSIDS_update(counter,conflict)                   
            counter=VSIDS_decay(counter,num_var)          
            learned_clause = Analyze_Conflict(assigned_literals, decide_pos)      
            dl = add_learned_clause_to(formula,literal_watch,clauses_literal_watched,learned_clause,assigned_literals) 
            learned_count += 1
            conf_flag,var,Imp_count = BackTrack(assigned_literals, dl, decide_pos,Imp_count)      

            if conf_flag == -1:                             
                return -1,Restart_count,learned_count,Decide_count,Imp_count
            assigned_literals.append(var)                                            
            conflict,literal_watch = Cheff_BCP(formula,literal_watch,clauses_literal_watched,assigned_literals,var)
    return assigned_literals,Restart_count,learned_count,Decide_count,Imp_count
    

def create_watchList(clauses, assigned_sym, num_var):       
    '''
    Initialize watchlist by introducing literal clause lookup table and first sets of watched literals.
    Dictionary and list is the main data structure used.
    '''  
    lite_clause_lookup = {}                  
    watched_literals = []         
    for i in range (-num_var,num_var+1):
        lite_clause_lookup[i] = []
    for i in range (0,len(clauses)):     
        newc = []
        first = 0
        for j in range(0,len(clauses[i])):
            if clauses[i][j] not in assigned_sym and first==0:
                A = clauses[i][j]
                first=1
                continue
            if clauses[i][j] not in assigned_sym and first==1:
                B = clauses[i][j]
                break
        newc.append(A)
        newc.append(B)
        watched_literals.append(newc)      
        lite_clause_lookup[A].append(i)              
        lite_clause_lookup[B].append(i)
    return lite_clause_lookup, watched_literals


def Cheff_BCP(clauses, lite_clause_lookup, watched_literals, assigned_sym, variable): 
    '''
    Cheff's boolean constrained propagation.
    '''
    prop_list = [variable]             
    while len(prop_list) != 0 :        
        variable = prop_list.pop()     
        for affected_claus_num in reversed(lite_clause_lookup[-variable]):
            affected_claus = clauses[affected_claus_num][:]
            A = watched_literals[affected_claus_num][0]
            B = watched_literals[affected_claus_num][1]
            A_prev=A
            B_prev=B
            status,assigned_sym,A,B,unit = CheckStatus(affected_claus,assigned_sym,A,B) 
            if status == "Unit" :
                prop_list.append(unit)
                assigned_sym.append(unit)                                        
            elif status == "Unsatisfied":                           
                return affected_claus,lite_clause_lookup

            lite_clause_lookup[A_prev].remove(affected_claus_num)
            lite_clause_lookup[B_prev].remove(affected_claus_num)
            watched_literals[affected_claus_num][0] = A
            watched_literals[affected_claus_num][1] = B
            lite_clause_lookup [A].append(affected_claus_num)
            lite_clause_lookup [B].append(affected_claus_num)
            
    return -1,lite_clause_lookup


def CheckStatus(clause, assigned_sym, A, B):
    unit = 0
    if A in assigned_sym or B in assigned_sym:                   
        return "Satisied", assigned_sym, A, B, unit
    sym=[]                               
    for literal in clause:                 
        if -literal not in assigned_sym:
            sym.append(literal)
        if literal in assigned_sym :
            if -A not in assigned_sym :
                return "Satisied", assigned_sym,A, literal,unit
            return "Satisied",assigned_sym,literal,B,unit
    if len(sym) == 1:                             
        return "Unit",assigned_sym,A,B,sym[0]
    if len(sym) == 0:                           
        return "Unsatisfied",assigned_sym,A,B,unit
    else :
        return "Unresolved",assigned_sym, sym[0], sym[1], unit 


def Analyze_Conflict(assigned_sym, decide_pos):
    '''
    Trivial conflict analysis by adding wrong assigned path to clause set
    '''
    learn = []
    for x in decide_pos:
        learn.append(-assigned_sym[x])
    return learn


def all_vars_assigned(num_var, M_len):        # Returns True if all variables already assigne , False otherwise
    if M_len >= num_var:
        return True
    return False


def assign(variable,M,decide_pos):             # Adds the decision literal to M and correponding update to decision level
    decide_pos.append(len(M))
    M.append(variable)


def add_learned_clause_to(clauses,literal_watch,clauses_literal_watched,Learned_c,M):
    if len(Learned_c) == 0:
        return -1
    if len(Learned_c) == 1:             # if unit clause is learnt : add it as a decision 
        M.append(Learned_c[0])
        return 1,Learned_c[0]
    clauses.append(Learned_c)           # for others, add two literals A,B to literal watch data structure
    A = Learned_c[0]
    B = Learned_c[1]
    i = len(clauses)-1
    newc = []
    newc.append(A)
    newc.append(B)
    clauses_literal_watched.append(newc)
    literal_watch[A].append(i)
    literal_watch[B].append(i)
    return 0


def BackTrack(assigned_sym, dec_level, decide_pos, Imp_count):  
    '''
    Backtrack function
    '''    
    Imp_count = Imp_count + len(assigned_sym) - len(decide_pos)
    if not decide_pos:
        return -1,-1,Imp_count
    dec_level = decide_pos.pop()
    literal = assigned_sym[dec_level]
    del assigned_sym[dec_level:]
    return 0,-literal,Imp_count


def getabs(e):
    return abs(e)


def main():       
    '''
    main function that prints standard output
    '''  
    parser = argparse.ArgumentParser(description='mySAT')
    parser.add_argument('input', type=str, help='NAME OF THE CNF BENCHMARK THAT IT WILL ACCEPT AS INPUT')
    args = parser.parse_args()

    a,num_var,num_claus,clauses = read_clause(args.input)                

    startSolve = time.process_time()
    solution = CDCL(clauses,num_var)                           
    EndSolve = time.process_time()

    if solution[0] != -1:
        tempsol = solution[0]
        tempsol.sort(key=getabs)
        print("RESULT: SAT")
        print("ASSIGNMENT: " + ' '.join([res_process(x) for x in tempsol]))
    else :
        print("RESULT: UNSAT")
        return


if __name__=="__main__":
    main()

