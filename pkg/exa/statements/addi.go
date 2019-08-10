package statements

import (
	"fmt"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("ADDI", newAddi)
}

type addiStatement struct {
	input InputStatement
}

func (*addiStatement) Do(state *interpreter.State) error {
	return fmt.Errorf("NotImplemented: ADDI")
}

// New builds an addiStatement from the input statement
func newAddi(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N", "R/N", "R"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &addiStatement{
		input: input,
	}, nil
}
