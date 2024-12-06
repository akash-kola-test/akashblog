import json
import logging
import pathlib


def setup_logging(config_file_path: str) -> None:
    config_file = pathlib.Path(config_file_path)
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)
