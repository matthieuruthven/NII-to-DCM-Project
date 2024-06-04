# NII_to_DCM_Python.py
# Code to convert ground-truth (GT) segmentations from 
# a NIfTI (.nii) file to DICOM (.dcm) files

# Author: Matthieu Ruthven (matthieuruthven@nhs.net)
# Last modified: 4th June 2024

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

def main(seg_path, nii_dir_path, dcm_dir_path):

    # Create list of files in folder containing .dcm files
    dcm_list = list_files_in_dir(dcm_dir_path)

    # Check there are 272 "dcm" files in "dcm_dir_path"
    assert len(dcm_list) == 272, f'There should be 272 "dcm" files in {dcm_dir_path}.'

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

    # Plot GT segmentation slice (i.e. 2D image)
    plt.imshow(gt_segs[idx, ...])
    plt.axis('off')

    # Load NIfTI image file
    nii_img = nib.load(nii_dir_path / f'{str(dcm_dir_path).split('/')[-1]}_img.nii.gz')
    nii_img = nii_img.get_fdata()

    # Check shape of image array
    assert nii_img.shape == (272, 512, 512), 'The shape of the array of the image should be (272, 512, 512).'

    # Plot image slice
    plt.imshow(nii_img[idx, ...])
    plt.axis('off')

    # Load corresponding "dcm" file
    dcm_file = pydicom.dcmread(dcm_dir_path / dcm_list[idx])

    # Check shape of image array
    assert dcm_file.pixel_array.shape == (512, 512), 'The shape of the array of the image should be (512, 512).'

    # Plot image
    plt.imshow(dcm_file.pixel_array)
    plt.axis('off')

    # Change orientation of GT segmentations
    nii_slice = np.fliplr(np.rot90(nii_img[idx, ...]))

    # Plot GT segmentation slice
    plt.imshow(nii_slice)
    plt.axis('off')

    # Check images are consistent
    if len(np.unique(nii_slice - dcm_file.pixel_array.astype('float64'))) == 1:

        # For each "dcm" file
        for idx, dcm_file in enumerate(dcm_list):

            # Load "dcm" file
            dcm_file = pydicom.dcmread(dcm_dir_path / dcm_file)

            # Extract corresponding slice from NIfTI image array
            nii_img = np.fliplr(np.rot90(nii_img[idx, ...])).astype('int16')

            # Check images are consistent
            assert len(np.unique(nii_slice - dcm_file.pixel_array.astype('float64'))) == 1, f'Slice {idx + 1}: There are inconsistencies between the DICOM and NIfTI images.'

            # Extract corresponding GT segmentations
            gt_segs = np.fliplr(np.rot90(gt_segs[idx, ...])).astype('int16')

            # Change pixel_array field
            dcm_file.pixel_array = gt_segs

            # Change PixelData field
            dcm_file.PixelData = dcm_file.pixel_array.tobytes()

            # Save modified "dcm" file
            # dcm_file.save_as(new_dcm_dir_path / dcm_file)

    else:

        # Update idx
        idx *= -1
        idx -= 1

        # Change orientation of GT segmentations
        nii_slice = np.fliplr(np.rot90(nii_img[idx, ...]))

        # Plot 2D image of GT segmentations
        plt.imshow(nii_slice)
        plt.axis('off')

        # Check images are consistent 
        len(np.unique(nii_slice - dcm_file.pixel_array.astype('float64'))) == 1, 'There is an inconsistency in the images.'

        # For each "dcm" file
        for idx, dcm_file in enumerate(dcm_list.reverse()):

            # Load "dcm" file
            dcm_file = pydicom.dcmread(dcm_dir_path / dcm_file)

            # Extract corresponding GT segmentations
            gt_segs = np.fliplr(np.rot90(gt_segs[idx, ...])).astype('int16')

            # Change pixel_array field
            dcm_file.pixel_array = gt_segs

            # Change PixelData field
            dcm_file.PixelData = dcm_file.pixel_array.tobytes()

            # Save modified "dcm" file
            # dcm_file.save_as(new_dcm_dir_path / dcm_file)

    # Print update
    print('Finished converting ground-truth segmentations from a NIfTI file to DICOM files.')

if __name__ == "__main__":

    # Create parser
    parser = argparse.ArgumentParser(description='Code to convert ground-truth segmentations from NIfTI files to DICOM files.')

    # Add arguments
    parser.add_argument(
        '--nii_seg_path', 
        help='Path to NIfTI file of ground-truth segmentations.',
        default='/Users/andreia/Desktop/matthieu/2021_speech_data/vol_1/segmentations/3d_slicer_combined/Segmentation.nii.gz',
        type=Path
        )
    parser.add_argument(
        '--nii_img_dir_path', 
        help='Path to folder containing NIfTI file of images.',
        default='/Users/andreia/Desktop/matthieu/2021_speech_data/vol_1/nifti',
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
    assert os.path.exists(args.nii_seg_path), 'Please specify the absolute path to the NIfTI ground-truth segmentation file using the --nii_seg_path argument to "NII_to_DCM_Python.py".'
    assert os.path.exists(args.nii_img_dir_path), 'Please specify the absolute path to the folder containing the NIfTI image file using the --nii_img_dir_path argument to "NII_to_DCM_Python.py".'
    assert os.path.exists(args.dcm_dir_path), 'Please specify the absolute path to the folder containing the DICOM image files (i.e. the files with the relevant headers) using the --dcm_dir_path argument to "NII_to_DCM_Python.py".'

    # Run main function
    main(args.nii_seg_path, args.nii_img_dir_path, args.dcm_dir_path)
