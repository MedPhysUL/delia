# Project Tree

```
|_📂 dicom2hdf/
  |_📂 data_generators/
    |_📄 patient_data_generator.py
  |_📂 data_readers/
    |_📂 dicom/
	  |_📄 dicom_reader.py
	|_📂 patient_data/
	  |_📄 patient_data_query_context.py
	  |_📄 patient_data_query_stategy.py
	  |_📄 patient_data_reader.py
	  |_📂 factories/
		|_📄 base_patient_data_factory.py
		|_📄 patient_data_factories.py
	|_📂 segmentation/
	  |_📄 segmentation_context.py
	  |_📄 segmentation_reader.py
	  |_📄 segmentation_strategy.py
	  |_📂 factories/
	    |_📄 base_segmentation_factory.py
	    |_📄 nrrd_segmentation_factories.py
	    |_📄 segment.py
	    |_📄 segmentation.py
  |_📂 datasets/
	|_📄 patient_dataset.py
	|_📂 tools/
	  |_📄 segmentation_filename_patterns_matcher.py
|_📄 __main__.py
|_📄 data_model.py
|_📄 logging_tools.py
|_📄 root.py
|_📄 utils.py
|_📄 LICENSE
|_📄 ProjectTree.md
|_📄 README.md
|_📄 requirements.txt
|_📄 setup.py
```
