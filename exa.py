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
        interp_state.next_statement += 1


class MARK(Statement):

    _expected_args = 2

    def __init__(self, line_num, statement):
        super().__init__(line_num, statement)
        self._label = statement[1]


class COPY(Statement):

    def __init__(self, line_num, statement):
        super().__init__(line_num, statement)
        self._from = statement[1]
        self._to = statement[2]


class MathStatement(Statement):

    _expected_args = 4

    def __init__(self, line_num, statement):
        super().__init__(line_num, statement)
        self._a = statement[1]
        self._b = statement[2]
        self._to = statement[3]


class ADDI(MathStatement):
    pass


class MULI(MathStatement):
    pass


class SUBI(MathStatement):
    pass


class InterpreterState:

    def __init__(self):
        self.T = 0
        self.X = 0
        self.next_statement = 0


class Interpreter:

    _commands = {
        'COPY': COPY,
        'ADDI': ADDI,
        'MULI': MULI,
        'SUBI': SUBI,
        'MARK': MARK,
    }

    def run(self, statements):
        state = InterpreterState()
        program, labels = self.parse(statements)

        print(labels)

        while True:
            if state.next_statement >= len(program):
                # End of program
                break

            stmt = program[state.next_statement]
            print(stmt)
            stmt.do(state)

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
    interp.run(statements)
