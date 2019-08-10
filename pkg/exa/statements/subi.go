package statements

import (
	"fmt"
)

func init() {
	register("SUBI", newSubi)
}

type subiStatement struct {
	input InputStatement
}

func (*subiStatement) Do() error {
	return fmt.Errorf("NotImplemented: SUBI")
}

// New builds an subiStatement from the input statement
func newSubi(input InputStatement) (Statement, error) {
	return &subiStatement{
		input: input,
	}, nil
}
