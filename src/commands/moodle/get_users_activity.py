from datetime import datetime
from pathlib import Path
from typing import List
from src.commands.base import BaseCommand
from src.services.google_drive.google_drive import send_file_to_googledrive
from src.services.moodle import MoodleFunctionException, call_moodle_function
from src.settings import google_drive
from src.utils import save_csv_file, timestamp_to_datetime
from src.settings import output_path


class GetUsersActivity(BaseCommand):
    description = 'Get users access activity.'

    def execute(self):
        output_file = output_path/'moodle_users_activity.csv'

        self.output.message('Fetching users...')
        users = self.get_users()
        self.output.message('Done!')

        self.output.message('Saving result into file...')
        self.save_users(users, output_file)
        self.output.message('Done!')

        if self.input.arguments['upload_drive']:
            self.send_file_to_drive(output_file)

        self.output.message('Well done!')

    def get_users(self):
        try:
            return call_moodle_function(
                'core_enrol_get_enrolled_users', {'courseid': 1})
        except MoodleFunctionException as e:
            self.output.error(str(e))
            return []

    def save_users(self, users: List, file_path: Path):
        rows = []
        for row in users:
            last_access = timestamp_to_datetime(row['lastaccess'])
            fullname = row['fullname']
            email = row['email']
            departament = row['department']
            last_course_access = timestamp_to_datetime(row['lastcourseaccess'])

            rows.append([fullname, email, departament, last_access,
                        last_course_access])

        header = ['Fullname', 'Email', 'Departament',
                  'Last access', 'Last course access']
        save_csv_file(file_path, rows, header)

    def send_file_to_drive(self, file_path):
        self.output.message('Uploading file to google drive...')
        google_drive_file_name = 'moodle_users_activity_{0}.csv'.format(
            datetime.now().strftime('%Y%m%d'))

        send_file_to_googledrive(
            file_path, google_drive_file_name, google_drive['folder_output'])

        self.output.message('Done!')
