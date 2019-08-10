#!/usr/bin/env python3

import argparse
import operator
import os.path


MATH_CMDS = set(['ADDI', 'SUBI', 'MULI', 'DIVI', 'MODI'])
JUMP_CMDS = set(['MARK', 'JUMP', 'TJMP', 'FJMP'])
REGISTER_NAMES = 'FTX'

OPERATORS = {
    'ADDI': operator.add,
    'MULI': operator.mul,
    'SUBI': operator.sub,
    'MODI': operator.mod,
    'DIVI': operator.floordiv,
    '>': operator.gt,
    '<': operator.lt,
    '=': operator.eq,
}


class File:

    def __init__(self, file_id, initial_data=None):
        self._id = file_id
        self._cursor = 0
        self._content = initial_data or []

    def at_eof(self):
        return (self._cursor + 1) > len(self._content)

    def seek(self, offset):
        dest = self._cursor + offset
        if dest < 0:
            dest = 0
        if (dest + 1) > len(self._content):
            dest = len(self._content)
        self._cursor = dest

    def read(self):
        # Check for reading past the end of the file by checking that
        # there is an item in the array at the current index before
        # returning it.
        try:
            response = self._content[self._cursor]
        except IndexError:
            raise RuntimeError('Read past the end of file {} at position {}'.format(
                self._id, self._cursor))
        self._cursor += 1
        return response

    def write(self, val):
        try:
            self._content[self._cursor] = val
            self._cursor += 1
        except IndexError:
            self._content.append(val)
            self._cursor = len(self._content)

    def get_content(self):
        return self._content


def check_syntax(syntax, line_num, tokens):
    if len(syntax) != len(tokens) - 1:
        raise RuntimeError(
            'Expected {} arguments to {} got {} on line {}: {}',
            len(syntax), tokens[0], line_num, ' '.join(tokens))
    for i, (syn, tok) in enumerate(zip(syntax, tokens[1:])):
        if syn == 'R':
            if tok not in REGISTER_NAMES:
                raise RuntimeError(
                    'Expected register name, found {} at position {} on line {}'.format(
                        tok, i, line_num))
        elif syn == 'R/N':
            try:
                int(tok)
            except ValueError:
                if tok not in REGISTER_NAMES:
                    raise RuntimeError(
                        'Expected register name or integer, found {} at position {} on line {}'.format(
                            tok, i, line_num))
        elif syn == 'OP':
            if tok not in OPERATORS:
                raise RuntimeError(
                    'Unrecognized operator {} at position {} on line {}, must be one of {}'.format(
                        tok, i, line_num, list(OPERATORS.keys())))
        elif syn == 'L':
            # A label can be anything.
            pass
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

    # check the syntax of all the statements, and record the locations
    # of the labels
    labels = {}
    for i, (ln, tokens) in enumerate(tokenized):
        cmd = tokens[0]

        if cmd == 'COPY':
            check_syntax(('R/N', 'R'), ln, tokens)

        elif cmd in MATH_CMDS:
            check_syntax(('R/N', 'R/N', 'R'), ln, tokens)

        elif cmd == 'TEST':
            if len(tokens) == 2:
                if tokens[1] != 'EOF':
                    raise RuntimeError(
                        'Unrecognized test {} on line {}'.format(
                            tokens[1], line_num))
            else:
                check_syntax(('R/N', 'OP', 'R/N'), ln, tokens)

        elif cmd in JUMP_CMDS:
            check_syntax(('L',), ln, tokens)
            if cmd == 'MARK':
                label = tokens[1]
                if label in labels:
                    raise RuntimeError(
                        'Duplicate label {} on line {}'.format(label, line_num))
                labels[label] = i

        elif cmd == 'GRAB':
            check_syntax(('R/N',), ln, tokens)

        elif cmd == 'FILE':
            check_syntax(('R',), ln, tokens)

        elif cmd == 'SEEK':
            check_syntax(('R/N',), ln, tokens)

        elif cmd == 'DROP':
            check_syntax((), ln, tokens)

        else:
            raise RuntimeError('Unrecognized command {} on line {}'.format(
                cmd, ln))

    return tokenized, labels


def get_rn(val, registers, current_file):
    if val in registers:
        return registers[val]
    if val == 'F':
        if not current_file:
            raise RuntimeError('No open file')
        return current_file.read()
    return int(val)


def dupe_registers(registers):
    new_reg = {}
    new_reg.update(registers)
    return new_reg


def run_statement(line_num, statement, program_counter, registers, labels, file_id, files):
    cmd = statement[0]
    registers = dupe_registers(registers)

    if cmd == 'COPY':
        src = get_rn(statement[1], registers, files.get(file_id))
        dest = statement[2]
        if dest == 'F':
            current_file = files.get(file_id)
            if not current_file:
                raise RuntimeError('Writing to file before opening on line {}'.format(line_num))
            current_file.write(src)
        else:
            registers[dest] = src
        program_counter += 1

    elif cmd in MATH_CMDS:
        a = get_rn(statement[1], registers, files.get(file_id))
        b = get_rn(statement[2], registers, files.get(file_id))
        dest = statement[3]
        op = OPERATORS[cmd]
        registers[dest] = op(a, b)
        program_counter += 1

    elif cmd == 'TEST':
        if statement[1] == 'EOF':
            if not file_id:
                raise RuntimeError('Testing EOF without an open file on line {}'.format(
                    line_num))
            if files[file_id].at_eof():
                registers['T'] = 1
            else:
                registers['T'] = 0
        else:
            a = get_rn(statement[1], registers, files.get(file_id))
            op = OPERATORS[statement[2]]
            b = get_rn(statement[3], registers, files.get(file_id))
            if op(a, b):
                registers['T'] = 1
            else:
                registers['T'] = 0
        program_counter += 1

    elif cmd == 'JUMP':
        label = statement[1]
        program_counter = labels[label]

    elif cmd == 'TJMP':
        label = statement[1]
        if registers['T']:
            program_counter = labels[label]
        else:
            program_counter += 1

    elif cmd == 'FJMP':
        label = statement[1]
        if not registers['T']:
            program_counter = labels[label]
        else:
            program_counter += 1

    elif cmd == 'MARK':
        program_counter += 1

    elif cmd == 'GRAB':
        file_id = get_rn(statement[1], registers, files.get(file_id))
        if file_id not in files:
            files[file_id] = File(file_id)
        program_counter += 1

    elif cmd == 'DROP':
        file_id = None
        program_counter += 1

    elif cmd == 'SEEK':
        current_file = files.get(file_id)
        if not current_file:
            raise RuntimeError('No open file')
        offset = get_rn(statement[1], registers, current_file)
        current_file.seek(offset)
        program_counter += 1

    else:
        raise NotImplementedError(cmd)
    return program_counter, registers, file_id


def run_program(program, labels, files):
    program_counter = 0
    registers = {
        'T': 0,
        'X': 0,
    }
    file_id = None

    while program_counter < len(program):
        line_num, statement = program[program_counter]
        program_counter, registers, file_id = run_statement(
            line_num, statement, program_counter, registers, labels, file_id, files)
        print('{:3} {:20} T={:4} X={:4}'.format(
            line_num, ' '.join(statement), registers['T'], registers['X']))

    return registers, files


def load_data_file(file_id, file_handle):
    content = []
    for num, line in enumerate(file_handle):
        try:
            content.append(int(line.strip()))
        except TypeError:
            raise RuntimeError('Invalid integer {} on line {} of {}'.format(
                line.strip(), num, filename))
    return File(file_id, content)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('program')
    p.add_argument('-f', dest='files', action='append', default=[])
    args = p.parse_args()

    with open(args.program, 'r') as f:
        statements = f.readlines()

    files = {}
    for filename in args.files:
        try:
            file_id = int(os.path.basename(filename))
        except TypeError:
            raise RuntimeError('Invalid filename {}, must be an integer'.format(
                filename))
        with open(filename, 'r') as f:
            files[file_id] = load_data_file(file_id, f)

    program, labels = parse_program(statements)
    results, files = run_program(program, labels, files)
    print('\nT={T:4} X={X:4}'.format(**results))

    for file_id, file_content in sorted(files.items()):
        print('\nFile: {}'.format(file_id))
        for i in file_content.get_content():
            print('  {}'.format(i))
