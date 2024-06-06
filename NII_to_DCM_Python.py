# NII_to_DCM_Python.py
# Code to convert ground-truth (GT) segmentations from 
# a NIfTI (.nii) file to DICOM (.dcm) files

# Author: Matthieu Ruthven (matthieuruthven@nhs.net)
# Last modified: 6th June 2024

# Import required packages
import argparse
from pathlib import Path
import os
import nibabel as nib
import numpy as np
import pydicom
import matplotlib.pyplot as plt

def list_files_in_dir(dir_path):
    
    # Create list of files in folder
    file_list = [g for g in os.listdir(dir_path) if (g.endswith('dcm') and g.startswith('IM-'))]
    file_list.sort()

    # Check list is not empty
    assert file_list, f'There are no ".dcm" files in "{dir_path}".'

    # Return list
    return file_list

def main(seg_path, nii_img_path, dcm_dir_path, save_dir_path):

    # Create list of DICOM files in "dcm_dir_path"
    dcm_list = list_files_in_dir(dcm_dir_path)

    # Check there are 272 DICOM files in "dcm_dir_path"
    assert len(dcm_list) == 272, f'There should be 272 DICOM files in {dcm_dir_path}.'

    # Specify index
    idx = 100

    # Load NIfTI GT segmentation file
    gt_segs = nib.load(seg_path)
    gt_segs = gt_segs.get_fdata()

    # Check shape of GT segmentation array
    assert gt_segs.shape == (272, 512, 512), 'The shape of the array of the ground-truth segmentations should be (272, 512, 512).'

    # Check there are three segmentation classes
    seg_val_list = np.unique(gt_segs)
    assert len(seg_val_list) == 3, 'There are not three segmentation classes in the ground-truth segmentations.'
    assert min(seg_val_list) == 0, 'One segmentation class should have a value of 0.'
    assert max(seg_val_list) == 2, 'One segmentation class should have a value of 2.'

    # Plot slice (i.e. 2D image) of GT segmentations
    # plt.imshow(gt_segs[idx, ...])
    # plt.axis('off')

    # Load NIfTI image file
    nii_img = nib.load(nii_img_path)
    nii_img = nii_img.get_fdata()

    # Check shape of image array
    assert nii_img.shape == (272, 512, 512), 'The shape of the array of the image should be (272, 512, 512).'

    # Plot image slice
    # plt.imshow(nii_img[idx, ...])
    # plt.axis('off')

    # Load DICOM file containing image
    dcm_file = pydicom.dcmread(dcm_dir_path / dcm_list[idx])

    # Check shape of image array
    assert dcm_file.pixel_array.shape == (512, 512), 'The shape of the array of the image should be (512, 512).'

    # Plot DICOM image
    # plt.imshow(dcm_file.pixel_array)
    # plt.axis('off')

    # Change orientation of NIfTI image slice
    nii_slice = np.fliplr(np.rot90(nii_img[idx, ...]))

    # Plot NIfTI image slice
    # plt.imshow(nii_slice)
    # plt.axis('off')

    # Check images are consistent
    if len(np.unique(nii_slice - dcm_file.pixel_array.astype('float64'))) != 1:

        # Update idx
        idx *= -1
        idx -= 1

        # Change orientation of NIfTI image slice
        nii_slice = np.fliplr(np.rot90(nii_img[idx, ...]))

        # Plot NIfTI image slice
        # plt.imshow(nii_slice)
        # plt.axis('off')

        # Check images are consistent 
        assert len(np.unique(nii_slice - dcm_file.pixel_array.astype('float64'))) == 1, 'There is an inconsistency in the images.'

        # Reverse list of DICOM image files
        dcm_list.reverse()

    # For each DICOM file
    for idx, dcm_name in enumerate(dcm_list):

        # Load DICOM file
        dcm_file = pydicom.dcmread(dcm_dir_path / dcm_name)

        # Extract corresponding slice from NIfTI image array
        nii_slice = np.fliplr(np.rot90(nii_img[idx, ...])).astype('int16')

        # Check images are consistent
        assert len(np.unique(nii_slice - dcm_file.pixel_array.astype('float64'))) == 1, f'Slice {idx + 1}: There are inconsistencies between the DICOM and NIfTI images.'

        # Extract corresponding GT segmentations
        gt_seg_slice = np.fliplr(np.rot90(gt_segs[idx, ...])).astype('int16')

        # Change PixelData field
        dcm_file.PixelData = gt_seg_slice.tobytes()

        # Save modified DICOM file
        dcm_file.save_as(save_dir_path / dcm_name)

    # Print update
    print('Finished converting ground-truth segmentations from a NIfTI file to DICOM files.')

if __name__ == "__main__":

    # Create parser
    parser = argparse.ArgumentParser(description='Code to convert ground-truth segmentations from NIfTI files to DICOM files.')

    # Add arguments
    parser.add_argument(
        '--nii_seg_path', 
        help='Path to NIfTI file of ground-truth segmentations.',
        type=Path,
        required=True
        )
    parser.add_argument(
        '--nii_img_path', 
        help='Path to NIfTI file of image.',
        type=Path,
        required=True
        )
    parser.add_argument(
        '--dcm_dir_path',
        help='Path to folder containing DICOM files of image (i.e. files with relevant headers).',
        type=Path,
        required=True
        )
    parser.add_argument(
        '--save_dir_path',
        help='Path to folder where DICOM files of ground-truth segmentations will be saved.',
        type=Path,
        required=True
        )

    # Parse arguments
    args = parser.parse_args()

    # Check if folders exist
    assert os.path.exists(args.nii_seg_path), 'Please specify the absolute path to the NIfTI ground-truth segmentation file using the --nii_seg_path argument to "NII_to_DCM_Python.py".'
    assert os.path.exists(args.nii_img_path), 'Please specify the absolute path to the NIfTI image file using the --nii_img_path argument to "NII_to_DCM_Python.py".'
    assert os.path.exists(args.dcm_dir_path), 'Please specify the absolute path to the folder containing the DICOM image files (i.e. the files with the relevant headers) using the --dcm_dir_path argument to "NII_to_DCM_Python.py".'
    assert os.path.exists(args.save_dir_path), 'Please ensure the folder into which the DICOM ground-truth segmentation files will be saved (i.e the folder with the name and absolute path specified by the --save_dir_path argument to "NII_to_DCM_Python.py") exists.'

    # Run main function
    main(args.nii_seg_path, args.nii_img_path, args.dcm_dir_path, args.save_dir_path)
