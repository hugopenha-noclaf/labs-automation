from datetime import datetime
from exceptions import MoodleFunctionException
from services import InputInterface, OutputInterface
from utils import (send_file_to_googledrive, create_csv_file,
                   timestamp_to_datetime, call_moodle_function)
from conf import google_drive


def get_moodle_users_activity(input_interface: InputInterface,  output: OutputInterface):
    filename = 'moodle_users_activity.csv'

    output.message('Fetching users...')
    try:
        users = call_moodle_function(
            'core_enrol_get_enrolled_users', {'courseid': 1})
    except MoodleFunctionException as e:
        output.error(str(e))
        return

    output.message('Done!')

    output.message('Saving result into file...')
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
    create_csv_file(header, rows, filename)

    output.message('Done!')

    if input_interface.arguments['upload_drive']:
        output.message('Uploading file to google drive...')
        google_drive_file_name = 'moodle_users_activity_{0}.csv'.format(
            datetime.now().strftime('%Y%m%d'))

        send_file_to_googledrive(
            filename, google_drive_file_name, google_drive['folder_output'])

        output.message('Done!')

    output.message('Well done!')
