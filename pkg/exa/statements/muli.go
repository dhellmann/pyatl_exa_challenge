package statements

import (
	"fmt"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("MULI", newMuli)
}

type muliStatement struct {
	input InputStatement
}

func (*muliStatement) Do(state *interpreter.State) error {
	return fmt.Errorf("NotImplemented: MULI")
}

// New builds an muliStatement from the input statement
func newMuli(input InputStatement) (Statement, error) {
	return &muliStatement{
		input: input,
	}, nil
}
