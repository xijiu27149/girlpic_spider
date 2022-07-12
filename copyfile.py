import sys
import os
import shutil
from tkinter import *


#dicname=sys.argv[1]
#filecount = sys.argv[2]
#dicname = "D:\\Temp\\text"
#filecount=5
root = Tk()


def confirmclick():
    dicname = txt_dic.get(1.0,"end").strip()
    filecount = txt_count.get(1.0, "end")
    if(not os.path.exists(dicname)):
        print("路径错误")
        #sys.exit()
    files = os.listdir(dicname)
  
    max = 1
    maxfile = ""
    for file in files:
        no = os.path.splitext(file)[0]
        if(int(no) > max):
            max = int(no)
            maxfile = file
    for i in range(max+1, int(filecount)+1):
        maxfilepath = "{}\\{}".format(dicname, maxfile)
        newfilename = "{}{}".format(str(i).rjust(
            len(os.path.splitext(maxfile)[0]), '0'), os.path.splitext(maxfile)[-1])
        newfilepath = "{}\\{}".format(dicname, newfilename)
        shutil.copyfile(maxfilepath, newfilepath)
    print("Done")


txt_dic=Text(root)
txt_count = Text(root)

btn_ok=Button(root,text="确定",command=confirmclick)

txt_count.pack()
txt_dic.pack()
btn_ok.pack()
txt_dic.insert("insert", "路径")
#txt_count.insert("count", "文件数")

root.mainloop()
