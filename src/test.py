#matplotlib inline

import matplotlib
import matplotlib.pyplot as plt

q_step_list = [32, 64, 128]
compression_ratio_list=[]
for q_step in q_step_list:

	predictor=2  
	select=1
# You must be in the ’src’ directory.  
rm /tmp/*.png  
cp ../sequences/stockholm/* /tmp  
rm -rf /tmp/org
mkdir /tmp/org
cp /tmp/*.png /tmp/org

python3 -O MDWT.py -p /tmp/  
python3 -O MCDWT.py -P $predictor -p /tmp/  

    
#python3 ../tools/show_statistics.py -i /tmp/LH001.png  
python3 ../tools/quantize1.py -i /tmp/LH001.png -o /tmp/LH001.png -q $q_step -s $select
#python3 ../tools/show_statistics.py -i /tmp/LH001.png  
python3 ../tools/quantize1.py -i /tmp/HL001.png -o /tmp/HL001.png -q $q_step -s $select
python3 ../tools/quantize1.py -i /tmp/HH001.png -o /tmp/HH001.png -q $q_step -s $select
 
python3 ../tools/quantize1.py -i /tmp/LH002.png -o /tmp/LH002.png -q $q_step -s $select
python3 ../tools/quantize1.py -i /tmp/HL002.png -o /tmp/HL002.png -q $q_step -s $select
python3 ../tools/quantize1.py -i /tmp/HH002.png -o /tmp/HH002.png -q $q_step -s $select
 
python3 ../tools/quantize1.py -i /tmp/LH003.png -o /tmp/LH003.png -q $q_step -s $select
python3 ../tools/quantize1.py -i /tmp/HL003.png -o /tmp/HL003.png -q $q_step -s $select
python3 ../tools/quantize1.py -i /tmp/HH003.png -o /tmp/HH003.png -q $q_step -s $select

rm -rf /tmp/mcdw
mkdir /tmp/mcdw
cp /tmp/LL*.png /tmp/mcdw  
cp /tmp/LH*.png /tmp/mcdw  
cp /tmp/HL*.png /tmp/mcdw  
cp /tmp/HH*.png /tmp/mcdw 

first_compressed_ratio= !calc `wc -c /tmp/org/*.png | cut -f 1 -d " "` / `wc -c /tmp/mcdw/*.png | cut -f 1 -d " "`
compressed_ratio = float(first_compressed_ratio[0][2:])
print "compressed_ratio=" compressed_ratio
python3 -O MCDWT.py -P $predictor -p /tmp/ -b  
python3 -O MDWT.py -p /tmp/ -b  
 
for i in /tmp/00?.png; do python3 ../tools/substract_offset.py -i $i -o $i.png; done; animate /tmp/00?.png.png  
 
rm -f /tmp/diff*.png
for i in {0..4}; do ii=$(printf "%03d" $i); bash ../tools/show_differences.sh -1 /tmp/$ii.png -2 ../sequences/stockholm/$ii.png -o /tmp/diff_$ii.png; done; animate /tmp/diff*.png  
 
for i in {0..4}; do ii=$(printf "%03d" $i); MSE=`python3 -O ../tools/MSE.py -x ../sequences/stockholm/$ii.png -y /tmp/$ii.png`; printf "MSE(%s)=%s\n" $ii $MSE; done
compression_ratio_list.add(compressed_ratio)



plt(q_step_list,compression_ratio_list)

