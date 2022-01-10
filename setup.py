import setuptools
from src.__init__ import __version__

setuptools.setup(
    name="dicom2hdf",
    version=__version__,
    author="Maxence Larose",
    author_email="maxence.larose.1@ulaval.ca",
    description="Medical data formatting and pre-processing module whose main objective"\
                " is to build an HDF5 dataset containing all medical images of patients"\ 
                " (DICOM format) and their associated segmentations. The HDF5 dataset"\ 
                " is then easier to use to perform tasks on the medical data, such as"\
                " machine learning tasks.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MaxenceLarose/DicomToHDF5",
    license="Apache License 2.0",
    keywords='dicom hdf5 medical image segmentation pre-processing',
    package_dir={"": "src"},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "colorama == 0.4.4",
        "cycler == 0.11.0",
        "fonttools == 4.28.1",
        "h5py == 3.4.0",
        "kiwisolver == 1.3.2",
        "matplotlib == 3.5.0",
        "numpy == 1.21.2",
        "packaging == 21.3",
        "Pillow == 8.4.0",
        "pydicom == 2.2.2",
        "pynrrd == 0.4.2",
        "pyparsing == 3.0.6",
        "python - dateutil == 2.8.2",
        "setuptools - scm == 6.3.2",
        "SimpleITK == 2.1.1",
        "six == 1.16.0",
        "tomli == 1.2.2",
        "tqdm == 4.62.3",
    ],
)
