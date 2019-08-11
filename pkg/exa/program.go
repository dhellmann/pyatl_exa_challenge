package exa

import (
	"bufio"
	"fmt"
	"io"
	"strings"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/datafile"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/statements"
)

// Program is a bunch of statements
type Program struct {
	statements []statements.Statement
	labels     map[string]int
}

// Load reads the contents of a file and creates a Program and returns
// it with a mapping of any labels that have been marked.
func Load(fd io.Reader) (*Program, error) {

	program := &Program{
		labels: map[string]int{},
	}

	lineNum := 0
	statementNum := 0

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
			LineNum: lineNum,
			Line:    line,
			Tokens:  strings.Fields(line),
		}
		newStatement, err := statements.Build(inStmt)
		if err != nil {
			return nil, err
		}

		program.statements = append(program.statements, newStatement)

		if inStmt.Tokens[0] == "MARK" {
			if _, ok := program.labels[inStmt.Tokens[1]]; ok {
				return nil, fmt.Errorf("Line %d: Duplicate label %q",
					lineNum, inStmt.Tokens[1])
			}
			program.labels[inStmt.Tokens[1]] = statementNum
		}

		statementNum++
	}

	return program, nil
}

// Run executes a program and returns the resulting state or any errors
func (p *Program) Run(dataFiles map[int]datafile.File) (*interpreter.State, error) {
	state := &interpreter.State{
		Labels: p.labels,
		Files:  dataFiles,
	}

	for {
		if state.Counter >= len(p.statements) {
			break
		}
		nextStatement := p.statements[state.Counter]
		fmt.Printf("%-20s ", nextStatement)
		if err := nextStatement.Do(state); err != nil {
			return nil, err
		}
		fmt.Printf("%v\n", state)
	}

	return state, nil
}
