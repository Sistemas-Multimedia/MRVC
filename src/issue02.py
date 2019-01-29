#!/usr/bin/env python
import subprocess
import sys
"""subprocess.run(["bash","./test_sum_sub.sh","10"])"""
subprocess.call(["bash", 'test_sum_sub.sh 24'])

subprocess.call("./DWT.py -i /tmp/issues02/0000 -d /tmp/issues02/0000", shell=True)