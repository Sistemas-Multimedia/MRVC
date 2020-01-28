# Script Issue Week 2

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

The python script allows to download a video (mp4 format), extract a specified number of frames, convert those frames to 16 bits, apply a DDWT and MCDWT transforms. Supports multi-level MCDWT and reconstruction from MCDWT and DWT.

Once the script is executed, all the generated files are stored in a single folder (same as vname argument in the tmp folder). vname will be used to export the generated files and folders in tmp.

The most important parameter is -transform, if True the script will apply the direct transform. If False, the backwards transform is applied. Default is True.

To reconstruct, make sure to pass the same parameters (frames, vname, T) as the direct transform.

# Output Directory Structure!
-  /VideoName:
  - - /extracted
  - - /16bit
  - - /16bitreconstructed (16 bit from video normalized)
  - - /MDWT
  - - - /MCDWT
  - - - - /1 (Level 1 by default)
  - - - - /2 (Level 2)
  - - - - /n...
  - - /_reconMCDWT
  - - - /1 (Reconstruction from MCDWT level 1 by default)
  - - - /2 (Reconstruction from MCDWT level 2)
  - - - /n...
  - - /_reconMDWT (Sequence reconstructed)


# Arguments supported!

  - -h Shows help
  - -vpath path to the local video
  - -vurl video URL to download
  - -level Number of spatial resolutions to MCDWT transform (levels in the Laplacian Pyramid) default 1
  - -T Number of levels of the MCDWT (temporal scales) 2 by default.
  - -vname To change the video name to the output folder.
  - -frames to select the number of images to transform, 5 by default.
  - -transform To specified the direct transform or reconstruction, True by default.

### Dependencies

Install  dependencies:

```sh
$ pip3 install pywt
$ pip3 install opencv-python
$ sudo add-apt-repository ppa:jonathonf/ffmpeg-4
$ sudo apt install ffmpeg
```

### Example

By default the script allows to download a video and extract 5 frames to the direct transform:

```sh
$ ./scriptv2.py
```

To reconstruct the images from the video, activate the -transform False flag.

```sh
$ ./scriptv2.py -transform False
```

If you want to extract more frames add the -frames argument.
```sh
$ ./scriptv2.py -frames 15
```

If you want to download a video to transform from the web
```sh
$ ./scriptv2.py -vurl http://www.hpca.ual.es/~vruiz/videos/un_heliostato.mp4
```

Working with a local video, MANDATORY .MP4 VIDEO EXTENSION
```sh
$ ./scriptv2.py -vpath un_heliostato.mp4 -frames 20 -vname un_heliostato
```

Multi-level MCDWT is also possible with T temporal spaces.
```sh
$ ./scriptv2.py -level 4 -frames 10 -T 3
```


### Issues to be solved

  - Right now only supports MP4 video format



   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
