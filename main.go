package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"os"
	"regexp"
)

func main() {
	data := read_stdin()
	parse_packages(data)
}

func read_stdin() string {
	data := ""
	r := bufio.NewReader(os.Stdin)
	buf := make([]byte, 0, 4*1024)
	for {
		n, err := r.Read(buf[:cap(buf)])
		buf = buf[:n]
		data += string(buf)
		if n == 0 {
			if err == nil {
				continue
			}
			if err == io.EOF {
				break
			}
			log.Fatal(err)
		}
		// process buf
		if err != nil && err != io.EOF {
			log.Fatal(err)
		}
	}

	return data
}

func parse_packages(info string) int {
	reg := `(?U)\n[a-zA-Z0-9]+/.*\n    `

	nodes := SplitAfter(reg, info)
	for _, item := range nodes {
		fmt.Printli("Section: " + item)
	}
	return 0
}
func SplitAfter(reg string, str string) []string {
	var (
		r []string
		p int
	)
	re := regexp.MustCompile(reg)
	is := re.FindAllStringIndex(str, -1)
	if is == nil {
		return append(r, str)
	}
	for _, i := range is {
		r = append(r, str[p:i[0]])
		r = append(r, str[i[0]:i[1]])
		p = i[1]
	}
	return append(r, str[p:])
}

func extract(nodes []string) ret []string{
	for i = 1;i < len(nodes); i = i + 2 {
	}
}
