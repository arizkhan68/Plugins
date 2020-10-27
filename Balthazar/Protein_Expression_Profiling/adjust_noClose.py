from ij import WindowManager, IJ
#import time

imp = IJ.getImage()
current_image = imp.title
luts =  imp.getLuts()

open_images = WindowManager.getImageTitles()

for image in open_images:
  IJ.selectWindow(image)
  imp = IJ.getImage()
  imp.setLuts(luts)
  IJ.run(imp, "Next Slice [>]", "")
  IJ.run("Save")
  #imp.close()
  #time.sleep(1)

IJ.selectWindow(current_image)