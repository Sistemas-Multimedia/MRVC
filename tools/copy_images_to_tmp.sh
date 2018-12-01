set -x
let i=0
for f in ../images/*.png
do
    _i_=$(printf "%03d" $i)
    ./add_32768_128.py ../images/$_i_.png /tmp/${_i_}_0_LL.png # image_scale
    ((i++))
done
set +x
