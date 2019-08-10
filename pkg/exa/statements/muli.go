package statements

import (
	"fmt"
)

func init() {
	register("MULI", newMuli)
}

type muliStatement struct {
	input InputStatement
}

func (*muliStatement) Do() error {
	return fmt.Errorf("NotImplemented: MULI")
}

// New builds an muliStatement from the input statement
func newMuli(input InputStatement) (Statement, error) {
	return &muliStatement{
		input: input,
	}, nil
}
