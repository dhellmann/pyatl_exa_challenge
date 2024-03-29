package interpreter

import (
	"fmt"
	"strconv"
)

// CheckSyntax verifies that the input instructions match the
// specified syntax.
func CheckSyntax(syntax []string, tokens []string, lineNum int) error {

	if len(syntax) != len(tokens)-1 {
		return fmt.Errorf("Line %d: Expected %d arguments to %s got %d: %v",
			lineNum, len(syntax), tokens[0], len(tokens)-1, tokens)
	}

	for i := 0; i < len(syntax); i++ {
		syn := syntax[i]
		tok := tokens[i+1] // skip statement name
		switch syn {

		case "R/N":
			if tok == "X" || tok == "T" || tok == "F" {
				continue
			}
			if _, err := strconv.Atoi(tok); err == nil {
				continue
			}
			return fmt.Errorf("Line %d: Expected register name or integer for argument %d got %q: %v",
				lineNum, i, tok, tokens)

		case "R":
			if tok == "X" || tok == "T" || tok == "F" {
				continue
			}
			return fmt.Errorf("Line %d: Expected register name for argument %d got %q: %v",
				lineNum, i, tok, tokens)

		case "OP":
			switch tok {
			case "<":
			case ">":
			case "=":
			default:
				return fmt.Errorf("Line %d: Unknown operator %q as argument %d: %v",
					lineNum, i, tok, tokens)
			}

		case "L":
			// A label can be anything

		default:
			return fmt.Errorf("Unknown syntax instruction %q", syn)
		}
	}

	return nil
}
