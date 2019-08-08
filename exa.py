#!/usr/bin/env python3

import argparse


class Interpreter:

    def __init__(self):
        self.T = 0
        self.X = 0

    def run(self, statements):
        program, labels = self.parse(statements)

        line_num = 0
        while True:
            if line_num >= len(program):
                # End of program
                break

            stmt_n, stmt = program[line_num]

            print(stmt_n, stmt)

            line_num += 1

    def parse(self, statements):
        # eliminate blank lines
        statements = [
            (ln, stmt.strip().split())
            for ln, stmt in enumerate(statements)
            if stmt.strip()
        ]

        # collect labels
        labels = {}
        for i, (ln, stmt) in enumerate(statements):
            if stmt[0] == 'MARK':
                try:
                    label = stmt[1]
                except IndexError:
                    raise RuntimeError('Invalid MARK statement on line {}'.format(ln))
                if label in labels:
                    raise RuntimeError('Duplicate mark {} on line {}'.format(ln, label))
                labels[label] = i

        return statements, labels


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('file')
    args = p.parse_args()

    with open(args.file, 'r') as f:
        statements = f.readlines()

    interp = Interpreter()
    interp.run(statements)
