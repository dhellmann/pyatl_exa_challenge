package statements

import (
	"fmt"
)

func init() {
	register("ADDI", newAddi)
}

type addiStatement struct {
	input InputStatement
}

func (*addiStatement) Do() error {
	return fmt.Errorf("NotImplemented: ADDI")
}

// New builds an addiStatement from the input statement
func newAddi(input InputStatement) (Statement, error) {
	return &addiStatement{
		input: input,
	}, nil
}
