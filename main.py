import argparse
import gpt_dpll
def get_args():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-i', '--input',
        metavar='I',
        # default='cnf_instances/Steiner-9-5-bce.cnf',
        # default='cnf_instances/Steiner-15-7-bce.cnf',
        # default='cnf_instances/Steiner-27-10-bce.cnf',
        # default='cnf_instances/test.cnf',
        # default='cnf_instances/uf20-01.cnf',
        # default='cnf_instances/uf50-01.cnf',
        # default='cnf_instances/uf50-01.cnf',
        default='trivial_test/class.cnf',
        # default='cnf_instances/uuf100-UNSAT.cnf',
        help='The DIMACS file')
    argparser.add_argument(
        '-v', '--verbose',
        default=1,
        help='Verbose option')
    args = argparser.parse_args()
    return args

def main():
    try:
        args = get_args()
        input_cnf_file = args.input
        verbose = args.verbose
    except:
        print("missing or invalid arguments")
        exit(0)

    # dpll_solver.solve(input_cnf_file, verbose)
    solver = gpt_dpll.solve(input_cnf_file, verbose)
    # solver.solve()

if __name__ == '__main__':
    main()
