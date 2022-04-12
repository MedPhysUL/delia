# Medical data formatting and pre-processing module
This package provides a set of utilities for extracting data contained in DICOM files into an HDF5 dataset containing patients' medical images as well as binary label maps obtained from the segmentation of these images (if available). The HDF5 dataset is then easier to use to perform tasks on the medical data, such as machine learning tasks. It is a higher-level library that builds on the excellent lower-level [pydicom](https://pydicom.github.io/pydicom/stable/) library.

Anyone who is willing to contribute is welcome to do so.

## Motivation

**Digital Imaging and Communications in Medicine** ([**DICOM**](https://www.dicomstandard.org/)) is *the* international standard for medical images and related information. It defines the formats for medical images that can be exchanged with the data and quality necessary for clinical use. The working group [DICOM WG-23](https://www.dicomstandard.org/activity/wgs/wg-23/) on Artificial Intelligence / Application Hosting is currently working to identify or develop the DICOM mechanisms to support AI workflows, concentrating on the clinical context. Moreover, their future *roadmap and objectives* includes working on the concern that current DICOM mechanisms might not be adequate to cover some use cases, particularly bulk analysis of large repository data, e.g. for training deep learning neural networks. **However, no tool has been developed to achieve this goal at present.**

The **purpose** of this module is therefore to provide the necessary tools to facilitate the use of medical images in an AI workflow.  This goal is accomplished by using the [HDF file format](https://www.hdfgroup.org/) to create a dataset containing patients' medical images as well as binary label maps obtained from the segmentation of these images (if available).

## Installation

### Latest stable version :

```
pip install dicom2hdf
```

### Latest (possibly unstable) version :

```
pip install git+https://github.com/MaxenceLarose/dicom2hdf
```

## Brief explanation of how it works 

First, it is necessary to explain briefly how the package builds a dataset using the provided data.

The primary `dicom2hdf` data structure is the `PatientDataModel` object, i.e. a named tuple gathering the image and  segmentation data available in a patient record. The `PatientDataGenerator` class allows to iterate over several patient folders and create a `PatientDataModel` object for each of them, which allows to extract large amounts of data quickly. For each patient, all DICOM files in their folder are read. If the series descriptions of a certain volume match one of the descriptions present in the given `series_descriptions` dictionary, this volume and its segmentation (if available) are automatically added to the `PatientDataModel`. Note that if no `series_descriptions` dictionary is given, i.e. `series_descriptions = None`, then all images (and associated segmentations) will be added to the dataset. 

The `PatientDataGenerator` can therefore be used to iteratively perform tasks on each of the patients, such as displaying certain images, transforming images into numpy arrays, or populating an HDF5 dataset. It is this last task that is highlighted in this package, but it must be understood that the data extraction is performed in a very general manner by the `PatientDataGenerator` and is therefore not limited to this single application. For example, someone could easily develop a numpy dataset whose creation/ would be ensured by the `PatientDataGenerator`, similar to the HDF5 dataset.

### Organize your data

Since this module requires the use of data, it is important to properly configure the data-related elements before using it. The following sections show how to configure these.

#### File format

Images files must be in standard [**DICOM**](https://www.dicomstandard.org/) format and segmentation files must be in [DICOM-SEG](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.20.html) format.

If your segmentation files are in a research file format (`.nrrd`, `.nii`, etc.), you need to convert them into the standardized [DICOM-SEG](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.20.html) format. You can use the [pydicom-seg](https://pypi.org/project/pydicom-seg/) library to create the DICOM-SEG files OR use the [itkimage2dicomSEG](https://github.com/MaxenceLarose/itkimage2dicomSEG) python module, which provide a complete pipeline to perform this conversion.

#### Series descriptions (Optional)

*This dictionary is **not** mandatory for the code to work and therefore its default value is `None`. Note that if no `series_descriptions` dictionary is given, i.e. `series_descriptions = None`, then all images (and associated segmentations) will be added to the dataset.*

The series descriptions are specified as a **dictionary** that contains the series descriptions of the images that needs to be extracted from the patients' files. Keys are arbitrary names given to the images we want to add and values are lists of series descriptions. The images associated with these series descriptions do not need to have a corresponding segmentation volume. If none of the descriptions match the series in a patient's files, a warning is raised and the patient is added to the list of patients for whom the pipeline has failed.

Note that the series descriptions can be specified as a classic dictionary or as a path to a **json file** that contains the series descriptions. Both methods are presented below.

<details>
  <summary>Using a json file</summary>

Create a json file containing only the dictionary of the names given to the images we want to add (keys) and lists of series descriptions (values). Place this file in your data folder.

Here is an example of a json file configured as expected :

```json
{
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
</details>

<details>
  <summary>Using a Python dictionary</summary>

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
</details>

#### Structure your patients directory

It is important to configure the directory structure correctly to ensure that the module interacts correctly with the data files. The `patients` folder, must be structured as follows. *Note that all DICOM files in the patients' folder will be read.*

```
|_📂 Project directory/
  |_📄 main.py
  |_📂 data/
    |_📄 series_descriptions.json
    |_📂 patients/
      |_📂 patient1/
       	|_📄 ...
       	|_📂 ...
      |_📂 patient2/
       	|_📄 ...
       	|_📂 ...
      |_📂 ...
```

### Import the package

The easiest way to import the package is to use :

```python
from dicom2hdf import *
```

This will import the useful classes `PatientsDataset` and `PatientDataGenerator`. These two classes represent two different ways of using the package. The following examples will present both procedures.

### Use the package

#### Example using the patient dataset class

This file can then be executed to obtain an hdf5 dataset.

```python
from dicom2hdf import PatientsDataset

patients_dataset = PatientsDataset(
    path_to_dataset="data/patient_dataset.h5",
)

patients_dataset.create_hdf5_dataset(
    path_to_patients_folder="data/Patients",
    tags_to_use_as_attributes=[(0x0008, 0x103E), (0x0020, 0x000E), (0x0008, 0x0060)],
    series_descriptions="data/series_descriptions.json",
    overwrite_dataset=True
)

```

The created HDF5 dataset will then look something like :

![patient_dataset](https://github.com/MaxenceLarose/dicom2hdf/raw/main/images/patient_dataset.png)

#### Example using the patient data generator class

This file can then be executed to perform on-the-fly tasks on images.

```python
from dicom2hdf import PatientDataGenerator
import SimpleITK as sitk

patient_data_generator = PatientDataGenerator(
    path_to_patients_folder="data/Patients",
    series_descriptions="data/series_descriptions.json"
)

for patient_dataset in patient_data_generator:
    print(f"Patient ID: {patient_dataset.patient_id}")
    
    for patient_image_data in patient_dataset.data:
        dicom_header = patient_image_data.image.dicom_header
        simple_itk_image = patient_image_data.image.simple_itk_image
        numpy_array_image = sitk.GetArrayFromImage(simple_itk_image)
        
        """Perform any tasks on images on-the-fly."""
        print(numpy_array_image.shape)
```

#### Need more examples?

You can find more in the [examples folder](https://github.com/MaxenceLarose/dicom2hdf/tree/main/examples).

## TODO

- [ ] Generalize the use of a specific tag to add images that have not been segmented. At the moment, the only tag available is `series_descriptions`.

## License

This code is provided under the [Apache License 2.0](https://github.com/MaxenceLarose/dicom2hdf/blob/main/LICENSE).

## Citation

```
@article{dicom2hdf,
  title={dicom2hdf: DICOM to HDF python module},
  author={Maxence Larose},
  year={2022},
  publisher={Université Laval},
  url={https://github.com/MaxenceLarose/dicom2hdf},
}
```

## Contact

Maxence Larose, B. Ing., [maxence.larose.1@ulaval.ca](mailto:maxence.larose.1@ulaval.ca)
