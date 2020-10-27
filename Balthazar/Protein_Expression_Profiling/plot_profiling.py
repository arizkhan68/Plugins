from __future__ import division
import sys, os, os.path, re, time, shutil, csv, math
from ij.process import ImageProcessor
from ij import ImagePlus, IJ, WindowManager, plugin
from ij.gui import ProfilePlot, Roi, PolygonRoi
from ij.plugin import Commands
from ij.measure import ResultsTable

#@ String (label="Please enter staining # 1", value = "") staining1
#@ String (label="Please enter staining # 2", value = "") staining2
#@ String (label="Please enter staining # 3", value = "") staining3
#@ String (label="Please enter staining # 4", value = "") staining4
#@ String (label="Please enter staining # 5", value = "") staining5
#@ String (label="Enter which staining is primary", choices={1, 2, 3, 4, 5}, style="radioButtonHorizontal", persist = true) primary_staining
#@ String (label="Process only primary antibody staining?", choices={"Yes", "No"}, style="radioButtonHorizontal", persist = true) process_only_primary
#@ String (label="Process all slices?", choices={"Yes", "No"}, style="radioButtonHorizontal", persist = true) all_slices

#@ String (label="Intensity processing method", choices={"max", "mean"}, style="radioButtonHorizontal", persist = true) intensity_to_process
#@ Integer (label="Enter minimum required cd for image processing", style="slider", min=0, max=200, stepSize=5, value=25) min_cd

#@ Integer (label="Select line width", style="slider", min=0, max=200, stepSize=5, value=75) linewidth

#@ String (visibility=MESSAGE, value="The images in the directory below will only be processed if there are no open images", required=false) msg
#@ File (label="Select a directory to process images", style="directory", value = "", persist = false) myDir

stainings = list()
for i in range(5):
	staining = eval("staining" + str(i+1))
	if staining.strip() != "":
		stainings.append(staining.strip())

primary_staining = eval("staining" + primary_staining).strip()
if primary_staining in stainings:
	primary_channel = stainings.index(primary_staining)
else:
	sys.exit("Primary staining channel is wrong")

if process_only_primary == "Yes":
	process_only_primary = True
else:
	process_only_primary = False

if all_slices == "Yes":
	all_slices = True
else:
	all_slices = False

#################################################################

IJ.run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box dots_size=5 font_size=10 show_numbers white_numbers store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=none")

IJ.run("Set Measurements...", "centroid redirect=None decimal=6")

if IJ.isResultsWindow():
  IJ.selectWindow(restults_window)
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


###############################################################
def mean(x, j):
	total = 0
	for element in x:
		print(eval(element))
	#return total


################################################################

def saveProfile(nch, top, bottom, staining, genotype, staining_dir, image_name, cd = min_cd, cd_no = 0, all_slices = False):
	if all_slices == True:
		temp_imp = IJ.getImage()
		top = temp_imp.NSlices
		bottom = 1
  
	for j in range(bottom, top+1):
	  imp1 = IJ.getImage()
	  imp1.setC(nch)
	  imp1.setZ(j)
	  pp1 = ProfilePlot(imp1)
	  s = "profile" + str(j)
	  exec(s + " = pp1.getProfile()")

	file_name = image_name[ : (image_name.rfind('.tif'))] + "_" + staining + ".csv"
	file_save = staining_dir + file_name
	if cd == 1:
	  with open(file_save, "w") as text_file:
	    text_file.write("cd,cd_type,x,value")
	#  text_file.close()
	with open(file_save, "a") as text_file:
	  for j in range(len(eval("profile" + str(top)))):
	#      print([profile1[j], profile2[j] ], max([profile1[j], profile2[j] ]))
	    x = list()
	    
	    for k in range(bottom, top+1):
	      x.append("profile" + str(k) + "[j]")
	    #print(x)
	    if intensity_to_process == "max":
	    	text_file.write("\n" + str(cd) + "," + str(cd_no) + "," + str(j) + "," + str(eval(max(x))))
	    	#print(len(x))
	    else:
	    	
	    	#print(int(len(x)))
	    	total = 0
	    	for element in x:
				total = total + eval(element)
    		text_file.write("\n" + str(cd) + "," + str(cd_no) + "," + str(j) + "," + str(total/len(x)))
	#  text_file.close()
	#print(top, bottom)

##############################################################################################
def getPoints(cd, points):
  if cd == 1:
    x1 = points[1]
    x2 = points[2]
    end = (x1 + x2)/2
    start = (2 * x1) - end
    return(int(start), int(end))
  else:
    if cd < (len(points) - 1):
      return(int((points[cd-1] + points[cd])/2), int((points[cd] + points[cd+1])/2))
    else:
      x1 = points[cd-1]
      x2 = points[cd]
      start = (x1 + x2)/2
      end = (2 * x2) - start
      return(int(start), int(end))
#############################################################################################

def processImage():
  imp = IJ.getImage()
  image_name = imp.title
  nChannels = imp.NChannels
  if process_only_primary == False:
    if nChannels != len(stainings):
      sys.exit("There are " + str(nChannels) + " channels in this image, as against " + str(len(stainings)) + " stainings you have specified. \nPlease fix this issue in the script and then re-run it?")

#  IJ.run("Save")
  image_dir = IJ.getDirectory("image")
  genotype = image_dir[0 : (len(image_dir)-1)]
  genotype = genotype[(genotype.rfind(os.path.sep)+1) : ]
  IJ.run(imp, "Measure", "")
  marker_dir = image_dir + "markers" + os.path.sep
  profile_dir = image_dir + "plot_profile" + os.path.sep
  makeDir(marker_dir, profile_dir)
  csv_file = saveResults(imp, marker_dir)
  cd_type = list(); xpoints = list(); ypoints = list(); slices = list()
  
  with open(csv_file, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for line in csv_reader:
      cd_type.append(int(float(line[5])))
      xpoints.append(int(float(line[1])))
      ypoints.append(int(float(line[2])))
      slices.append(int(line[4]))

  #start with 25
  if len(xpoints) < min_cd:
    imp.setRoi(PolygonRoi(xpoints,ypoints,Roi.POLYLINE))
    print("Not enough cds")
    imp.close()
    return()  
  start_time= time.time()
  line = "line=" + str(linewidth)
  IJ.run(imp, "Line Width...", line)
  if max(slices) == 1:
    top = 2
    bottom = 1
  else:
    top = max(slices)
    if min(slices) < top:
      bottom = min(slices)
    else:
      bottom = top - 1
  if process_only_primary == True:
    staining_dir = profile_dir + stainings[primary_channel] + os.path.sep
    makeDir(staining_dir)
  else:
    for staining in stainings:
      staining_dir = profile_dir + staining + os.path.sep
      makeDir(staining_dir)

  for cd in range(1, len(xpoints), 1):
    xpolypoints = getPoints(cd, xpoints)
    ypolypoints = getPoints(cd, ypoints)
    imp.setRoi(PolygonRoi(xpolypoints,ypolypoints,Roi.POLYLINE))
    for i, staining in enumerate(stainings):
      if process_only_primary == True and i != primary_channel:
        continue
      staining_dir = profile_dir + staining + os.path.sep
      nChannel = i + 1
      saveProfile(nChannel, top, bottom, staining, genotype, staining_dir, image_name, cd = cd, cd_no = cd_type[cd], all_slices = all_slices)

  end_time= time.time()
  print(int(end_time-start_time))
  imp.close()



def main():
  if (WindowManager.getImageCount() > 0):
    IJ.run("Save")
    processImage()
#  if (WindowManager.getImageCount() > 0):
#    for image in range(WindowManager.getImageCount()):
#      processImage()
  else:
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
    print(dir_list)
    if len(dir_list) > 0:
      for dir in dir_list:
        genotype_dirs = list()
        filenames= os.listdir (dir)
        for filename in filenames:
          if os.path.isdir(os.path.join(os.path.abspath(dir), filename)):
            genotype_dirs.append(os.path.join(os.path.abspath(dir), filename))
        for genotype_dir in genotype_dirs:
          image_list = listDir(genotype_dir, file_type = ".tiff", recursive = False)
          for image in image_list:
            IJ.open(image)
            processImage()
    else:
      image_list = listDir(selected_dir, file_type = ".tiff", recursive = False)
      for image in image_list:
        IJ.open(image)
        processImage()
main()
