<p align="center" width="100%">
    <img width="100%" src="https://github.com/MaxenceLarose/delia/raw/main/images/logo/delia_banner.svg">
</p>
<p align="center"><i>DELIA facilitates data extraction from DICOM files to support large-scale image analysis workflows.</i></p>

# Notable features

- Bulk extraction of images and segmentations from multiple patients' DICOM files. Segmentations must be in [DICOM-SEG](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.20.html) or [RTStruct](https://dicom.nema.org/dicom/2013/output/chtml/part03/sect_A.19.html) format.
- Creation of an [HDF5](https://github.com/h5py/h5py) database containing multiple patients' medical images as well as binary label maps (segmentations). The database is then easier to use than DICOMs to perform tasks on medical data, such as training deep neural networks. 
- Bulk extraction of radiomics features from multiple patients' DICOM files using [pyradiomics](https://github.com/AIM-Harvard/pyradiomics).

# Installation

## Latest stable version :

```
pip install delia
```

## Latest (possibly unstable) version :

```
pip install git+https://github.com/MaxenceLarose/delia
```

# Quick usage preview

## Extract images as `numpy` arrays

```python
from delia.extractors import PatientsDataExtractor

patients_data_extractor = PatientsDataExtractor(path_to_patients_folder="patients")

for patient in patients_data_extractor:
    for image_data in patient.data:
        array = image_data.image.numpy_array
        
        """Perform any tasks on images on-the-fly."""
        print(array)
```

## Create patients database (HDF5)

```python
from delia.databases import PatientsDatabase
from delia.extractors import PatientsDataExtractor

patients_data_extractor = PatientsDataExtractor(path_to_patients_folder="patients")

database = PatientsDatabase(path_to_database="patients_database.h5")

database.create(patients_data_extractor=patients_data_extractor)

```

## Create radiomics dataset (CSV)

```python
from delia.extractors import PatientsDataExtractor
from delia.radiomics import RadiomicsDataset, RadiomicsFeatureExtractor

patients_data_extractor = PatientsDataExtractor(path_to_patients_folder="patients")

radiomics_dataset = RadiomicsDataset(path_to_dataset="radiomics.csv")
radiomics_dataset.extractor = RadiomicsFeatureExtractor(path_to_params="features_extractor_params.yaml")

radiomics_dataset.create(patients_data_extractor=patients_data_extractor, organ="Heart", image_modality="CT")

```

# Motivation

**Digital Imaging and Communications in Medicine** ([**DICOM**](https://www.dicomstandard.org/)) is *the* international standard for medical images and related information. The working group [DICOM WG-23](https://www.dicomstandard.org/activity/wgs/wg-23/) on Artificial Intelligence / Application Hosting is currently working to identify or develop the DICOM mechanisms to support AI workflows, concentrating on the clinical context. Moreover, their future *roadmap and objectives* includes working on the concern that current DICOM mechanisms might not be adequate to cover some use cases, particularly bulk analysis of large repository data, e.g. for training deep learning neural networks. **However, no tool has been developed to achieve this goal at present.**

The main **purpose** of this module is therefore to provide the necessary tools to facilitate the use of medical images in an AI workflow.  This goal is accomplished by using the [HDF file format](https://www.hdfgroup.org/) to create a database containing patients' medical images as well as binary label maps obtained from the segmentation of these images.

# How it works

## Main concepts

There are 4 main concepts :

1. `PatientDataModel` : It is the primary `delia` data structure. It is a named tuple gathering the image and segmentation data available in a patient record. 
2. `PatientsDataExtractor` : A Python [Generator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Generator) that allows to iterate over several patients and create a `PatientDataModel` object for each of them. A sequence of `delia` and/or `monai` transformations to apply to specific images or segmentations can be specified (see [MONAI](https://docs.monai.io/en/stable/transforms.html)).
3. `PatientsDatabase` : An object that is used to create/interact with an HDF5 file (a database!) containing all patients information (images + label maps). The `PatientsDataExtractor` is used to populate this database. 
4. `RadiomicsDataset` : An object that is used to create/interact with a csv file (a dataset!) containing radiomics features extracted from images. The `PatientsDataExtractor` is used to populate this dataset. 

## Organize your data

Since this module requires the use of data, it is important to properly configure the data-related elements before using it.

### File format

Images files must be in standard [**DICOM**](https://www.dicomstandard.org/) format and segmentation files must be in [DICOM-SEG](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.20.html) or [RTStruct](https://dicom.nema.org/dicom/2013/output/chtml/part03/sect_A.19.html) format.

If your segmentation files are in a research file format (`.nrrd`, `.nii`, etc.), you need to convert them into the standardized [DICOM-SEG](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.20.html) or [RTStruct](https://dicom.nema.org/dicom/2013/output/chtml/part03/sect_A.19.html) format. You can use the [pydicom-seg](https://pypi.org/project/pydicom-seg/) library to create the DICOM-SEG files OR use the [itkimage2dicomSEG](https://github.com/MaxenceLarose/itkimage2dicomSEG) python module, which provide a complete pipeline to perform this conversion. Also, you can use the [RT-Utils](https://github.com/qurit/rt-utils) library to create the RTStruct files.

### Series descriptions (Optional)

*This dictionary is **not** mandatory for the code to work and therefore its default value is `None`. Note that if no `series_descriptions` dictionary is given, i.e. `series_descriptions = None`, then all images will be added to the database.*

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

## Structure your patients directory

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

# Import the package

The easiest way to import the package is to use :

```python
import delia
```

You can explicitly use the objects sub-modules :

```python
from delia.databases import PatientsDatabase
from delia.extractors import PatientsDataExtractor
from delia.radiomics import RadiomicsDataset, RadiomicsFeatureExtractor
```

# Use the package

## Example using the `PatientsDatabase` class

This file can then be executed to obtain an hdf5 database.

```python
from delia.databases import PatientsDatabase
from delia.extractors import PatientsDataExtractor
from delia.transforms import (
    PETtoSUVD,
    ResampleD
)
from monai.transforms import (
    CenterSpatialCropD,
    Compose,
    ScaleIntensityD,
    ThresholdIntensityD
)

patients_data_extractor = PatientsDataExtractor(
    path_to_patients_folder="data/patients",
    series_descriptions="data/series_descriptions.json",
    transforms=Compose(
        [
            ResampleD(keys=["CT_THORAX", "TEP", "Heart"], out_spacing=(1.5, 1.5, 1.5)),
            CenterSpatialCropD(keys=["CT_THORAX", "TEP", "Heart"], roi_size=(1000, 160, 160)),
            ThresholdIntensityD(keys=["CT_THORAX"], threshold=-250, above=True, cval=-250),
            ThresholdIntensityD(keys=["CT_THORAX"], threshold=500, above=False, cval=500),
            ScaleIntensityD(keys=["CT_THORAX"], minv=0, maxv=1),
            PETtoSUVD(keys=["TEP"])
        ]
    )
)

database = PatientsDatabase(path_to_database="data/patients_database.h5")

database.create(
    patients_data_extractor=patients_data_extractor,
    tags_to_use_as_attributes=[(0x0008, 0x103E), (0x0020, 0x000E), (0x0008, 0x0060)],
    overwrite_database=True
)

```

The created HDF5 database will then look something like :

![patient_dataset](https://github.com/MaxenceLarose/delia/raw/main/images/patient_dataset.png)

## Example using the `PatientsDataExtractor`class

This file can then be executed to perform on-the-fly tasks on images.

```python
from delia.extractors import PatientsDataExtractor
from delia.transforms import Compose, CopySegmentationsD, PETtoSUVD, ResampleD
import SimpleITK as sitk

patients_data_extractor = PatientsDataExtractor(
    path_to_patients_folder="data/patients",
    series_descriptions="data/series_descriptions.json",
    transforms=Compose(
        [
            ResampleD(keys=["CT_THORAX", "Heart"], out_spacing=(1.5, 1.5, 1.5)),
            PETtoSUVD(keys=["TEP"]),
            CopySegmentationsD(segmented_image_key="CT_THORAX", unsegmented_image_key="TEP")
        ]
    )
)

for patient_dataset in patients_data_extractor:
	print(f"Patient ID: {patient_data.patient_id}")

    for patient_image_data in patient_dataset.data:
        dicom_header = patient_image_data.image.dicom_header
        simple_itk_image = patient_image_data.image.simple_itk_image
        numpy_array_image = sitk.GetArrayFromImage(simple_itk_image)

        """Perform any tasks on images on-the-fly."""
        print(numpy_array_image.shape)
```

## Need more examples?

You can find more in the [examples folder](https://github.com/MaxenceLarose/delia/tree/main/examples).

# A deeper look into the `PatientsDataExtractor` object

The `PatientsDataExtractor` has 3 important variables:  a `path_to_patients_folder` (which dictates the path to the folder that contains all patient records), a `series_descriptions` (which dictates the images that needs to be extracted from the patient records) and `transforms` that defines a sequence of transformations to apply on images or segmentations. For each patient/folder available in the `path_to_patients_folder`, all DICOM files in their folder are read. If the series descriptions of a certain volume match one of the descriptions present in the given `series_descriptions` dictionary, this volume and its segmentation (if available) are automatically added to the `PatientDataModel`. Note that if no `series_descriptions` dictionary is given (`series_descriptions = None`), then all images (and associated segmentations) will be added to the database. 

The `PatientsDataExtractor` can therefore be used to iteratively perform tasks on each of the patients, such as displaying certain images, transforming images into numpy arrays, or creating an HDF5 database using the `PatientsDatabase`. It is this last task that is highlighted in this package, but it must be understood that the data extraction is performed in a very general manner by the `PatientsDataExtractor` and is therefore not limited to this single application. For example, someone could easily develop a `Numpydatabase` whose creation would be ensured by the `PatientsDataExtractor`, similar to the current `PatientsDatabase` based on the HDF5 format.

# TODO

- [ ] Generalize the use of arbitrary tags to choose images to extract. At the moment, the only tag available is `series_descriptions`.

# License

This code is provided under the [Apache License 2.0](https://github.com/MaxenceLarose/delia/blob/main/LICENSE).

# Citation

```
@misc{delia,
  title={DELIA: DICOM Extraction for Large-scale Image Analysis},
  author={Maxence Larose},
  year={2022},
  publisher={Université Laval},
  url={https://github.com/MaxenceLarose/delia},
}
```

# Contact

Maxence Larose, B. Ing., [maxence.larose.1@ulaval.ca](mailto:maxence.larose.1@ulaval.ca)
