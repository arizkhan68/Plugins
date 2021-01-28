dir = getDirectory("image");
image_name = getTitle();
csv_file = substring(image_name, 0, lastIndexOf(image_name, ".tif")) + ".csv";
csv_file = dir + csv_file
filestring=File.openAsString(csv_file);
rows=split(filestring, "Z\n");
colors = newArray("orange", "white", "green", "lightGray", "yellow", "red", "gray", "magenta", "blue", "cyan", "darkGray", "magenta", "pink", "black");

//x = newArray(rows.length);
//y=newArray(rows.length);
//channel = newArray(rows.length);
//slice = newArray(rows.length);
for(i=0; i<rows.length; i++){
	columns=split(rows[i],",");
//	x[i]=parseInt(columns[1]);
//	y[i]=parseInt(columns[2]);
//	channel[i]=parseInt(columns[3]);
//	slice[i]=parseInt(columns[4]);
	Stack.setChannel(columns[3]);
	Stack.setSlice(columns[4]);
	if (columns.length > 5){
		if (columns[5] < colors.length ){
			text = "dot large add label " + colors[columns[5]];
		}
		
	}else{
		text = "dot large add label orange";
	}
	setKeyDown("shift"); makePoint(columns[1], columns[2], text);
	//Overlay.drawLabels(true);
}