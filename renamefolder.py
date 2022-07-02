
import os


pdic="E:\ososedki"
folders=os.listdir(pdic)
for folder in folders:
    subfolder="E:\ososedki\{}".format(folder)
    items=os.listdir(subfolder)
    for item in items:
        itemfolder = "E:\ososedki\{}\{}".format(folder, item)
        minstr=int(item.split('-')[0])
        maxstr = int(item.split('-')[1])
        newfoldername="{}-{}".format(str(minstr).rjust(6,'0'),str(maxstr).rjust(6,'0'))
        if(item !=newfoldername):
            os.rename(itemfolder,"E:\ososedki\{}\{}".format(folder,newfoldername))
print("Done")
