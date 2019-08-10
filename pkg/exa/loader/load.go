package loader

import (
	"bufio"
	"os"
	"strings"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/statements"
)

// Load reads the contents of a file and creates a Program
func Load(filename string) (exa.Program, error) {

	fd, err := os.Open(filename)
	defer fd.Close()
	if err != nil {
		return exa.Program{}, err
	}

	results := exa.Program{}
	lineNum := 0
	statementCount := 0
	input := bufio.NewScanner(fd)
	for input.Scan() {

		lineNum++

		line := strings.Trim(input.Text(), " \t\n")
		if line == "" {
			continue
		}
		if line[0] == '#' {
			continue
		}

		inStmt := statements.InputStatement{
			LineNum:      lineNum,
			Line:         line,
			Tokens:       strings.Fields(line),
			StatementNum: statementCount,
		}
		newStatement, err := statements.Build(inStmt)
		if err != nil {
			return exa.Program{}, err
		}

		results = append(results, newStatement)

		statementCount++
	}

	return results, nil
}
