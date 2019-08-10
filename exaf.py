#!/usr/bin/env python3

import argparse
import operator


MATH_CMDS = set(['ADDI', 'SUBI', 'MULI', 'DIVI', 'MODI'])

OPERATORS = {
    'ADDI': operator.add,
    'MULI': operator.mul,
    'SUBI': operator.sub,
}


def check_syntax(syntax, line_num, tokens):
    if len(syntax) != len(tokens) - 1:
        raise RuntimeError(
            'Expected {} arguments to {} got {} on line {}: {}',
            len(syntax), tokens[0], line_num, ' '.join(tokens))
    for i, (syn, tok) in enumerate(zip(syntax, tokens[1:])):
        if syn == 'R':
            if tok not in 'TX':
                raise RuntimeError(
                    'Expected register name, found {} at position {} on line {}'.format(
                        tok, i, line_num))
        elif syn == 'R/N':
            try:
                int(tok)
            except ValueError:
                if tok not in 'TX':
                    raise RuntimeError(
                        'Expected register name or integer, found {} at position {} on line {}'.format(
                            tok, i, line_num))
        else:
            raise RuntimeError('Unknown syntax instruction {}'.format(syn))


def parse_program(statements):
    # clean up extra white space, eliminate blank lines, ignore
    # comments, and parse each line into tokens
    tokenized = [
        (ln, stmt.strip().split())
        for ln, stmt in enumerate(line.strip() for line in statements)
        if stmt and not stmt.startswith('#')
    ]

    # check the syntax of all the statements
    for i, (ln, tokens) in enumerate(tokenized):
        cmd = tokens[0]
        if cmd == 'COPY':
            check_syntax(('R/N', 'R'), ln, tokens)
        elif cmd in MATH_CMDS:
            check_syntax(('R/N', 'R/N', 'R'), ln, tokens)
        else:
            raise RuntimeError('Unrecognized command {} on line {}'.format(
                cmd, ln))

    return tokenized


def get_rn(val, registers):
    if val in registers:
        return registers[val]
    return int(val)


def dupe_registers(registers):
    new_reg = {}
    new_reg.update(registers)
    return new_reg


def run_statement(line_num, statement, program_counter, registers):
    cmd = statement[0]
    registers = dupe_registers(registers)

    if cmd == 'COPY':
        src = get_rn(statement[1], registers)
        dest = statement[2]
        registers[dest] = src
        program_counter += 1

    elif cmd in MATH_CMDS:
        a = get_rn(statement[1], registers)
        b = get_rn(statement[2], registers)
        dest = statement[3]
        op = OPERATORS[cmd]
        registers[dest] = op(a, b)
        program_counter += 1

    else:
        raise NotImplementedError(cmd)
    return program_counter, registers


def run_program(program):
    program_counter = 0
    registers = {
        'T': 0,
        'X': 0,
    }

    while program_counter < len(program):
        line_num, statement = program[program_counter]
        program_counter, registers = run_statement(
            line_num, statement, program_counter, registers)
        print('{:3} {:20} T={:4} X={:4}'.format(
            line_num, ' '.join(statement), registers['T'], registers['X']))

    return registers


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('program')
    args = p.parse_args()

    with open(args.program, 'r') as f:
        statements = f.readlines()

    program = parse_program(statements)
    results = run_program(program)
    print('\nT={T:4} X={X:4}'.format(**results))
