from typing import Dict, List, Optional
from src.commands.base import BaseCommand
from src.services.moodle import MoodleFunctionException, call_moodle_function, get_course_activity_status, get_course_contents, get_users_enrolled_in_course
from src.utils import save_csv_file, timestamp_to_datetime, upload_file_to_googledrive_labs_folder
from src.settings import output_path


class GetUserCourseActivities(BaseCommand):
    description = 'Get course activities with grades.'

    def execute(self) -> None:
        """
            This command fetch all activities for all users from a specific course.
            It fetches too the grades.
        """
        output_file = output_path/'moodle_user_grades.csv'

        self.course_id = self.input.arguments['course']

        if not self.course_id:
            raise Exception('The course must be informed')

        self.output.message('Fetching modules...')
        modules = self.get_course_modules()

        header = ['Nome usuário', 'Email usuário', 'Cargo usuário', 'Nome Módulo', 'Status', 'Data conclusão', 'Rastreio',
                  'Sobre escrito por', 'Nota', 'Nota enviada em', 'Data nota']
        save_csv_file(file_path=output_file, header=header)

        users = self.get_users()
        for user in users:
            self.output.message(f"Processing user {user['name']}")

            self.output.message('Fetching completion course status...')
            statuses = self.get_user_completion_course_status(user['id'])

            if not statuses:
                self.output.message(f'User has no course status')
                self.output.message('====')
                continue

            self.output.message('Fetching course grades...')
            grades = self.get_user_course_grades(user['id'])

            statuses = self.join_course_activities_statuses_with_grades(
                statuses, grades)

            rows = []
            for s in statuses:
                module_name = modules[s['module_id']]
                row = [user['name'], user['email'], user['department'], module_name,
                       s['status'], s['time_completed'], s['tracking'], s['override_by']]
                if 'grade' in s:
                    row.extend(
                        [s['grade'], s['grade_submitted'], s['date_graded']])

                rows.append(row)

            self.output.message('Saving result into file...')

            save_csv_file(file_path=output_file, rows=rows, mode='a')

            self.output.message('====')

        if self.input.arguments['upload_drive']:
            self.output.message('Uploading file to google drive...')
            upload_file_to_googledrive_labs_folder(output_file)

        self.output.message('Well done!')

    def get_user_completion_course_status(self, user_id) -> Optional[List[Dict]]:
        """
            Fetch the user completion status for a course.
        """
        try:
            response = get_course_activity_status(user_id, self.course_id)

            status_description = {
                0: 'Incompleto',
                1: 'Completo',
                2: 'Completo - Passou',
                3: 'Completo - Não passou'
            }

            tracking_description = {
                0: 'Nenhum',
                1: 'Manual',
                2: 'Automático'
            }

            data = []
            for i in response['statuses']:
                data.append({
                    'module_id': i['cmid'],
                    'module_name': i['modname'],
                    'status': status_description[i['state']],
                    'time_completed': timestamp_to_datetime(i['timecompleted']),
                    'tracking': tracking_description[i['tracking']],
                    'override_by': i['overrideby']
                })
            return data
        except MoodleFunctionException:
            return []

    def get_user_course_grades(self, user_id) -> Optional[List[Dict]]:
        """
            Get all grades od user from a course.
        """
        params = {'userid': user_id, 'courseid': self.course_id}
        try:
            response = call_moodle_function(
                'gradereport_user_get_grade_items', params)
            data = []
            for i in response['usergrades'][0]['gradeitems']:
                if i['itemmodule'] == 'quiz':
                    data.append({
                        'module_id': i['cmid'],
                        'module_type': i['itemmodule'],
                        'module_name': i['itemname'],
                        'grade': i['graderaw'],
                        'grade_submitted': timestamp_to_datetime(i['gradedatesubmitted']),
                        'date_graded': timestamp_to_datetime(i['gradedategraded'])
                    })

            return data
        except MoodleFunctionException:
            return []

    def get_course_modules(self):
        """
            Get all modules for the course.
        """
        try:
            result = get_course_contents(self.course_id)
            tiles = [{'tile_id': tile['id'], 'tile_name': tile['name'],
                     'modules': tile['modules']} for tile in result]

            modules = {}
            for tile in tiles:
                for m in tile['modules']:
                    modules[m['id']] = m['name']

            return modules
        except MoodleFunctionException:
            return None

    def join_course_activities_statuses_with_grades(self, statuses, grades):
        """
            For all activity status, try to find the grande. 
            If the grade for a module is found, then save the grades info into status line.
        """
        for s in statuses:
            for g in grades:
                if s['module_id'] == g['module_id']:
                    s.update(g)
        return statuses

    def get_users(self):
        """
            Get the users enrolled to the course.
        """
        try:
            users = get_users_enrolled_in_course(self.course_id)
            data = []
            for u in users:
                data.append({
                    'name': u['fullname'],
                    'id': u['id'],
                    'department': u['department'],
                    'email': u['email']
                })
            return data
        except MoodleFunctionException:
            return []
