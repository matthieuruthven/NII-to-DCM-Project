# NII-to-DCM-Project

Code to convert ground-truth (GT) segmentations from a NIfTI file to DICOM files.

## Introduction

### Requirements

Software: [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### Setting up

1. Download this repository.

2. Open a new terminal and navigate to the folder containing the files from this repository.

3. Enter the following command to create a conda environment and install the Python packages required to run the code:
```
conda env create -f environment.yml
```

4. Enter the following command to activate the conda environment
```
conda activate nii_to_dcm
```

## NIfTI to DICOM Conversion

Enter the following command to convert a NIfTI file of GT segmentations to DICOM files:
```
python NII_to_DCM_Python.py --nii_seg_path path/to/file --nii_img_path path/to/file --dcm_dir_path path/to/folder --save_dir_path path/to/folder
```
Where:
 - *path/to/file* following the **--nii_seg_path** argument is the path to the NIfTI file of the GT segmentations.
 - *path/to/file* following the **--nii_img_path** argument is the path to the NIfTI file of the image (in this case, a three-dimensional magnetic resonance image).
 - *path/to/folder* following the **--dcm_dir_path** argument is the path to the folder containing the DICOM files of the image.
 - *path/to/folder* following the **--save_dir_path** argument is the path to the folder into which the DICOM files of the GT segmentations will be saved.