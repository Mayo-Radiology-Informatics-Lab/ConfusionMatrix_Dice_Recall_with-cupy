# Confusion matrix, dice, accuracy with cupy
Scikitlearn 'confusion matrix' extraction is very slow for digital pathology images of 30k x 30k pixels. Instead cupy library with matrix multiplication could be used to speed up the calculation. 

Need cupy library; check for correct version compatible with your cudatoolkit. <b/>
https://pypi.org/project/cupy/ 

Use Metric_withcupy.py to calculate metric and save in new folder. <b/>


Use Metric_dicecupy_average.py to take average of all files. <b/>
