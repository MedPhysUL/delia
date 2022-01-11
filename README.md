# Medical data formatting and pre-processing module
This package is a medical data formatting and pre-processing module whose main objective is to build an HDF5 dataset containing all medical images of patients (DICOM format) and their associated segmentations. The HDF5 dataset is then easier to use to perform tasks on the medical data, such as machine learning tasks.

Anyone who is willing to contribute is welcome to do so.

## What is the purpose of this module?

**Digital Imaging and Communications in Medicine** ([**DICOM**](https://www.dicomstandard.org/)) is *the* international standard for medical images and related information. It defines the formats for medical images that can be exchanged with the data and quality necessary for clinical use. With the rapid development of artificial intelligence in the last few years, especially deep learning, medical images are increasingly used for understanding or prediction purposes. The working group [DICOM WG-23](https://www.dicomstandard.org/activity/wgs/wg-23/) on Artificial Intelligence / Application Hosting is currently working to identify or develop the DICOM mechanisms to support AI workflows, concentrating on the clinical context. Moreover, their Future Roadmap and Objectives includes working on the concern that current DICOM mechanisms might not be adequate to cover some use cases, particularly bulk analysis of large repository data, e.g. for training deep learning neural networks. 

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

The easiest way to import the package is to use :

```python
from dicom2hdf import *
```

This will import the useful classes `PatientDataset` and `PatientDataGenerator`. These two classes represent two different ways of using the package. The following examples will present both procedures.

### Example using the patient dataset class

```python
from dicom2hdf import *

dataset = PatientDataset(
    path_to_dataset=PathName.PATH_TO_PATIENT_DATASET,
)

dataset.create_hdf5_dataset(
    path_to_patients_folder=PathName.PATH_TO_PATIENTS_FOLDER,
    path_to_segmentations_folder=PathName.PATH_TO_SEGMENTATIONS_FOLDER,
    series_descriptions=os.path.join(PathName.PATH_TO_DATA_FOLDER, "series_descriptions.json"),
    organs=os.path.join(PathName.PATH_TO_DATA_FOLDER, "organs.json"),
    images_folder_name=FolderName.IMAGES_FOLDER_NAME,
    verbose=True,
    overwrite_dataset=True
)
```

### Example using the patient data generator class

```python
from dicom2hdf import *

patient_data_generator = PatientDataGenerator(
    paths_to_patients_folder_and_segmentations=paths_to_patients_folder_and_segmentations,
    verbose=verbose,
    series_descriptions=series_descriptions,
    organs=organs
)

for patient_dataset in patient_data_generator:
    patient_name = patient_dataset.patient_name
    
    for patient_image_data in enumerate(patient_dataset.data):
        dicom_header = patient_image_data.image.dicom_header
        simple_itk_image = patient_image_data.image.simple_itk_image
        numpy_array_image = sitk.GetArrayFromImage(simple_itk_image)
        
        """Perform some tasks on images on-the-fly."""
```

## Project Tree

```
├── src/                             
│   ├── data_generators/
│   │   └── patient_data_generator.py                  
│   ├── data_readers/
│   │   ├── dicom/
│   │   │	└── dicom_reader.py 		
│   │   ├── patient_data/
│   │   │   ├──	factories/
│   │   │	│	├── base_patient_data_factory.py
│   │   │	│	└── patient_data_factories.py
│   │   │   ├── patient_data_query_context.py 
│   │   │   ├── patient_data_query_stategy.py      
│   │   │	└── patient_data_reader.py 						
│   │   ├── segmentation/
│   │   │   ├──	factories/
│   │   │	│	├── base_segmentation_factory.py
│   │   │	│	├── nrrd_segmentation_factories.py
│   │   │	│	├── segment.py
│   │   │	│	└── segmentation.py
│   │   │   ├──	segmentation_context.py
│   │   │   ├──	segmentation_reader.py
│   │   │	└── segmentation_strategy.py
│   ├── datasets/
│   │   ├── tools/
│   │   |	├──segmentation_filename_patterns_matcher.py
│   │   └── hdf5_dataset.py
│   ├── __main__.py
│   ├── data_model.py
│   ├── logging_tools.py
│   ├── root.py
│   └── utils.py
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
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
