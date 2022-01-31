import json
from typing import Optional
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from src.settings import output_path
from pathlib import Path

# Meta file is used to save google drive file id for an output file.
# It's used to replace files instead of creating new one for the same file name.
metadata_file = output_path/'googledrive_files_metadata.json'


def get_googledrive_file_id(filename: str) -> Optional[str]:
    """
        Get the google file id matching the filename.
    """
    with open(metadata_file, 'r') as f:
        data = json.loads(f.read())

    if filename in data:
        return data[filename]['id']

    return None


def save_googledrive_file_id(filename: str, id: str) -> None:
    """
        Save the google file id reference, so if we need to send the same file again (with the same name),
        the file is replaced instead of created.
    """
    f = open(metadata_file, 'r')
    data = json.loads(f.read())
    f.close()

    data[filename] = {
        'filename': filename,
        'id': id
    }

    with open(metadata_file, 'w') as f:
        json.dump(data, f)


def send_file_to_googledrive(file_path: Path, file_name: str, folder_id=None) -> None:
    """
        Upload file to google drive.
        :param file_path: The path of the file who will be uploaded.
        :param file_name: The name of the file in google drive.
        :folder_id: The folder id where the file will be placed.
    """
    config_path = Path(__file__).resolve().parent
    auth = GoogleAuth(config_path/'settings.yaml')
    drive = GoogleDrive(auth)

    metadata = {'title': file_name}

    file_id = get_googledrive_file_id(file_path.name)

    if file_id:
        metadata.update({'id': file_id})

    if folder_id:
        metadata.update(
            {'parents': [{'kind': 'drive#fileLink', 'id': folder_id}]})

    file = drive.CreateFile(metadata)
    file.SetContentFile(file_path)
    file.Upload()

    save_googledrive_file_id(file_path.name, file['id'])
