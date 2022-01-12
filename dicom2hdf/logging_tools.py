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


if __name__ == '__main__':
    logs_file_setup(logging.DEBUG)
