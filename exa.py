#!/usr/bin/env python3

import argparse
import operator
import os.path


class Statement:

    _expected_args = 3

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        if len(tokens) != self._expected_args:
            raise RuntimeError('Expected {} arguments to {} on line {}: {}'.format(
                self._expected_args, tokens[0], line_num, tokens))
        self._line_num = line_num
        self._tokens = tokens

    def __str__(self):
        return '{:3} {}'.format(
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


class JUMP(Statement):

    _expected_args = 2

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._label = tokens[1]

    def do(self, interp_state):
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


class TEST(Statement):

    _op_funcs = {
        '>': operator.gt,
        '<': operator.lt,
        '=': operator.eq,
    }

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        # The number of arguments we expect depends on the mode, with
        # EOF testing a special case.
        if tokens[-1] == 'EOF':
            self._expected_args = 2
        else:
            self._expected_args = 4
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._a = tokens[1]
        if tokens[-1] == 'EOF':
            self._op = 'EOF'
            self._b = None
        else:
            self._op = tokens[2]
            self._b = tokens[3]

    def do(self, interp_state):
        if self._op == 'EOF':
            if interp_state.at_eof(self._line_num):
                result = 1
            else:
                result = 0
        else:
            a = interp_state.get_value(self._a, self._line_num)
            b = interp_state.get_value(self._b, self._line_num)

            try:
                op_func = self._op_funcs[self._op]
            except KeyError:
                raise RuntimeError('Unknown operator {} on line {}'.format(
                    self._op, self._line_num))

            if op_func(a, b):
                result = 1
            else:
                result = 0

        interp_state.store('T', result, self._line_num)
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


class GRAB(Statement):

    _expected_args = 2

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._id = tokens[1]

    def do(self, interp_state):
        file_id = interp_state.get_value(self._id, self._line_num)
        interp_state.grab_file(file_id)
        interp_state.next_statement += 1


class DROP(Statement):

    _expected_args = 1

    def do(self, interp_state):
        interp_state.drop_file(self._line_num)
        interp_state.next_statement += 1


class FILE(Statement):

    _expected_args = 2

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._to = tokens[1]

    def do(self, interp_state):
        interp_state.store(self._to, interp_state.current_file_id)
        interp_state.next_statement += 1


class SEEK(Statement):

    _expected_args = 2

    def __init__(self, line_num, stmt_num, tokens, interp, state):
        super().__init__(line_num, stmt_num, tokens, interp, state)
        self._offset = tokens[1]

    def do(self, interp_state):
        offset = interp_state.get_value(self._offset, self._line_num)
        interp_state.seek(offset, self._line_num)
        interp_state.next_statement += 1


class File:

    def __init__(self, file_id, output, initial_data=None):
        self._id = file_id
        self._output = output
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

    def read(self, line_num):
        # Check for reading past the end of the file by checking that
        # there is an item in the array at the current index before
        # returning it.
        try:
            response = self._content[self._cursor]
        except IndexError:
            raise RuntimeError('Read past the end of file {} at position {} on line {}'.format(
                self._id, self._cursor, line_num))
        self._cursor += 1
        return response

    def write(self, val, line_num):
        try:
            self._content[self._cursor] = val
            self._cursor += 1
        except IndexError:
            self._content.append(val)
            self._cursor = len(self._content)

    def get_content(self):
        return self._content


class InterpreterState:

    def __init__(self, output, files):
        self._output = output
        self._registers = {
            'T': 0,
            'X': 0,
        }
        self.next_statement = 0
        self.labels = {}
        self._files = files
        self._current_file = None
        self.current_file_id = None

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
        elif val == 'F':
            return self._current_file.read(line_num)
        else:
            try:
                vali = int(val)
                if not (-9999 <= vali <= 9999):
                    raise RuntimeError(
                        'Integer {} out of range [-9999, 9999]'.format(vali))
                return vali
            except TypeError:
                raise RuntimeError('Invalid input value {} on line {}'.format(
                    val, line_num))

    def store(self, loc, val, line_num):
        if loc in self._registers:
            self._registers[loc] = val
        elif loc == 'F':
            self._current_file.write(val, line_num)
        else:
            raise RuntimeError('Invalid storage address {} on line {}'.format(
                loc, line_num))

    def at_eof(self, line_num):
        if not self._current_file:
            raise RuntimeError('Tested EOF no file was open on line {}'.format(
                line_num))
        return self._current_file.at_eof()

    def grab_file(self, file_id):
        if file_id not in self._files:
            self._output('Creating file {}'.format(file_id))
            self._files[file_id] = File(file_id, self._output)
        self._current_file = self._files[file_id]
        self.current_file_id = file_id

    def drop_file(self, line_num):
        if not self._current_file:
            raise RuntimeError('Dropped when no file was open on line {}'.format(
                line_num))
        self._current_file = None
        self.current_file_id = None

    def seek(self, offset, line_num):
        if not self._current_file:
            raise RuntimeError('Seeked when no file was open on line {}'.format(
                line_num))
        self._current_file.seek(offset)

    def get_files(self):
        return self._files


class Interpreter:

    _commands = {
        'COPY': COPY,

        'ADDI': ADDI,
        'MULI': MULI,
        'DIVI': DIVI,
        'MODI': MODI,
        'SUBI': SUBI,

        'MARK': MARK,
        'JUMP': JUMP,

        'TEST': TEST,
        'TJMP': TJMP,
        'FJMP': FJMP,

        'FILE': FILE,
        'GRAB': GRAB,
        'DROP': DROP,
        'SEEK': SEEK,
    }

    def __init__(self, output):
        self._output = output
        self._data_files = {}

    def load_data_file(self, file_id, file_handle):
        content = []
        for num, line in enumerate(file_handle):
            try:
                content.append(int(line.strip()))
            except TypeError:
                raise RuntimeError('Invalid integer {} on line {} of {}'.format(
                    line.strip(), num, filename))
        self._data_files[file_id] = File(file_id, self._output, content)

    def run(self, statements):
        state = InterpreterState(self._output, self._data_files)
        program = self.parse(statements, state)

        while True:
            if state.next_statement >= len(program):
                # End of program
                break

            stmt = program[state.next_statement]
            stmt.do(state)
            self._output('{:30} {}'.format(str(stmt), state))

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
    p.add_argument('program')
    p.add_argument('-f', dest='files', action='append', default=[])
    p.add_argument('-v', dest='verbose', action='store_true', default=True)
    p.add_argument('-q', dest='verbose', action='store_false')
    args = p.parse_args()

    with open(args.program, 'r') as f:
        statements = f.readlines()

    def output(message):
        if args.verbose:
            print(message)

    interp = Interpreter(output)

    for filename in args.files:
        try:
            file_id = int(os.path.basename(filename))
        except TypeError:
            raise RuntimeError('Invalid filename {}, must be an integer'.format(
                filename))
        with open(filename, 'r') as f:
            interp.load_data_file(file_id, f)

    result = interp.run(statements)

    if args.verbose:
        print('FINAL:', result)
    else:
        print('X={:4} T={:4}'.format(result.X, result.T))

    for file_id, file_content in sorted(result.get_files().items()):
        print('\nFile: {}'.format(file_id))
        for i in file_content.get_content():
            print('  {}'.format(i))
