# NII_to_DCM_Python.py
# Code to convert ground-truth segmentations from 
# NIfTI (.nii) files to DICOM (.dcm) files

# Author: Matthieu Ruthven (matthieuruthven@nhs.net)
# Last modified: 2nd June 2024

# Import required packages
import argparse
from pathlib import Path
import os
import nibabel as nib
from numpy import unique as np_unique
import pydicom
import matplotlib.pyplot as plt

def list_files_in_dir(dir_path, file_type):

    # Check that argument "file_type" is either "nii.gz" or "dcm"
    assert (file_type == 'nii.gz') or (file_type == 'dcm'), '"file_type" argument to "list_files_in_dir" function should either be "nii.gz" or "dcm".'
    
    # Create list of files in folder
    if file_type == 'nii.gz':
        file_list = [g for g in os.listdir(dir_path) if (g.endswith(file_type) and g.startswith('Segmentation'))]
    elif file_type == 'dcm':
        file_list = [g for g in os.listdir(dir_path) if (g.endswith(file_type) and g.startswith('IM-'))]
    file_list.sort()

    # Check list is not empty
    assert file_list, f'There are no "{file_type}" files in "{dir_path}".'

    # Return list
    return file_list

def main(nii_dir_path, dcm_dir_path):

    # Create list of files in folder containing .nii files
    nii_list = list_files_in_dir(nii_dir_path, 'nii.gz')

    # Create list of files in folder containing .dcm files
    dcm_list = list_files_in_dir(dcm_dir_path, 'dcm')

    # Check there is only one "nii.gz" file in "nii_dir_path"
    assert len(nii_list) == 1, f'There should only be one "nii.gz" file in {nii_dir_path}.'

    # Check there are 272 "dcm" files in "dcm_dir_path"
    assert len(dcm_list) == 272, f'There should be 272 "dcm" files in {dcm_dir_path}.'

    # Load "nii.gz" file
    nii_file = nib.load(nii_dir_path / nii_list[0])

    # Check shape of ground-truth segmentation array
    assert nii_file.shape == (272, 512, 512), 'The shape of the array of the ground-truth segmentations should be (272, 512, 512).'

    # Check there are three segmentation classes
    seg_val_list = np_unique(nii_file.get_fdata())
    assert len(seg_val_list) == 3, 'There are not three segmentation classes in the ground-truth segmentations.'
    assert min(seg_val_list) == 0, 'One segmentation class should have a value of 0.'
    assert max(seg_val_list) == 2, 'One segmentation class should have a value of 2.'

    # Plot a 2D image of the ground-truth segmentations
    plt.imshow(nii_file.get_fdata()[136, ...])
    plt.axis('off')

    # Load "dcm" file
    dcm_file = pydicom.dcmread(dcm_dir_path / dcm_list[136])

    # Check shape of image array
    assert dcm_file.pixel_data.shape == (512, 512), 'The shape of the array of the image should be (512, 512).'

    # Plot the image
    plt.imshow(dcm_file.pixel_data)
    plt.axis('off')

    # Print update
    print('Finished converting ground-truth segmentations from a NIfTI file to a DICOM file.')

if __name__ == "__main__":

    # Create parser
    parser = argparse.ArgumentParser(description='Code to convert ground-truth segmentations from NIfTI files to DICOM files.')

    # Add arguments
    parser.add_argument(
        '--nii_dir_path', 
        help='Path to folder containing NIfTI file(s) of ground-truth segmentation(s).',
        default='/Users/andreia/Desktop/matthieu/2021_speech_data/vol_1/segmentations/3d_slicer_combined',
        type=Path
        )
    parser.add_argument(
        '--dcm_dir_path',
        help='Path to folder containing DICOM image file(s) (i.e. files with relevant headers).',
        default='/Users/andreia/Desktop/matthieu/2021_speech_data/vol_1/dicom/3D_Sag_T2_Cube_08mm_R2_12',
        type=Path
        )

    # Parse arguments
    args = parser.parse_args()

    # Check if folders exist
    assert os.path.exists(args.nii_dir_path), 'Please specify the absolute path to the folder containing the NIfTI file(s) of ground-truth segmentation(s) using the --nii_dir_path argument to "NII_to_DCM_Python.py".'
    assert os.path.exists(args.dcm_dir_path), 'Please specify the absolute path to the folder containing the DICOM image file(s) (i.e. the files with the relevant headers) using the --dcm_dir_path argument to "NII_to_DCM_Python.py".'

    # Run main function
    main(args.nii_dir_path, args.dcm_dir_path)
