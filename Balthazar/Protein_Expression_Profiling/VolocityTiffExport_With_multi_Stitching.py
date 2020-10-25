from ij import WindowManager, IJ
import os, os.path, subprocess, shutil
from ij.plugin import Commands
from os import listdir
from ij.gui import WaitForUserDialog

#@ Integer (label="Select the number of imput files to be used per stitched image", style="slider", min=1, max=20, stepSize=1, value=2, persist = false) images_num_to_stitch
#@ File (label="Select a directory to process images", style="directory", value="", persist=false, required=true) parent_dir
"""
Set images_num_to_stitch to 2 or more to direct this program to stitch images in pairs (2) or triplet (3) etc
But make sure that you have imaged according!
"""
parent_dir = str(parent_dir)

images_num_to_stitch = int(images_num_to_stitch)

#images_num_to_stitch = 2 ## Number of tiff files to stitch; pairs -- 2

def main():
  #parent_dir = IJ.getDirectory("Select Parent Directory")
  file_type = ".mvd2"
  mvd2_file_list = listDir(parent_dir, file_type)

  for mvd2_file in mvd2_file_list:
    mvd2_dir = mvd2_file[0 :(mvd2_file.rfind(os.path.sep) +1)]
    tiff_dir = mvd2_dir + "tiff" + os.path.sep
    makeDir(tiff_dir)
    stitched_dir = tiff_dir + "stitched_images" + os.path.sep
    makeDir(stitched_dir)
    tiff_list = VolocityFileSave(mvd2_file, tiff_dir)
    if tiff_list:
      if "luts" in locals():
        luts = mainStitching(tiff_list, tiff_dir, stitched_dir, luts)
      else:
        luts = mainStitching(tiff_list, tiff_dir, stitched_dir, luts = "")
    else:
      continue

  Commands.closeAll()


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
    if os.path.isdir(fullPath):
      allFiles = allFiles + listDir(fullPath, file_type)
    elif fullPath.endswith(file_type):
      allFiles.append(fullPath)
  return(allFiles)

#################################################

def makeDir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)
#################################################

def VolocityFileSave(mvd2_file, tiff_dir):
  if (WindowManager.getImageCount() > 0):
    Commands.closeAll()

  IJ.run("Bio-Formats Importer", "open=[" + mvd2_file + "] autoscale color_mode=Composite open_all_series rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT")

  genotype = mvd2_file[(mvd2_file.rfind(os.path.sep) +1) : mvd2_file.rfind('.mvd2')]

  images_list = WindowManager.getImageTitles()

  if len(images_list)%2 == 1:
    print("There are odd number of images in", (genotype + ".mvd2"))
    return
  tiff_list = list()
  for i, image in enumerate(images_list):
		if i == 0:
			tiff_name = IJ.pad(i+1, 3) + "_" + genotype + ".tiff"
		else:
			image_num = image[image.rindex(" ")+1:]

			tiff_name = IJ.pad(int(image_num), 3) + "_" + genotype + ".tiff"

		tiff_save_name = tiff_dir + tiff_name
		IJ.selectWindow(image)
		imp = IJ.getImage()
		IJ.saveAsTiff(imp, tiff_save_name)
		imp.close()
		tiff_list.append(tiff_name)
  tiff_list.sort()
  return tiff_list



######################################################

def mainStitching(tiff_list, tiff_dir, stitched_dir, luts):
  temp_dir = tiff_dir + "TEMP" + os.path.sep
  #temp_dir = os.path.expanduser('~') + "/Desktop/temp_tiffs123/"
  makeDir(temp_dir)

  for i in range(0, len(tiff_list), images_num_to_stitch):
		for k in range(images_num_to_stitch):
			print(images_num_to_stitch)
			x = i + k
			shutil.copyfile(tiff_dir + tiff_list[x], temp_dir + tiff_list[x])
		
		
		luts = stitch(temp_dir, stitched_dir,luts)

  shutil.rmtree(temp_dir)
  return luts


#############################################################

def stitch(temp_dir, stitched_dir, luts):
  IJ.run("Grid/Collection stitching", "type=[Unknown position] order=[All files in directory] directory=[" + temp_dir + "] output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]")

#  wait(60000)
  b = ""
  all_files = os.listdir(temp_dir)
  all_files.sort()
  for tiff_file in all_files:
    if tiff_file.endswith(".tiff"):
      if b:
        b = b + "-" + tiff_file[:3]
      else:
        b = b + tiff_file[:3]
    os.remove(temp_dir + tiff_file)
  save_file = b + ".tiff"
  imp = IJ.getImage()

  if luts:
    imp.setLuts(luts)
  else:
    #dialog = WaitForUserDialog("Please adjust Luts & click OK to continue")
    changeColors(imp)
    dialog = WaitForUserDialog("Please adjust Luts & click OK to continue")
    dialog.show()
    luts =  imp.getLuts()

  IJ.saveAsTiff(imp, stitched_dir + save_file)
  imp.close()
  return luts

#############################################################

def changeColors(imp):
	colors = ["Green", "Red", "Magenta", "DAPI"]
	imp.setZ(1)
	for i in range(imp.NChannels):
	  IJ.run("Previous Slice [<]", "")

	for i in range(imp.NChannels):
		if i < (imp.NChannels -1):
		  IJ.run(imp, colors[i], "")
		  IJ.run("Next Slice [>]", "")
		else:
		  IJ.run(imp, colors[-1], "")



################################################

#if __name__ == '__main__':
#  main()

main()
