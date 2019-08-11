package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("SEEK", newSeek)
}

type seekStatement struct {
	input InputStatement
}

func (s *seekStatement) String() string {
	return s.input.String()
}

func (s *seekStatement) Do(state *interpreter.State) error {
	offset, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	if err = state.Seek(offset); err != nil {
		return err
	}
	state.Counter++
	return nil
}

// New builds a seekStatement from the input statement
func newSeek(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &seekStatement{
		input: input,
	}, nil
}
