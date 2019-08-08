#!/usr/bin/env python3

import argparse


class Statement:

    _expected_args = 3

    def __init__(self, line_num, statement):
        if len(statement) != self._expected_args:
            raise RuntimeError('Expected {} arguments to {} on line {}: {}'.format(
                self._expected_args, statement[0], line_num, statement))
        self._line_num = line_num
        self._stmt = statement

    def __str__(self):
        return '{} {}'.format(
            self._line_num,
            ' '.join(self._stmt),
        )

    def do(self, interp_state):
        raise NotImplementedError('{}.do'.format(
            self.__class__.__name))


class MARK(Statement):

    _expected_args = 2

    def __init__(self, line_num, statement):
        super().__init__(line_num, statement)
        self._label = statement[1]

    def do(self, interp_state):
        interp_state.next_statement += 1


class TJMP(Statement):

    _expected_args = 2

    def __init__(self, line_num, statement):
        super().__init__(line_num, statement)
        self._label = statement[1]

    def do(self, interp_state):
        if interp_state.T:
            label_address = interp_state.labels[self._label]
            interp_state.next_statement = label_address
        else:
            interp_state.next_statement += 1


class COPY(Statement):

    def __init__(self, line_num, statement):
        super().__init__(line_num, statement)
        self._from = statement[1]
        self._to = statement[2]

    def do(self, interp_state):
        try:
            _from = interp_state.get_value(self._from)
        except TypeError:
            raise RuntimeError('Invalid address {} on line {}'.format(
                self._from, self._line_num))

        try:
            interp_state.store(self._to, _from)
        except ValueError as err:
            raise RuntimeError('Invalid target address {} on line {}'.format(
                self._to, self._line_num))

        interp_state.next_statement += 1


class MathStatement(Statement):

    _expected_args = 4

    def __init__(self, line_num, statement):
        super().__init__(line_num, statement)
        self._a = statement[1]
        self._b = statement[2]
        self._to = statement[3]

    def do(self, interp_state):
        try:
            a = interp_state.get_value(self._a)
        except TypeError:
            raise RuntimeError('Invalid input value {} on line {}'.format(
                self._a, self._line_num))

        try:
            b = interp_state.get_value(self._b)
        except TypeError:
            raise RuntimeError('Invalid input value {} on line {}'.format(
                self._b, self._line_num))

        try:
            interp_state.store(self._to, self.compute(a, b))
        except ValueError as err:
            raise RuntimeError('Invalid target address {} on line {}'.format(
                self._to, self._line_num))

        interp_state.next_statement += 1



class ADDI(MathStatement):

    def compute(self, a, b):
        return a + b


class MULI(MathStatement):

    def compute(self, a, b):
        return a * b


class SUBI(MathStatement):

    def compute(self, a, b):
        return a - b


class InterpreterState:

    def __init__(self, labels):
        self.T = 0
        self.X = 0
        self.next_statement = 0
        self.labels = labels

    def __str__(self):
        return 'X= {:4} T= {:4} next= {:4}'.format(
            self.X, self.T, self.next_statement)

    def get_value(self, val):
        if val == 'X':
            return self.X
        elif val == 'T':
            return self.T
        else:
            return int(val)

    def store(self, loc, val):
        if loc == 'X':
            self.X = val
        elif loc == 'T':
            self.T = val
        else:
            raise ValueError('Invalid location {}'.format(loc))


class Interpreter:

    _commands = {
        'COPY': COPY,
        'ADDI': ADDI,
        'MULI': MULI,
        'SUBI': SUBI,
        'MARK': MARK,
        'TJMP': TJMP,
    }

    def run(self, statements):
        program, labels = self.parse(statements)
        state = InterpreterState(labels)

        while True:
            if state.next_statement >= len(program):
                # End of program
                break

            stmt = program[state.next_statement]
            stmt.do(state)
            print('{:30} {}'.format(str(stmt), state))

        return state

    def parse(self, statements):
        # eliminate blank lines
        statements = [
            (ln, stmt.strip().split())
            for ln, stmt in enumerate(statements)
            if stmt.strip()
        ]

        # build commands and collect marks
        labels = {}
        program = []
        for i, (ln, stmt) in enumerate(statements):
            if stmt[0] == 'MARK':
                try:
                    label = stmt[1]
                except IndexError:
                    raise RuntimeError('Invalid MARK statement on line {}'.format(ln))
                if label in labels:
                    raise RuntimeError('Duplicate mark {} on line {}'.format(ln, label))
                labels[label] = i
            try:
                factory = self._commands[stmt[0]]
            except KeyError:
                raise RuntimeError('Unknown statement on line {}: {}'.format(stmt, ln))
            program.append(factory(ln, stmt))

        return program, labels


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('file')
    args = p.parse_args()

    with open(args.file, 'r') as f:
        statements = f.readlines()

    interp = Interpreter()
    result = interp.run(statements)
    print('FINAL:', result)
