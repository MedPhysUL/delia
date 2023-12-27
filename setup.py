import setuptools

setuptools.setup(
    name="delia",
    version="1.2.7",
    author="Maxence Larose",
    author_email="maxence.larose.1@ulaval.ca",
    description="DICOM Extraction for Large-scale Image Analysis (DELIA).",
    long_description=open('README.md', "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MaxenceLarose/delia",
    license="Apache License 2.0",
    keywords='dicom hdf5 medical image segmentation pre-processing python3 radiomics deep-learning dicom-seg rt-struct',
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "h5py",
        "monai==1.0.1",
        "numpy",
        "pandas",
        "pydicom",
        "pydicom-seg",
        "rt_utils",
        "scikit-image",
        "SimpleITK"
    ],
)
