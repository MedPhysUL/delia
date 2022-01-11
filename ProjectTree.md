# Project Tree

```
├── dicom2hdf/                             
│   ├── data_generators/
│   │   └── patient_data_generator.py                  
│   ├── data_readers/
│   │   ├── dicom/
│   │   │	└── dicom_reader.py 		
│   │   ├── patient_data/
│   │   │   ├── patient_data_query_context.py 
│   │   │   ├── patient_data_query_stategy.py      
│   │   │	├── patient_data_reader.py
│   │   │   └──	factories/
│   │   │		├── base_patient_data_factory.py
│   │   │		└── patient_data_factories.py
│   │   ├── segmentation/
│   │   │   ├──	segmentation_context.py
│   │   │   ├──	segmentation_reader.py
│   │   │	├── segmentation_strategy.py
│   │   │   └──	factories/
│   │   │		├── base_segmentation_factory.py
│   │   │		├── nrrd_segmentation_factories.py
│   │   │		├── segment.py
│   │   │		└── segmentation.py
│   ├── datasets/
│   │   ├── hdf5_dataset.py
│   │   └── tools/
│   │   	├──segmentation_filename_patterns_matcher.py
│   ├── __main__.py
│   ├── data_model.py
│   ├── logging_tools.py
│   ├── root.py
│   └── utils.py
├── LICENSE
├── ProjectTree.md
├── README.md
├── requirements.txt
└── setup.py
```
