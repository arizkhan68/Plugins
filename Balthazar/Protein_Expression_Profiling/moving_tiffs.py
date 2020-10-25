from ij import WindowManager, IJ
import os, os.path, shutil, sys
from ij.io import OpenDialog
#@ PrefService prefs
from fiji.util.gui import GenericDialogPlus

################################################
# Obtained from https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/ 
#non-recursive version

def listDir(dirName, file_type, recursive = False):
  # create a list of file and sub directories 
  # names in the given directory 
  listOfFile = os.listdir(dirName)
  allFiles = list()
  # Iterate over all the entries
  for entry in listOfFile:
    # Create full path
    fullPath = os.path.join(dirName, entry)
    # If entry is a directory then get the list of files in this directory 
    if fullPath.endswith(file_type) or fullPath.endswith(file_type + os.path.sep):
        allFiles.append(fullPath)
    elif recursive:
      if os.path.isdir(fullPath):
            allFiles = allFiles + listDir(fullPath, file_type, recursive = True)
  return(allFiles)

##############################################
def makeDir(*directories):
  for directory in directories:
    if not os.path.exists(directory):
      os.makedirs(directory)

#################################################
def getTiffName(j, tiffs_per_image):
	x = tiffs_per_image * (j + 1) - (tiffs_per_image - 1)
	tif_file_name = ""
	for m in range(tiffs_per_image):
		tif_file_name = tif_file_name + str(x).zfill(3) + "-"
		x = x + 1
	tif_file_name = tif_file_name.rstrip("-")  + ".tiff"
	return tif_file_name

######################################################

def getOptions():
	gui = GenericDialogPlus("Options for Moving TIFF files")
	gui.addMessage("Select the number of imput files to be used per stitched image")
	gui.addSlider("", 2, 10, 2)
	gui.addFileField("Select csv file", "")
	gui.addMessage("Add key values and corresponding genotype, when finished, leave fields empty")
	gui.addStringField("Key :", prefs.get(None, "key1", "p"))
	gui.addToSameRow()
	gui.addStringField("Genotype :", prefs.get(None, "genotype1", "PROM-1_HA"))
	gui.addStringField("Key :", prefs.get(None, "key2", "p"))
	gui.addToSameRow()
	gui.addStringField("Genotype :", prefs.get(None, "genotype2", "PROM-1_HA"))
	gui.addStringField("Key :", prefs.get(None, "key3", "p"))
	gui.addToSameRow()
	gui.addStringField("Genotype :", prefs.get(None, "genotype3", "PROM-1_HA"))
	gui.addStringField("Key :", prefs.get(None, "key4", "p"))
	gui.addToSameRow()
	gui.addStringField("Genotype :", prefs.get(None, "genotype4", "PROM-1_HA"))
	gui.addStringField("Key :", prefs.get(None, "key5", "p"))
	gui.addToSameRow()
	gui.addStringField("Genotype :", prefs.get(None, "genotype5", "PROM-1_HA"))
	gui.showDialog() 

	if gui.wasOKed():
		tiffs_per_image = int(gui.getNextNumber())
		csv_file = str(gui.getNextString())
		genotypes = {}
		for i in range(5):
			key = str(gui.getNextString())
			value = str(gui.getNextString())
			if key != "":
				genotypes[key] = value
	else:
		return
	if len(genotypes) > 0:
		a = list(genotypes.items())[0]
		prefs.put(None, "key1", a[0])
		prefs.put(None, "genotype1", a[1])
	if len(genotypes) > 1:
		a = list(genotypes.items())[1]
		prefs.put(None, "key2", a[0])
		prefs.put(None, "genotype2", a[1])
	if len(genotypes) > 2:
		a = list(genotypes.items())[2]
		prefs.put(None, "key3", a[0])
		prefs.put(None, "genotype3", a[1])
	if len(genotypes) > 3:
		a = list(genotypes.items())[3]
		prefs.put(None, "key4", a[0])
		prefs.put(None, "genotype4", a[1])
	if len(genotypes) > 4:
		a = list(genotypes.items())[4]
		prefs.put(None, "key5", a[0])
		prefs.put(None, "genotype5", a[1])
	return tiffs_per_image, csv_file, genotypes

######################################################
def moveFiles():
	tiffs_per_image, csv_file, genotypes = getOptions()
	#print(tiffs_per_image, csv_file, genotypes)
	fileName = csv_file
	f = open(fileName, 'r')
	top = f.readline()
	line = f.readline()
	list = []
	delim = ','
	#line variable contains the first data row
	while(line != ""):
		split = line.split(delim)
		split.pop(0)
		for i in range(len(split)):
			split[i] = genotypes.get(split[i].strip()) #strip to remove newline character
		list.append(split)
		line = f.readline()
	top = top.split(delim)
	top.pop(0)
	for i in range(len(top)):
		csv_dir = os.path.dirname(csv_file)
		replicate_dir = os.path.join(csv_dir, "replicate_" + str(i+1) + os.path.sep)
		file_type = "stitched_images"
		stitched_images_dir = listDir(replicate_dir, file_type, True)
		print(stitched_images_dir[0])
		for j in range(len(list)):
			tif_file_name = getTiffName(j, tiffs_per_image)
			if list[j][i] != None:
				#print(tif_file_name, list[j][i])
				makeDir(os.path.join(stitched_images_dir[0], list[j][i]))
				#print(os.path.join(stitched_images_dir[0], tif_file_name), os.path.join(stitched_images_dir[0], list[j][i], tif_file_name))
				shutil.move(os.path.join(stitched_images_dir[0], tif_file_name), os.path.join(stitched_images_dir[0], list[j][i], tif_file_name))
	f.close()		
##################################################################################


moveFiles()


	