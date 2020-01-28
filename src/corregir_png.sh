#!/bin/bash
entrada=$1
d=0;
for i in /tmp/$entrada/0??.png; do 
  mv $i /tmp/$entrada/00$d.png; d=$((d+1));
done
