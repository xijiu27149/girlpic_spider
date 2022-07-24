package main

import (
	"fmt"
	"github.com/antchfx/htmlquery"
	"golang.org/x/net/html"
	"io"
	"net/http"
	"os"
	"path"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"
)

func main() {
	starturl := "https://www.haotu555.net/htm/98/"
	classurl := "https://www.haotu555.net"
	savepath := "H:\\folder\\haotu555"
	cur_class, _ := strconv.Atoi(os.Args[1])
	cur_page, _ := strconv.Atoi(os.Args[2])
	var wg sync.WaitGroup
	//cur_class := 16
	//cur_page := 4

	doc, err := htmlquery.LoadURL(starturl)
	if err != nil {
		panic(err)
	}
	list, err := htmlquery.QueryAll(doc, "//div[@class='jigou']/ul/li")
	if err != nil {
		panic(err)
	}
	for i, n := range list {
		if i+1 < cur_class {
			continue
		}
		a := htmlquery.FindOne(n, "//a")
		classname := htmlquery.InnerText(a)
		halfsuburl := htmlquery.SelectAttr(a, "href")
		compclassid := regexp.MustCompile("/htm/(.*?)/")
		classidstr := compclassid.FindStringSubmatch(halfsuburl)
		classid := classidstr[len(classidstr)-1]

		var build strings.Builder
		build.WriteString(classurl)
		build.WriteString(halfsuburl)
		suburl := build.String()
		span := htmlquery.FindOne(n, "//span")
		countstr := htmlquery.InnerText(span)
		itemsdoc, err := htmlquery.LoadURL(suburl)
		if err != nil {
			panic(err)
		}
		classpagenode := htmlquery.FindOne(itemsdoc, "//span[@class='pageinfo']/strong[1]")
		classpagesizestr := htmlquery.InnerText(classpagenode)
		classpagesize, _ := strconv.ParseInt(classpagesizestr, 0, 64)
		classpagesizeint32 := int(classpagesize)
		for p := 1; p <= classpagesizeint32; p++ {
			if i+1 == cur_class && p < cur_page {
				continue
			}
			itemurl := fmt.Sprintf("%slist_%s_%d.html", suburl, classid, p)
			itempagedoc, _ := htmlquery.LoadURL(itemurl)
			items, err := htmlquery.QueryAll(itempagedoc, "//li[@class='post-home home-list1']")
			if err != nil {
				panic(err)
			}
			wg.Add(len(items))
			for k := 0; k < len(items); k++ {
				go func(k int) {
					defer wg.Done()
					Spider(i, len(list), p, classpagesizeint32, savepath, classname, countstr, items[k], nil, k)
				}(k)
			}
			wg.Wait()
		}

	}
}
func Spider(i int, classcount int, classpageindex int, classpagecount int, savepath string, classname string, countstr string, item *html.Node, ch chan bool, k int) {
	b := htmlquery.FindOne(item, "//h3/a")
	imgpageurl := htmlquery.SelectAttr(b, "href")
	imgtitle := htmlquery.InnerText(b)
	c := htmlquery.FindOne(item, "//div[@class='fields']/span[1]")
	imgcountstr := htmlquery.InnerText(c)
	imgdic := fmt.Sprintf("%s\\%s【%s】\\%s[%s]", savepath, classname, countstr, imgtitle, imgcountstr)
	if !PathExists(imgdic) {
		os.MkdirAll(imgdic, os.ModePerm)
	}
	imgpagedoc, err := htmlquery.LoadURL(imgpageurl)
	if err != nil {
		panic(err)
	}
	pagesizenode := htmlquery.FindOne(imgpagedoc, "//div[@class='nav-links']/a[1]")
	pagesizeInt32 := 1
	if pagesizenode != nil {
		pagesizestext := htmlquery.InnerText(pagesizenode)
		compileregex := regexp.MustCompile("共(.*?)页")
		matchArr := compileregex.FindStringSubmatch(pagesizestext)
		pagesizestr := matchArr[len(matchArr)-1]
		pagesize, _ := strconv.ParseInt(pagesizestr, 0, 64)
		pagesizeInt32 = int(pagesize)
	}

	imgindex := 1
	for k := 1; k <= pagesizeInt32; k++ {
		pageurl := imgpageurl
		if k > 1 {
			pageurl = strings.Replace(imgpageurl, ".html", fmt.Sprintf("_%d.html", k), 1)
		}
		imgdoc, _ := htmlquery.LoadURL(pageurl)
		imgs, _ := htmlquery.QueryAll(imgdoc, "//div[@class='cmntent']/img")
		for _, img := range imgs {
			sourceurl := htmlquery.SelectAttr(img, "src")
			fullname := path.Base(sourceurl)
			filesuffix := path.Ext(fullname)
			//filenameonly := strings.TrimSuffix(fullname, filesuffix)
			noname := fmt.Sprintf("%03d", imgindex)
			imgname := fmt.Sprintf("%s\\%s", imgdic, noname+filesuffix)
			if !PathExists(imgname) {
				DownloadFile(sourceurl, imgname)
			}
			fmt.Printf("class:%s【%d/%d】page:【%d/%d】subpage:【%d/%d】,imgs:【%d/%s】,%s \n", classname, i+1, classcount, classpageindex, classpagecount, k, pagesizeInt32, imgindex, imgcountstr, imgname)
			imgindex++
		}
		time.Sleep(time.Second * 2)
	}
	if ch != nil {
		ch <- true
	}
}
func PathExists(path string) bool {
	_, err := os.Stat(path)
	if err == nil {
		return true
	}
	if os.IsNotExist(err) {
		return false
	}
	return false
}
func DownloadFile(fileurl string, filename string) {
	res, err := http.Get(fileurl)
	if err != nil {
		panic(err)
	}
	defer res.Body.Close()
	out, err := os.Create(filename)
	if err != nil {
		panic(err)
	}
	defer out.Close()
	_, err = io.Copy(out, res.Body)
	if err != nil {
		panic(err)
	}
}
