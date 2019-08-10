package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("MARK", newMark)
}

type markStatement struct {
	input InputStatement
	label string
}

func (s *markStatement) String() string {
	return s.input.String()
}

func (s *markStatement) Do(state *interpreter.State) error {
	state.Counter++
	return nil
}

// New builds a markStatement from the input statement
func newMark(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"L"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &markStatement{
		input: input,
		label: input.Tokens[1],
	}, nil
}
