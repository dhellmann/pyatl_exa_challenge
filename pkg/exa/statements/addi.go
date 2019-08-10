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
	return &addiStatement{
		input: input,
	}, nil
}
