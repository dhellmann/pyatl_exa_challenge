package statements

import (
	"fmt"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("TEST", newTest)
}

type testStatement struct {
	input InputStatement
}

func (s *testStatement) String() string {
	return s.input.String()
}

func (s *testStatement) Do(state *interpreter.State) error {

	result := 0

	if len(s.input.Tokens) == 2 {
		eof, err := state.AtEOF()
		if err != nil {
			return err
		}
		if eof {
			result = 1
		}
	} else {
		a, err := state.GetRegOrNum(s.input.Tokens[1])
		if err != nil {
			return err
		}
		op := s.input.Tokens[2]
		b, err := state.GetRegOrNum(s.input.Tokens[3])
		if err != nil {
			return err
		}

		switch op {
		case ">":
			if a > b {
				result = 1
			}
		case "<":
			if a < b {
				result = 1
			}
		case "=":
			if a == b {
				result = 1
			}
		}
	}

	if err := state.Store(result, "T"); err != nil {
		return err
	}
	state.Counter++
	return nil
}

// New builds an testStatement from the input statement
func newTest(input InputStatement) (statement Statement, err error) {
	if len(input.Tokens) == 2 {
		if input.Tokens[1] != "EOF" {
			err = fmt.Errorf("Line %d: Invalid argument to TEST: %v",
				input.LineNum, input.Tokens)
		}
	} else {
		err = interpreter.CheckSyntax(
			[]string{"R/N", "OP", "R/N"},
			input.Tokens,
			input.LineNum,
		)
	}
	if err != nil {
		return nil, err
	}
	return &testStatement{
		input: input,
	}, nil
}
