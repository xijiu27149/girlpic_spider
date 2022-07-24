import os
import shutil
def removeemptyfolder():
   dicname="H:\\folder\\hotgirl\\"
   subdics=os.listdir(dicname)
   for subdic in subdics:
      temp=dicname+subdic
      files=os.listdir(temp)
      if(len(files)==0):
         shutil.rmtree(temp)
         print(temp+"已删除")
def addjpg():
   dicname = "/Users/dujingwei/Temp/folder/hotgirl/"
   filename = "/Users/dujingwei/Temp/folder/hotgirl/{}/{}"
   subdics=os.listdir(dicname)
   for subdic in subdics:
      temp = dicname+subdic
      if(subdic==".DS_Store"):
             continue
      files = os.listdir(temp)      
      for file in files:
         if(os.path.splitext(file)[-1]==""):
            oldfile = filename.format(subdic, file)
            newfile=filename.format(subdic,file+".jpg")
            if(os.path.exists(newfile)):
               os.remove(oldfile)
            else:
               os.rename(oldfile,newfile)
            print (newfile)
addjpg()