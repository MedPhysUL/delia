# Medical data formatting and pre-processing module
This package is a medical data formatting and pre-processing module whose main objective is to build an HDF5 dataset containing all medical images of patients (DICOM format) and their associated segmentations. The HDF5 dataset is then easier to use to perform tasks on the medical data, such as machine learning tasks.

Anyone who is willing to contribute is welcome to do so.

## What is the purpose of this module?

**Digital Imaging and Communications in Medicine** ([**DICOM**](https://www.dicomstandard.org/)) is *the* international standard for medical images and related information. It defines the formats for medical images that can be exchanged with the data and quality necessary for clinical use. With the rapid development of artificial intelligence in the last few years, especially deep learning, medical images are increasingly used for understanding or prediction purposes. The working group [DICOM WG-23](https://www.dicomstandard.org/activity/wgs/wg-23/) on Artificial Intelligence / Application Hosting is currently working to identify or develop the DICOM mechanisms to support AI workflows, concentrating on the clinical context. Moreover, their future *roadmap and objectives* includes working on the concern that current DICOM mechanisms might not be adequate to cover some use cases, particularly bulk analysis of large repository data, e.g. for training deep learning neural networks. 

The **purpose** of this module is therefore to provide the necessary tools to facilitate the use of medical images in an AI workflow.  This goal is accomplished by using the [HDF file format](https://www.hdfgroup.org/) to create a dataset containing all medical images of patients (DICOM format) and their associated segmentations. Currently, the accepted file formats for segmentations are `.nrrd` and `.seg.nrrd` ([3D slicer segmentation format](https://slicer.readthedocs.io/en/latest/user_guide/image_segmentation.html)).

## Installation

### Latest stable version :

```
pip install dicom2hdf
```

### Latest (possibly unstable) version :

```
pip install git+https://github.com/MaxenceLarose/dicom2hdf
```

## Getting started

### Organize your data

As this module requires the use of data, it is important to properly configure the data-related elements before using it. The following sections present how to configure these elements.

#### Segmentation files names

There are **2 rules** to follow when naming segmentation files.

1. Probably the least flexible aspect of the package is that the file names of the segmentations need to contain the **series instance UID** of the series the segmentation is referring to. This attribute was chosen since the series instance UID is the unique identifier of a series and it's a mandatory attribute in the DICOM format. An example of a series instance UID is `1.5.296.1.7230010.7.1.3.8323328.763.1231455091.301876`.

2. Another strong assumption is that the DICOM data have been previously anonymized. We therefore assume that each patient's name contains a **unique number**.  Segmentation file names must contain this number in order to be able to associate a segmentation with the corresponding patient. To make it easier to find this number in the name of the segmentation file, a word common to all segmentations should be defined and placed in front of the patient number in the name of the segmentation file.  An example of a **patient number prefix** is just the word `Patient`.

Now that the 2 rules are established, we can present examples of file names :

```
Filename 1 : Patient1_1.5.296.1.7230010.7.1.3.8323328.763.1231455091.301876.seg.nrrd
Filename 2 : Patient1_2.8.246.1.7230010.7.1.3.8323328.763.1241455091.311976.seg.nrrd
Filename 3 : Patient2_1.5.296.1.7431010.7.1.3.8324328.763.1241415091.306876.seg.nrrd
Filename 4 : Patient3_2.3.216.1.7230410.7.1.3.8323318.763.1231355146.211176.seg.nrrd
```

#### Organs

The organs are specified as a **dictionary** that contains the organs and their associated segment names (those segment names are the ones we can find in the segmentation). Keys are arbitrary organ names and values are lists of possible segment names. Note that it can also be specified as a path to a **json file** that contains the organs dictionary. Both methods are presented below.

##### Using a json file

Create a json file containing only the dictionary of the organs (keys) and their associated segment names (values). Place this file in your data folder.

Here is an example of a json file configured as expected :

```json
{
    "Prostate": [
        "Segment_1",
        "Prostate"
    ],
    "Rectum": [
        "Segment_2",
        "Rectum"
    ],
    "Bladder": [
        "Segment_3",
        "Bladder"
    ]
}
```

##### Using a Python dictionary

Create the organs dictionary in your main.py python file.

Here is an example of a python dictionary instanced as expected :

```python
organs = {
    "Prostate": [
        "Segment_1",
        "Prostate"
    ],
    "Rectum": [
        "Segment_2",
        "Rectum"
    ],
    "Bladder": [
        "Segment_3",
        "Bladder"
    ]
}
```

#### Series descriptions

The series descriptions are specified as a **dictionary** that contains the series descriptions of the images that absolutely needs to be extracted from the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of series descriptions. The images associated with these series descriptions do not need to have a corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that must be added to the dataset is to be able to add images without their segmentation. Note that it can also be specified as a path to a **json file** that contains the series descriptions. Both methods are presented below.

<span style="color:red">Warning : *This dictionary (or json file) can be modified during the execution of the package functions. THIS IS NORMAL, we potentially want to add series descriptions if none of the descriptions match the series in the patient file.* </span> 

##### Using a json file

Create a json file containing only the dictionary of the names given to the images we want to add (keys) and lists of series descriptions (values). Place this file in your data folder.

Here is an example of a json file configured as expected :

```json
{
    "TEP": [
        "TEP WB CORR (AC)",
        "TEP WB XL CORR (AC)",
        "None"
    ],
    "CT": [
        "CT 2.5 WB",
        "AC CT 2.5 WB"
    ]
}
```

##### Using a Python dictionary

Create the organs dictionary in your main.py python file.

Here is an example of a python dictionary instanced as expected :

```python
series_descriptions = {
    "TEP": [
        "TEP WB CORR (AC)",
        "TEP WB XL CORR (AC)"
    ],
    "CT": [
        "CT 2.5 WB",
        "AC CT 2.5 WB"
    ]
}
```

#### File names

It is good practice to create a class that lists the various names and important paths of the folders that contain the data, because, let's face it, everything is a bit arbitrary anyway. I propose here a way to organize this class. This allows the user to have an overview of the parameters to be defined and it will also simplify the explanations in the next section on the structure of the data file. 

To do this, it is first necessary to create a file named `root.py` which will contain the important `FolderName` and `PathName` class.  The `root.py` file must be placed in the same folder as the `data` folder (*this will become clearer in the next section*).  It is easier to understand this step with an example so here is the expected content of `root.py `. *The names of the folders and files can differ.*

```python
import os

ROOT = os.path.abspath(os.path.dirname(__file__))


class FileName:
    ORGANS_JSON = "organs.json"
    SERIES_DESCRIPTIONS_JSON = "series_descriptions.json"
    PATIENT_DATASET = "patient_dataset.h5"


class FolderName:
    DATA_FOLDER = "data"
    PATIENTS_FOLDER = "Patients"
    SEGMENTATIONS_FOLDER = "Segmentations"
    IMAGES_FOLDER = "IMAGES"


class PathName:
    PATH_TO_DATA_FOLDER = os.path.join(ROOT, FolderName.DATA_FOLDER)
    
    PATH_TO_ORGANS_JSON = os.path.join(PATH_TO_DATA_FOLDER, FileName.ORGANS_JSON)
    PATH_TO_SERIES_DESCRIPTIONS_JSON = os.path.join(PATH_TO_DATA_FOLDER, FileName.SERIES_DESCRIPTIONS_JSON)
    PATH_TO_PATIENT_DATASET = os.path.join(PATH_TO_DATA_FOLDER, FileName.PATIENT_DATASET)
    
    PATH_TO_PATIENTS_FOLDER = os.path.join(PATH_TO_DATA_FOLDER, FolderName.PATIENTS_FOLDER)
    PATH_TO_SEGMENTATIONS_FOLDER = os.path.join(PATH_TO_DATA_FOLDER, FolderName.SEGMENTATIONS_FOLDER)

```

#### Structure your data directory

It is important to configure the directory structure correctly to ensure that the module interacts correctly with the data files. The repository, particularly the data folder, must be structured as follows. *Again, the names of the folders and files can and probably will differ, but they must be consistent with the names written in the* `root.py` *file*.

```
|_📂 Project directory/
  |_📄 root.py
  |_📄 main.py
  |_📂 data/
    |_📄 organs.json
    |_📄 series_descriptions.json
    |_📂 Patients/
      |_📂 patient1/
       	|_📂 IMAGES/
       	  |_📄 IM0.DCM
       	  |_📄 IM1.DCM
       	  |_📄 ...
      |_📂 patient2/
        |_📂 IMAGES/
       	  |_📄 IM0.DCM
       	  |_📄 IM1.DCM
       	  |_📄 ...
      |_📂 ...
    |_📂 Segmentations/
      |_📄 Patient1_CTSeriesUids.seg.nrrd
      |_📄 Patient1_TEPSeriesUids.seg.nrrd
      |_📄 Patient2_CTSeriesUids.nrrd
      |_📄 Patient2_TEPSeriesUids.nrrd
      |_📄 ...
```

### Import the package

The easiest way to import the package is to use :

```python
from dicom2hdf import *
```

This will import the useful classes `PathGenerator`, `PatientDataset`, `PatientDataGenerator` and the useful function `logs_file_setup`. These two classes represent two different ways of using the package. The following examples will present both procedures.

### Use the package

The two examples below show code to add to the `main.py` file. 

#### Example using the patient dataset class

This file can then be executed to obtain an hdf5 dataset.

```python
import logging

from dicom2hdf import *

from .root import *

logs_file_setup(level=logging.INFO)

path_generator = PathGenerator(
    path_to_patients_folder=PathName.PATH_TO_PATIENTS_FOLDER,
    path_to_segmentations_folder=PathName.PATH_TO_SEGMENTATIONS_FOLDER,
    images_folder_name=FolderName.IMAGES_FOLDER_NAME,
    verbose=True,
    patient_number_prefix="Patient"
)

dataset = PatientDataset(
    path_to_dataset=PathName.PATH_TO_PATIENT_DATASET,
)

dataset.create_hdf5_dataset(
    path_generator=path_generator,
    series_descriptions=PathName.PATH_TO_SERIES_DESCRIPTIONS_JSON,
    organs=PathName.PATH_TO_ORGANS_JSON,
    verbose=True,
    overwrite_dataset=True
)

```

#### Example using the patient data generator class

This file can then be executed to perform on-the-fly tasks on images.

```python
import logging

from dicom2hdf import *

from .root import *

logs_file_setup(level=logging.INFO)

path_generator = PathGenerator(
    path_to_patients_folder=PathName.PATH_TO_PATIENTS_FOLDER,
    path_to_segmentations_folder=PathName.PATH_TO_SEGMENTATIONS_FOLDER,
    images_folder_name=FolderName.IMAGES_FOLDER_NAME,
    verbose=True,
    patient_number_prefix="Patient"
)

patient_data_generator = PatientDataGenerator(
    path_generator=path_generator,
    verbose=verbose,
    organs=PathName.PATH_TO_ORGANS_JSON
    series_descriptions=PathName.PATH_TO_SERIES_DESCRIPTIONS_JSON,
)

for patient_dataset in patient_data_generator:
    patient_name = patient_dataset.patient_name
    
    for patient_image_data in enumerate(patient_dataset.data):
        dicom_header = patient_image_data.image.dicom_header
        simple_itk_image = patient_image_data.image.simple_itk_image
        numpy_array_image = sitk.GetArrayFromImage(simple_itk_image)
        
        """Perform any tasks on images on-the-fly like printing the image array shape."""
        print(numpy_array_image.shape)
```

## License

This code is provided under the [Apache License 2.0](https://github.com/MaxenceLarose/dicom2hdf/blob/main/LICENSE).

## Citation

```
@article{dicom2hdf,
  title={DICOM to HDF python module},
  author={Maxence Larose},
  year={2022},
  publisher={Université Laval},
  url={https://github.com/MaxenceLarose/dicom2hdf},
}
```

## Contact

Maxence Larose, B. Ing., [maxence.larose.1@ulaval.ca](mailto:maxence.larose.1@ulaval.ca)
