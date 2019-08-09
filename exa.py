#!/usr/bin/env python3

import argparse
import operator


class Statement:

    _expected_args = 3

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        if len(tokens) != self._expected_args:
            raise RuntimeError('Expected {} arguments to {} on line {}: {}'.format(
                self._expected_args, tokens[0], line_num, tokens))
        self._line_num = line_num
        self._tokens = tokens

    def __str__(self):
        return '{} {}'.format(
            self._line_num,
            ' '.join(self._tokens),
        )

    def do(self, interp_state):
        raise NotImplementedError('{}.do'.format(
            self.__class__.__name))


class MARK(Statement):

    _expected_args = 2

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._label = tokens[1]
        state.add_label(self._label, stmt_num, line_num)

    def do(self, interp_state):
        interp_state.next_statement += 1


class TJMP(Statement):

    _expected_args = 2

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._label = tokens[1]

    def do(self, interp_state):
        if interp_state.T:
            label_address = interp_state.get_label(self._label, self._line_num)
            interp_state.next_statement = label_address
        else:
            interp_state.next_statement += 1


class FJMP(Statement):

    _expected_args = 2

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._label = tokens[1]

    def do(self, interp_state):
        if interp_state.T:
            interp_state.next_statement += 1
        else:
            label_address = interp_state.get_label(self._label, self._line_num)
            interp_state.next_statement = label_address


class COPY(Statement):

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._from = tokens[1]
        self._to = tokens[2]

    def do(self, interp_state):
        _from = interp_state.get_value(self._from, self._line_num)
        interp_state.store(self._to, _from, self._line_num)
        interp_state.next_statement += 1


class MathStatement(Statement):

    _expected_args = 4

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._a = tokens[1]
        self._b = tokens[2]
        self._to = tokens[3]

    def do(self, interp_state):
        a = interp_state.get_value(self._a, self._line_num)
        b = interp_state.get_value(self._b, self._line_num)
        interp_state.store(self._to, self.compute(a, b), self._line_num)
        interp_state.next_statement += 1


class TEST(Statement):

    _expected_args = 4

    _op_funcs = {
        '>': operator.gt,
        '<': operator.lt,
        '=': operator.eq,
    }

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._a = tokens[1]
        self._op = tokens[2]
        self._b = tokens[3]

    def do(self, interp_state):
        a = interp_state.get_value(self._a, self._line_num)
        b = interp_state.get_value(self._b, self._line_num)

        try:
            op_func = self._op_funcs[self._op]
        except KeyError:
            raise RuntimeError('Unknown operator {} on line {}'.format(
                self._op, self._line_num))

        if op_func(a, b):
            interp_state.store('T', 1, self._line_num)
        else:
            interp_state.store('T', 0, self._line_num)

        interp_state.next_statement += 1


class ADDI(MathStatement):

    def compute(self, a, b):
        return a + b


class MULI(MathStatement):

    def compute(self, a, b):
        return a * b


class DIVI(MathStatement):

    def compute(self, a, b):
        return a // b


class MODI(MathStatement):

    def compute(self, a, b):
        return a % b


class SUBI(MathStatement):

    def compute(self, a, b):
        return a - b


class InterpreterState:

    def __init__(self):
        self._registers = {
            'T': 0,
            'X': 0,
        }
        self.next_statement = 0
        self.labels = {}

    @property
    def T(self):
        return self._registers['T']

    @property
    def X(self):
        return self._registers['X']

    def __str__(self):
        return 'X={:4} T={:4} next={:4}'.format(
            self.X, self.T, self.next_statement)

    def add_label(self, label, stmt_num, line_num):
        if label in self.labels:
            raise RuntimeError('Duplicate mark {} on line {}'.format(
                line_num, label))
        self.labels[label] = stmt_num

    def get_label(self, label, line_num):
        if label not in self.labels:
            raise ValueError('Invalid label {} in jump on line {}'.format(
                label, line_num))
        return self.labels[label]

    def get_value(self, val, line_num):
        if val in self._registers:
            return self._registers[val]
        else:
            try:
                return int(val)
            except TypeError:
                raise RuntimeError('Invalid input value {} on line {}'.format(
                    val, line_num))

    def store(self, loc, val, line_num):
        if loc in self._registers:
            self._registers[loc] = val
        else:
            raise RuntimeError('Invalid storage address {} on line {}'.format(
                loc, line_num))


class Interpreter:

    _commands = {
        'COPY': COPY,
        'ADDI': ADDI,
        'MULI': MULI,
        'DIVI': DIVI,
        'MODI': MODI,
        'SUBI': SUBI,
        'MARK': MARK,
        'TJMP': TJMP,
        'FJMP': FJMP,
        'TEST': TEST,
    }

    def __init__(self, output):
        self.output = output

    def run(self, statements):
        state = InterpreterState()
        program = self.parse(statements, state)

        while True:
            if state.next_statement >= len(program):
                # End of program
                break

            stmt = program[state.next_statement]
            stmt.do(state)
            self.output('{:30} {}'.format(str(stmt), state))

        return state

    def parse(self, statements, state):
        # clean up extra white space, eliminate blank lines, ignore
        # comments, and parse each line into tokens
        tokenized = [
            (ln, stmt.strip().split())
            for ln, stmt in enumerate(line.strip() for line in statements)
            if stmt and not stmt.startswith('#')
        ]

        # build commands and collect marks
        program = []
        for sn, (ln, tokens) in enumerate(tokenized):
            try:
                factory = self._commands[tokens[0]]
            except KeyError:
                raise RuntimeError('Unknown statement on line {}: {}'.format(tokens, ln))
            program.append(factory(ln, sn, tokens, self, state))

        return program


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('file')
    p.add_argument('-v', dest='verbose', action='store_true', default=True)
    p.add_argument('-q', dest='verbose', action='store_false')
    args = p.parse_args()

    with open(args.file, 'r') as f:
        statements = f.readlines()

    def output(message):
        if args.verbose:
            print(message)

    interp = Interpreter(output)
    result = interp.run(statements)
    if args.verbose:
        print('FINAL:', result)
    else:
        print('X={:4} T={:4}'.format(result.X, result.T))
