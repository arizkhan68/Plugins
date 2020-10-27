from ij import WindowManager, IJ
import os, os.path, shutil
##################################################
def makeDir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)
################################################
def getFiles(dirName, file_type):
  listOfFile = os.listdir(dirName)
  for entry in listOfFile:
    if entry.startswith(file_type):
      fullPath = os.path.join(dirName, entry)
      return(fullPath)
################################################
# Obtained from https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/ 

def listDir(dirName, file_type):
  # create a list of file and sub directories 
  # names in the given directory 
  listOfFile = os.listdir(dirName)
  allFiles = list()
  # Iterate over all the entries
  for entry in listOfFile:
	  # Create full path
	  fullPath = os.path.join(dirName, entry)
	  # If entry is a directory then get the list of files in this directory 
	  if fullPath.endswith(file_type):
			allFiles.append(fullPath)

  return(allFiles)

#################################################

#################################################
def stitch(tiff_list, temp_dir):
	for i in range(1, len(tiff_list), 2):
		tiff_1 = tiff_list[i-1]
		tiff_2 = tiff_list[i]
		pairwise_stitching(tiff_1, tiff_2, temp_dir)

	return(listDir(temp_dir, ".tiff"))

#################################################

def pairwise_stitching(tiff_1, tiff_2, temp_dir):
	IJ.open(tiff_1)
	tiff_1_title = os.path.basename(tiff_1)
	IJ.open(tiff_2)
	tiff_2_title = os.path.basename(tiff_2)
	new_fused_image = "" + tiff_1_title.split("_")[0] + "-" + tiff_2_title.split("_")[0] + "_.tiff"

	IJ.run("Pairwise stitching", "first_image=" + tiff_1_title +  " second_image=" + tiff_2_title + " fusion_method=[Linear Blending] fused_image=" + new_fused_image + " check_peaks=1 compute_overlap x=0.0000 y=0.0000 z=0.0000 registration_channel_image_1=[Average all channels] registration_channel_image_2=[Average all channels]")
	IJ.selectWindow(tiff_1_title)
	IJ.run("Close")
	os.remove(tiff_1)
	IJ.selectWindow(tiff_2_title)
	IJ.run("Close")
	os.remove(tiff_2)
	IJ.selectWindow(new_fused_image)
	imp = IJ.getImage()
	IJ.saveAsTiff(imp, os.path.join(temp_dir, new_fused_image))
	imp.close()
	
#################################################

image_dir = IJ.getDirectory("image")
imp = IJ.getImage()
image_title = imp.title
luts =  imp.getLuts()
IJ.run("Close")
tiff_dir = os.path.dirname(image_dir)
while not tiff_dir.endswith("tiff"):
	tiff_dir = os.path.dirname(tiff_dir)
print(tiff_dir)
temp_dir = os.path.join(tiff_dir, "TEMP")
makeDir(temp_dir)
images = image_title.replace(".tiff", "")
images = images.split("-")
tiff_image_list = list()

for image in images:
	tiff = getFiles(tiff_dir, image)
	shutil.copyfile(tiff, os.path.join(temp_dir, os.path.basename(tiff)))
	tiff_image_list.append(os.path.join(temp_dir, os.path.basename(tiff)))


while len(tiff_image_list) > 1:
	tiff_image_list = stitch(tiff_image_list, temp_dir)
print(tiff_image_list[0])
shutil.copyfile(tiff_image_list[0], os.path.join(image_dir, image_title))
shutil.rmtree(temp_dir)

IJ.open(os.path.join(image_dir, image_title))
imp = IJ.getImage()
imp.setLuts(luts)
IJ.run("Save")
IJ.run(imp, "Next Slice [>]", "")

