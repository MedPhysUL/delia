# Project Tree

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
