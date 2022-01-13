"""
    @file:              logging_tools.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the logs_file_setup function, which allows the user to set the root logger
                        level to the specified level.
"""

import logging


def logs_file_setup(level=logging.INFO):
    import os
    import sys
    import time
    from datetime import date

    today = date.today()
    timestamp = str(time.time()).replace('.', '')
    logs_dir = f"logs/logs-{today.strftime('%d-%m-%Y')}"
    logs_file = f'{logs_dir}/{timestamp}.log'
    os.makedirs(logs_dir, exist_ok=True)
    logging.basicConfig(filename=logs_file, filemode='w+', level=level)
    handler = logging.StreamHandler(sys.stdout)
    logging.getLogger().addHandler(handler)
