#  Adaptive motion compensation based on the distortion of the prediction error

## Commands to use:

1. python3 -O ./MDWT.py -i ../sequences/stockholm/ -d /tmp/stockholm_  

* **python3** is the version of python.
* **-O** is used to not show the debug log.
* **-i** is the image sequences path (in this example ../sequences/stockholm/).
* **-d** is the result path (in this example /tmp/stockholm_).

2. python3 -O MCDWT.py -d /tmp/stockholm_ -m /tmp/mc_average_stockholm_

* **python3** is the version of python.
* **-O** is used to not show the debug log.
* **-d** is the image input path (in this example /tmp/stockholm_).
* **-m** is the result path (in this example /tmp/mc_average_stockholm_).

3. python3 -O MCDWT.py -p 2 -d /tmp/stockholm_ -m /tmp/mc_prediction_stockholm_

* **python3** is the version of python.
* **-O** is used to not show the debug log.
* **-p** is the method used, in this case 2 is the prediction method.
* **-d** is the image input path (in this example /tmp/stockholm_).
* **-m** is the result path (in this example /tmp/mc_prediction_stockholm_).

## Review of the result:

To check the entropy of the output generated, the show_statistics code is called for each subband.

1. for i in /tmp/mc_average_stockholm_*;do python3 ../tools/show_statistics.py  -i $i ;done; 

2. for i in /tmp/mc_prediction_stockholm_*;do python3 ../tools/show_statistics.py  -i $i ;done; 

The output of this commands are located in docs/issue3_stats_average.txt and issue3_stats_prediction.txt

With the sequences of images used there isn't many differences in the entropy value. 

