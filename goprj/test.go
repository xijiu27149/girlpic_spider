package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	cur_class, _ := strconv.Atoi(os.Args[1])
	cur_page, _ := strconv.Atoi(os.Args[2])
	cur_item, _ := strconv.Atoi(os.Args[3])
	cur_subpage, _ := strconv.Atoi(os.Args[4])
	fmt.Printf("%d_%d_%d_%d", cur_class, cur_page, cur_item, cur_subpage)
}
