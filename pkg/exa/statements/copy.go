package statements

import (
	"fmt"
)

func init() {
	register("COPY", newCopy)
}

type copyStatement struct {
	input InputStatement
}

func (*copyStatement) Do() error {
	return fmt.Errorf("NotImplemented: COPY")
}

// New builds a copyStatement from the input statement
func newCopy(input InputStatement) (Statement, error) {
	return &copyStatement{
		input: input,
	}, nil
}
