from ij import IJ
import os.path

#imp = IJ.getImage()
#image_title = imp.title
#image_title = image_title.split(".")

#if image_title[0].endswith("-1"):
#  sys.exit("Image is already duplicated")

dir1 = IJ.getDirectory("image")
IJ.run("Duplicate...", "duplicate")
imp = IJ.getImage()
dup_image_title = imp.title
image_save = os.path.join(dir1, dup_image_title)
IJ.saveAsTiff(imp, image_save)