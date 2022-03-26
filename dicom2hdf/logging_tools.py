"""
    @file:              logging_tools.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 03/2022

    @Description:       This file contains the configure_logging function, which allows the user to configure the
                        stream and file handlers of the dicom2hdf logger using the logging_conf.yaml file.
"""

from datetime import datetime
import logging
import logging.config
import os
import yaml


def configure_logging(path_to_configuration_file: str):
    now = datetime.now()
    logs_dir = f"logs/{now.strftime('%Y-%m-%d')}"
    logs_file = f"{logs_dir}/{now.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    os.makedirs(logs_dir, exist_ok=True)

    with open(path_to_configuration_file, 'r') as stream:
        config: dict = yaml.load(stream, Loader=yaml.FullLoader)

    config["handlers"]["file"]["filename"] = logs_file

    logging.config.dictConfig(config)
