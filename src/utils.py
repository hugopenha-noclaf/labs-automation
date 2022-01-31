import csv
from pathlib import Path
import re
from datetime import datetime
from typing import List, Optional, Union

from src.services.google_drive.google_drive import send_file_to_googledrive
from src.settings import google_drive


def save_csv_file(file_path: str, rows: Optional[List] = None, header: Optional[List] = None, mode: str = 'w') -> None:
    """
        Save the content in the list 'rows' into a csv file.
        If the mode param is igual to 'a', then the content will be appended in the end of file.
        :param file_path: The path of the file.
        :param rows: The content of the file.
        :param header: The header of the file (If informed).
        :param mode: The mode of write. 'w' for creation, 'a' for append the content.
    """
    with open(file_path, mode) as file:
        writer = csv.writer(file)

        if header:
            writer.writerow(header)

        if rows:
            writer.writerows(rows)


def timestamp_to_datetime(timestamp: str) -> Union[int, datetime]:
    """
        Convert a timestamp into a datetime object. 
        Returns 0 if a falsy value is informed.
    """
    return 0 if not timestamp else datetime.fromtimestamp(timestamp)


def remove_html_tags(html_string: str):
    """
        Remove html tags from string.
    """
    pattern = re.compile('<.*?>')
    return re.sub(pattern, '', html_string)


def upload_file_to_googledrive_labs_folder(output_file: Path):
    """
        Upload the output file into folder 'LabsStats'.
        :param output_file: The output file to upload.
    """
    google_drive_file_name = '{0}_{1}'.format(
        datetime.now().strftime('%Y%m%d'), output_file.name)
    send_file_to_googledrive(
        output_file, google_drive_file_name, google_drive['folder_output'])
