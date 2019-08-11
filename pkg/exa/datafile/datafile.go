package datafile

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path"
	"strconv"
	"strings"
)

type File interface {
	Read() (int, error)
	Write(int) error
	AtEOF() bool
	Seek(int)
}

type dataFile struct {
	id      int
	cursor  int
	content []int
}

func (df *dataFile) String() string {
	return fmt.Sprintf("%v", df.content)
}

func (df *dataFile) Read() (int, error) {
	if df.cursor >= len(df.content) {
		return 0, fmt.Errorf("Read past end of file %d at position %d",
			df.id, df.cursor)
	}
	result := df.content[df.cursor]
	df.cursor++
	return result, nil
}

func (df *dataFile) Write(val int) error {
	if df.cursor < len(df.content) {
		df.content[df.cursor] = val
	} else {
		df.content = append(df.content, val)
	}
	return nil
}

func (df *dataFile) AtEOF() bool {
	return df.cursor+1 > len(df.content)
}

func (df *dataFile) Seek(offset int) {
	dest := df.cursor + offset
	if dest < 0 {
		dest = 0
	}
	if dest > len(df.content) {
		dest = len(df.content)
	}
	df.cursor = dest
}

func New(id int) File {
	return &dataFile{
		id:      id,
		content: []int{},
	}
}

func loadOne(id int, fd io.Reader) (*dataFile, error) {
	f := &dataFile{
		id:      id,
		content: []int{},
	}

	input := bufio.NewScanner(fd)
	lineNum := 0
	for input.Scan() {
		line := strings.Trim(input.Text(), " \t\n")
		newVal, err := strconv.Atoi(line)
		if err != nil {
			return nil, fmt.Errorf("Bad value on line %d of %d: %s",
				lineNum, id, line)
		}
		f.content = append(f.content, newVal)
		lineNum++
	}

	return f, nil
}

func Load(filenames []string) (map[int]File, error) {
	results := map[int]File{}

	for _, filename := range filenames {

		fileID, err := strconv.Atoi(path.Base(filename))
		if err != nil {
			return results, fmt.Errorf("Data file names must be integers: %s: %s",
				filename, err)
		}

		fmt.Printf("Loading data file %s\n", filename)

		fd, err := os.Open(filename)
		defer fd.Close()
		if err != nil {
			return results, err
		}

		newFile, err := loadOne(fileID, fd)
		if err != nil {
			return results, err
		}

		results[fileID] = newFile

	}

	return results, nil
}
