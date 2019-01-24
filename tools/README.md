I´ve modified the shell extract_images.sh:

	- Downloads the video un_heliostato.mp4 (picked this one because it´s lightweight).
	- Creates a images folder to store all the frames extracted from the video.
	- Uses the ffmpeg library to extract 7 frames of the video with names un_heliostato_00x.png.
	- Moves the .png images to the images folder.
 
 
I´ve modified the shell get_video.sh:

	- Downloads the video un_heliostato.mp4.
 
 
I´ve added a shell setup.sh:

	- Installs ffmpeg4 library on the system.
	- Installs the python3 environment with pip.
	- Installs all the python modules to execute other .py scripts in this project
	NOTE: This will depend of the environment, this script will install on the system python3, pip3, opencv, numpy.