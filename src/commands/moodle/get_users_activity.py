from datetime import datetime
from pathlib import Path
from typing import List
from src.commands.base import BaseCommand
from src.services.google_drive.google_drive import send_file_to_googledrive
from src.services.moodle import MoodleFunctionException, call_moodle_function
from src.utils import save_csv_file, timestamp_to_datetime, upload_file_to_googledrive_labs_folder
from src.settings import output_path


class GetUsersActivity(BaseCommand):
    description = 'Get users access activity.'

    def execute(self):
        """
            This command fetch the access activity of all users.
        """

        output_file = output_path/'moodle_users_activity.csv'

        self.output.message('Fetching users...')
        users = self.get_users()
        self.output.message('Done!')

        self.output.message('Saving result into file...')
        self.save_users(users, output_file)
        self.output.message('Done!')

        if self.input.arguments['upload_drive']:
            self.output.message('Uploading file to google drive...')
            upload_file_to_googledrive_labs_folder(output_file)

        self.output.message('Well done!')

    def get_users(self):
        """
            Fetch users.
        """
        try:
            return call_moodle_function(
                'core_enrol_get_enrolled_users', {'courseid': 1})
        except MoodleFunctionException as e:
            self.output.error(str(e))
            return []

    def save_users(self, users: List, file_path: Path):
        """
            Save users into output file.
        """
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
