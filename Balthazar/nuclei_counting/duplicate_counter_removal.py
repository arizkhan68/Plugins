"""
Make sure you have setRoi_.ijm file in Fiji.app/scripts/Plugins folder

"""

from __future__ import division
import os, os.path, math, copy
from ij import ImagePlus, IJ, WindowManager
from collections import Counter
#from java.awt.event import KeyEvent



#@ Integer (label="Select the threshold value, distnace in pixel, below which points should be ignored", style="slider", min=5, max=100, stepSize=1, value=10, persist = true) threshold
#@ File (label="Select a directory to process images", style="directory", value = "", persist = false) selected_dir

#################################################################
IJ.run("Set Measurements...", "centroid redirect=None decimal=2")

if IJ.isResultsWindow():
	IJ.selectWindow("Results")
	IJ.run("Close")

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
		if fullPath.endswith(file_type[0]) or fullPath.endswith(file_type[1]):
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

def getSummary(csv_file, summary_array, tiff_name, max_counter):
	f = open(csv_file, 'r')
	top = f.readline()
	line = f.readline()
	list1 = list()
	delim = ','
	#line variable contains the first data row
	while(line != ""):
		split = line.split(delim)
		if len(split) < 6:
			list1.append(0)
		else:
			list1.append(split[5])
		line = f.readline()
	list1.sort()
	if list1[-1] > max_counter:
		max_counter = list1[-1]
	list1.insert(0, tiff_name)
	summary_array.append(list1)
	f.close()
	return summary_array, max_counter

#################################################
def summarize(path):
	summary_dir = os.path.join(os.path.dirname(path), "summary_files" +os.path.sep)
	makeDir(summary_dir)
	summary_file = os.path.join(summary_dir, os.path.basename(path) +".csv")

	csv_file_list = listDir(path, [".csv", ".csv"], False)
	summary_array = []
	max_counter = 0
	for csv_file in csv_file_list:
		tiff_name = os.path.basename(csv_file).replace(".csv", ".tiff")
		summary_array, max_counter = getSummary(csv_file, summary_array, tiff_name, max_counter)

	header = [("counter_" + str(i)) for i in range(max_counter+1)]
	header.insert(0, "image")
	write_array = list()
	write_array.append(header)

	for x in summary_array:
		tiff_name = x.pop(0)
		counter_dict = dict((i,x.count(i)) for i in set(x))
		new_list = [tiff_name]
		for i in range(max_counter + 1):
			if counter_dict.get(i) is not None:
				new_list.append(counter_dict.get(i))
			else:
				new_list.append(0)

		write_array.append(new_list)

	delim = ','
	writeFile = open(summary_file, 'w')
	for i in range(len(write_array)):
		curr_point = write_array[i]
		text = ""
		for j in range(len(curr_point)):
			text = text + str(curr_point[j]) + str(delim)
		text = text[:-1] + "\n"
		writeFile.write(text)

	writeFile.close()

##################################################

def saveResults(imp, directory):
	current_image = imp.title
	a = current_image[ : current_image.rfind(".tif")]
	csv_file = os.path.join(directory, a + ".csv")
	print(csv_file)
	IJ.saveAs("Results", csv_file)
	IJ.selectWindow("Results")
	IJ.run("Close")
	return(csv_file)
#################################################

def dist_formula(x1, y1, x2, y2):
	return math.sqrt(pow(x2-x1, 2) + pow(y2 - y1, 2))

#######################################################################

def remove_duplicate_counter(temp_file, directory):
	filename = temp_file
	temp_file = os.path.basename(temp_file)
	mod_file = os.path.join(directory, temp_file)
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

	writeFile = open(mod_file, 'w')
	writeArray = []
	while(len(list) != 0):
		OriginX = float(list[0][0])
		OriginY = float(list[0][1])
		writeArray.append(list[0])

		curr_slice = int(list[0][3])
		list.pop(0)
		temp_list = copy.copy(list)
		pop = 0
		#print(len(temp_list))
		for i in range(len(list)):
			x = int(list[i][3])
			if curr_slice != x and (x - curr_slice) < 3:

				newX = float(list[i][0])
				newY = float(list[i][1])
				dist = dist_formula(OriginX, OriginY, newX, newY)

				if dist < threshold:
					#print(i+pop)
					temp_list.pop(i - pop)
					pop = pop + 1

			elif (x - curr_slice) > 2:

				#print(length(list))
				break
		list = copy.copy(temp_list)
		#list = temp_list

	#iterator should point to the closest elemnt to origin point...
	#added to write array in the next loop through

	#writeArray = arrayCheck(writeArray)
	writeFile.write(top)
	#print(writeArray)
	for i in range(len(writeArray)):
		curr_point = writeArray[i]
		text = str(i+1)
		for j in range(len(curr_point)):
			text = text + str(delim) + curr_point[j]
		writeFile.write(text)

	f.close()
	writeFile.close()
###############################################
def processImage():
	imp = IJ.getImage()
	image_name = imp.title
	image_dir = IJ.getDirectory("image")
	IJ.run(imp, "Measure", "")
	marker_dir = os.path.join(image_dir, "markers" + os.path.sep)
	processed_marker_dir = os.path.join(image_dir, "processed_markers" + os.path.sep)
	makeDir(marker_dir, processed_marker_dir)
	csv_file = saveResults(imp, marker_dir)
	imp.deleteRoi()

	tiff_save_name = os.path.join(processed_marker_dir, image_name)
	IJ.saveAsTiff(imp, tiff_save_name)
	remove_duplicate_counter(csv_file, processed_marker_dir)
#	file_dir = os.path.dirname(os.path.abspath(__file__))
	IJ.run(imp, "setRoi ", "");
	IJ.run("Save")
	imp.close()
	return image_dir


#############################################################

def main():
	#summary = False
	if (WindowManager.getImageCount() > 0):
		IJ.run("Save")
		image_dir = processImage()
#	if (WindowManager.getImageCount() > 0):
#		for image in range(WindowManager.getImageCount()):
#			processImage()
	else:
		#summary = True
		#selected_dir = IJ.getDirectory("Select Directory")
		if not selected_dir.endswith(os.path.sep):
			selected_dir = selected_dir + os.path.sep

		dir_list = list()
		file_type = [".tif", ".tiff"]
		image_list = listDir(selected_dir, file_type = file_type, recursive = False)
		for image in image_list:
			IJ.open(image)
			image_dir = processImage()

	summarize(os.path.join(image_dir, "markers" ))
	summarize(os.path.join(image_dir, "processed_markers"))
main()
