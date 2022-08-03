package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	filepath := "C:\\Users\\dujw\\Downloads\\file.txt"
	file, err := os.Open(filepath)
	if err != nil {
		fmt.Println(err)
	}
	defer file.Close()
	reader := bufio.NewReader(file)
	for {
		str, _ := reader.ReadString('\n')

		err = os.Remove(str)
		if err != nil {
			fmt.Println(err)
		} else {
			fmt.Println("成功__" + str)
		}
	}
}
