# Script Issue Week 2

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

The python script allows to download a video (mp4 format), extract a specified number of frames, convert those frames to 16 bits, apply a DDWT and MCDWT transforms. Supports multi-level MCDWT and reconstruction from MCDWT and DWT.

Onced the scriped is executed, all the generated files are stored in a single folder (same as vname argument in the tmp folder). vname will be used to export the generated files and folders in tmp.

# Output Directory Structure!
-  /VideoName:
  - - /extracted
  - - /16bit
  - - /16bitreconstructed (16 bit from video normalized)
  - - /MDWT
  - - - /MCDWT (Level 1)
  - - - - /2 (Level 2)
  - - - - - /3 (Level 3)
  - - - - - - ... (Level n)
  - - /_reconMDWT (Secuence reconstructed from MCDWT and MDWT)
  - - /_reconMCDWT

# Arguments supported!

  - -h Shows help
  - -vpath path to the local video
  - -vurl video URL to download
  - -level Number of spatial resolutions to MCDWT transform (levels in the Laplacian Pyramid)
  - -vname To change the video name to the output forlder
  - -frames to select the number of images to transform

### Dependencies

Install  dependencies:

```sh
$ pip3 install pywt
$ pip3 install opencv-python
$ sudo add-apt-repository ppa:jonathonf/ffmpeg-4
$ sudo apt install ffmpeg
```

### Example

By default the script allows to download a video and extract 5 frames:

```sh
$ ./scriptW2.py
```

If you want to extract more frames add the -frames argumtent
```sh
$ ./scriptW2.py -frames 15
```

If you want to download a video
```sh
$ ./scriptW2.py -vurl http://www.hpca.ual.es/~vruiz/videos/un_heliostato.mp4
```

Working with a local video, MANDATORY .MP4 VIDEO EXTENSION
```sh
$ ./scriptW2.py -vpath un_heliostato.mp4 -frames 20 -vname un_heliostato
```

Multi-level MCDWT is also posible
```sh
$ ./scriptW2.py -level 4 -frames 10
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
