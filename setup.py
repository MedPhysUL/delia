import setuptools

setuptools.setup(
    name="dicom2hdf",
    version="0.2.2",
    author="Maxence Larose",
    author_email="maxence.larose.1@ulaval.ca",
    description="Medical data formatting and pre-processing module whose main objective"\
                " is to build an HDF5 dataset containing all medical images of patients"\
                " (DICOM format) and their associated segmentations. The HDF5 dataset"\
                " is then easier to use to perform tasks on the medical data, such as"\
                " machine learning tasks.",
    long_description=open('README.md', "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MaxenceLarose/dicom2hdf",
    license="Apache License 2.0",
    keywords='dicom hdf5 medical image segmentation pre-processing python3',
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "h5py",
        "numpy",
        "pydicom",
        "pydicom-seg",
        "SimpleITK",
        "tqdm",
        "rt_utils"
    ],
)
