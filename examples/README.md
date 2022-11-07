# Examples

The data used for the examples come from the public archive [TCIA](https://wiki.cancerimagingarchive.net/display/Public/NSCLC+Radiogenomics). 

[Download the data](https://wiki.cancerimagingarchive.net/display/Public/NSCLC+Radiogenomics) and place the patient records R01-005, R01-012 and R01-014 in a folder named `patients`. The structure of the `examples` folder should therefore be as follows:

```
|_📂 examples
  |_📄 ex01
  |_📄 ex02
  |_📂 data/
    |_📂 patients/
      |_📂 R01-005/
       	|_📂 ...
      |_📂 R01-012/
       	|_📂 ...
      |_📂 R01-014/
       	|_📂 ...
```

Note that only patients with IDs starting with R01 are used, as patients with AMC have no associated organ segmentation.



You are now ready to run all examples.
