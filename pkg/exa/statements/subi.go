package statements

import (
	"fmt"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("SUBI", newSubi)
}

type subiStatement struct {
	input InputStatement
}

func (*subiStatement) Do(state *interpreter.State) error {
	return fmt.Errorf("NotImplemented: SUBI")
}

// New builds an subiStatement from the input statement
func newSubi(input InputStatement) (Statement, error) {
	return &subiStatement{
		input: input,
	}, nil
}
