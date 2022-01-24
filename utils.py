from datetime import datetime
import requests
import json
import csv
from typing import Dict, List, Optional, Union
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from exceptions import MoodleFunctionException
from conf import moodle


def get_googledrive_file_id(filename):
    with open('outputs/googledrive_files_metadata.json', 'r') as f:
        data = json.loads(f.read())

    if filename in data:
        return data[filename]['id']

    return None


def save_googledrive_file_id(filename, id):
    f = open('outputs/googledrive_files_metadata.json', 'r')
    data = json.loads(f.read())
    f.close()

    data[filename] = {
        'filename': filename,
        'id': id
    }

    with open('outputs/googledrive_files_metadata.json', 'w') as f:
        json.dump(data, f)


def send_file_to_googledrive(filename: str, file_name: str, folder_id=None) -> None:
    auth = GoogleAuth()
    drive = GoogleDrive(auth)

    metadata = {'title': file_name}

    file_id = get_googledrive_file_id(filename)

    if file_id:
        metadata.update({'id': file_id})

    if folder_id:
        metadata.update(
            {'parents': [{'kind': 'drive#fileLink', 'id': folder_id}]})

    file = drive.CreateFile(metadata)
    file.SetContentFile(f'outputs/{filename}')
    file.Upload()

    save_googledrive_file_id(filename, file['id'])


def create_csv_file(header: List, rows: List, filename: str) -> None:
    with open(f'outputs/{filename}', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def timestamp_to_datetime(timestamp: str) -> Union[int, datetime]:
    return 0 if not timestamp else datetime.fromtimestamp(timestamp)


def call_moodle_function(function_name: str, params: Optional[Dict]) -> Union[List[Dict], Dict]:
    api_url = 'https://academy.faci.ly/webservice/rest/server.php'

    payload = {
        'wstoken': moodle['token'],
        'moodlewsrestformat': 'json',
        'wsfunction': function_name,
    }

    if params:
        payload.update(params)

    response = requests.get(api_url, params=payload)

    result = json.loads(response.text)

    if 'exception' in result:
        raise MoodleFunctionException(
            f"Failed to execute moodle function. Details: '{result['message']}'")

    return result
