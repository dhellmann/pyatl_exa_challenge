package statements

import (
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
	a, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	op := s.input.Tokens[2]
	b, err := state.GetRegOrNum(s.input.Tokens[3])
	if err != nil {
		return err
	}

	result := 0
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

	state.Store(result, "T")
	state.Counter++
	return nil
}

// New builds an testStatement from the input statement
func newTest(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N", "OP", "R/N"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &testStatement{
		input: input,
	}, nil
}
