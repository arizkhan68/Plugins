from __future__ import division
import os, os.path, shutil, csv, math
from ij.process import ImageProcessor
from ij import ImagePlus, IJ, WindowManager
from ij.plugin import Commands


#@ File (label="Select a directory to process images", style="directory", value = "", persist = false) myDir

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

#################################################

def makeDir(*directories):
  for directory in directories:
    if not os.path.exists(directory):
      os.makedirs(directory)
#################################################

def saveResults(imp, directory):
  current_image = imp.title
  a = current_image[ : current_image.rfind(".tif")]
  csv_file = directory + a + ".csv"
  IJ.saveAs("Results", csv_file)
  IJ.selectWindow("Results")
  IJ.run("Close")
  sortPoints(a + ".csv", directory)
  return(csv_file)
#################################################

def dist_formula(x1, y1, x2, y2):
  return math.sqrt(pow(x2-x1, 2) + pow(y2 - y1, 2))
################################################################################

def arrayCheck(writeList):
	# writeList is an array of arrays // list of lists
	# an addendum to sortPoints... correction measure
	j = len(writeList) - 1
	ME = 4 # Margin of Error
	while j > 1:
		fClosestIndex = -1
		fClosestDist = 100000000
		sClosestIndex = -1
		sClosestDist = 1000000000

		OriginX = float(writeList[j][0])
		OriginY = float(writeList[j][1])
		# finds first and second closest points on the
		for i in range(len(writeList)):
			newX = float(writeList[i][0])
			newY = float(writeList[i][1])
			if OriginX == newX and OriginY == newY:
				continue # Orign and new are the same points... therefore it is skipped...
			dist = dist_formula(OriginX, OriginY, newX, newY)
			if dist < fClosestDist:
				sClosestDist = fClosestDist
				sClosestIndex = fClosestIndex
				fClosestDist = dist
				fClosestIndex = i
			elif dist < sClosestDist:
				sClosestDist = dist
				sClosestIndex = i

		# at this point, we've found the two closest points....
		# now check if those two points are in the vicinity of the OriginX
		# if yes, then we end the loop and assume that the list is fully fixed
		# if no, the we place it where it belongs...

		if (((sClosestIndex > j - ME) and (sClosestIndex < j + ME )) and ( (fClosestIndex > j - ME) and (fClosestIndex < j + ME) )): # the two points are within two of the current point
			return writeList

		# If you've made it this far, it means that a switch must occur...
		element = writeList[j]
		writeList.pop(j)
		index = int((sClosestIndex + fClosestIndex) / 2)
		writeList.insert(index, element)

##################################################################################

def sortPoints(temp_file, directory):
	filename = directory + temp_file
	f = open(filename, 'r')
	top = f.readline()
	line = f.readline()
	list = []
	delim = ','
	#line variable contains the first data row
	while(line != ""):
		split = line.split(delim)
		split.pop(0)
		list.append(split)
		line = f.readline()
	mod_file = directory + '_mod' + temp_file
	writeFile = open(mod_file, 'w')
	writeArray = []
	iterator = 0

	while(len(list) != 0):
		maxDist = 100000000000
		OriginX = float(list[iterator][0])
		OriginY = float(list[iterator][1])
		writeArray.append(list[iterator])

		list.pop(iterator)
		for i in range(len(list)):
		  newX = float(list[i][0])
		  newY = float(list[i][1])
		  dist = dist_formula(OriginX, OriginY, newX, newY)
		  if dist < maxDist:
		    maxDist = dist
		    iterator = i
	#iterator should point to the closest elemnt to origin point...
	#added to write array in the next loop through

	writeArray = arrayCheck(writeArray)
	writeFile.write(top)
	for i in range(len(writeArray)):
	    writeFile.write(str(i) + str(delim) + str(writeArray[i][0])+ str(delim) + str(writeArray[i][1]) + str(delim) + str(writeArray[i][2]) + str(delim) + str(writeArray[i][3]) + str(delim) + str(writeArray[i][4]) + str(delim) + str(writeArray[i][5]))

	f.close()
	writeFile.close()
	os.remove(filename)
	os.rename(mod_file, filename)

#############################################################################################

def processImage():
  imp = IJ.getImage()
  image_name = imp.title
  image_dir = IJ.getDirectory("image")
  IJ.run(imp, "Measure", "")
  marker_dir = image_dir + "markers" + os.path.sep
  makeDir(marker_dir)
  csv_file = saveResults(imp, marker_dir)
  IJ.selectWindow(image_name)
  IJ.run("Close")

#############################################################################
def remove_marker_dir(curr_dir):
  directory = os.path.join(curr_dir, "markers")
  if os.path.exists(directory):
    shutil.rmtree(directory)

####################################################################################
def main():
  if IJ.isResultsWindow():
    IJ.selectWindow("Results")
    IJ.run("Close")
  if (WindowManager.getImageCount() > 0):
    #IJ.run("Save")
    Commands.closeAll()

  selected_dir = str(myDir)
  if not selected_dir.endswith(os.path.sep):
    selected_dir = selected_dir + os.path.sep
  dir_list = list()
  file_type = "stitched_images"
  if selected_dir.endswith(file_type + os.path.sep):
    dir_list.append(selected_dir)
    #print(dir_list)
  else:
    dir_list = listDir(selected_dir, file_type, recursive = True)
#  print(dir_list)

  if len(dir_list) > 0:
    for dir in dir_list:
      image_list = listDir(dir, file_type = ".tiff", recursive = False)
      remove_marker_dir(dir)
      for image in image_list:
        IJ.open(image)
        processImage()
  else:
    image_list = listDir(selected_dir, file_type = ".tiff", recursive = False)
    remove_marker_dir(selected_dir)
    for image in image_list:
      IJ.open(image)
      processImage()
######################################################################################

main()
