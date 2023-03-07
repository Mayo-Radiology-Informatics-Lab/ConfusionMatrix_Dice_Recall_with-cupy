#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 15:39:20 2023
THIS CODE USES CUPY AND MATRIX MULTIPLICATION FOR CALCULATING DICE, CONFUSION MATRIX. SCIKITLEARN CONFUSION MATRIX COULD TAKE 4-5HRS WHERE THIS CAN BE DONE IN 2-3 MIN WITH THIS CODE.
@author: JAIDIP JAGTAP
"""

import os
import numpy as np
from tqdm import *
from skimage import morphology
os.environ["CUDA_VISIBLE_DEVICES"]='0'
#Edit the following two...
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(pow(2,40))
import cv2
import cupy as cp


segmask_folder='/GROUNDTRUTH_MASKFOLDER/' 
predmask_folder='/PREDICTED_MASKFOLDER/'

Metric_output =r"/SAVE_CALCULATED_METRIC/"

   
if not os.path.exists(Metric_output):
    os.makedirs(Metric_output)


oriprefix = '_glomtuftmaskGT.png' #'_NIFTI.nii.gz'
count = 0
subdir, dirs, files = os.walk(segmask_folder).__next__()
files = [k1 for k1 in files if oriprefix in k1]
files=sorted(files)



strremove = -len(oriprefix)
segprefix = '.svs_glomtuft5xmask.png' #'.nii.gz'
DI_av=[]
#Now loop through files and build up numpy arrays
for filename in tqdm(files):
    if 'npz' not in filename:
        dice=[];accuracy=[]; precision=[]; recall=[];true_positives=[];false_negative_rate=[]
        count+=1
        pre,ext=filename.rsplit('_', 1)
        print(filename)
        pred_fname=os.path.join(predmask_folder, pre+segprefix)
        
        if os.path.exists(Metric_output+pre+segprefix+'.npz'):
            print(f"Skipping as output file exists: \t {filename}")
            continue        
        print(f"working on file: \t {filename}")
        np.savez(Metric_output+pre+segprefix+'.npz', np.zeros(shape=(1, 1)))       
        
        
        true_label = cv2.imread(segmask_folder+filename, cv2.COLOR_BGR2GRAY)            
        pred_mask = cv2.imread(pred_fname, cv2.COLOR_BGR2GRAY) #[:strremove]+'_Seg_crop20k.nii.gz'#processed1   _predseg       
        
        user_input = 'no'#input("Do you want to remove small area/false positives? (yes) ")
        if user_input.lower() == "yes":
            img_out=pred_mask.astype('uint8')
            er1=img_out>0 # boolean input needed
            r1=morphology.remove_small_objects(er1, min_size=5, connectivity=8)
            img=(r1*1).astype('uint8')

        else:
           img=pred_mask.astype('uint8')

    
        
        
        # Move matrices to GPU
        matrix1_gpu = cp.asarray(true_label)
        matrix2_gpu = cp.asarray(img)
        
        # Calculate true positives, false negatives, and false positives
        true_positives = cp.sum(matrix1_gpu * matrix2_gpu)
        false_negatives = cp.sum(matrix1_gpu * (1 - matrix2_gpu))
        false_positives = cp.sum((1 - matrix1_gpu) * matrix2_gpu)
        
        # Calculate metrics
        dice = (2 * true_positives) / (2 * true_positives + false_negatives + false_positives)
        accuracy = (true_positives + cp.sum(1 - matrix1_gpu) - false_positives) / matrix1_gpu.size
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        true_positive_rate = true_positives / (true_positives + false_negatives)
        false_negative_rate = false_negatives / (true_positives + false_negatives)
        
        # Calculate confusion matrix
        confusion_matrix = np.zeros((2, 2))
        confusion_matrix[0, 0] = true_positives
        confusion_matrix[0, 1] = false_positives
        confusion_matrix[1, 0] = false_negatives
        confusion_matrix[1, 1] = cp.sum((1 - matrix1_gpu) * (1 - matrix2_gpu))

        # confusion_matrix_normalized = confusion_matrix.astype('float') / confusion_matrix.sum(axis=1)[:, np.newaxis]
               
        # Save metrics and confusion matrix to NumPy file
        
        np.savez(Metric_output+pre+segprefix, dice=dice, accuracy=accuracy, precision=precision, recall=recall, true_positive_rate=true_positive_rate, false_negative_rate=false_negative_rate, confusion_matrix=confusion_matrix)
        

        '''
        # Move metrics back to CPU
        dice = cp.asnumpy(dice)
        accuracy = cp.asnumpy(accuracy)
        precision = cp.asnumpy(precision)
        recall = cp.asnumpy(recall)
        true_positive_rate = cp.asnumpy(true_positive_rate)
        false_negative_rate = cp.asnumpy(false_negative_rate)
        
        
        # Print metrics
        print("Dice coefficient:", dice)
        print("Accuracy:", accuracy)
        print("Precision:", precision)
        print("Recall:", recall)
        print("True positive rate:", true_positive_rate)
        print("False negative rate:", false_negative_rate)
       '''
        
    
