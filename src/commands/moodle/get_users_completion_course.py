from src.services.moodle import MoodleFunctionException, get_course_activity_status, get_course_contents, get_users_enrolled_in_course
from src.commands.base import BaseCommand
from src.utils import save_csv_file, upload_file_to_googledrive_labs_folder
from src.settings import output_path


class GetUsersCompletionCourse(BaseCommand):
    description = 'Get the completions status of all users in a course.'

    def execute(self):
        """
            This command get the status of completions of all users for a course.
            It build a report with the completion status for all modules of the course
            and the course completion status (if the user has completed 100% the course).
        """
        if not self.input.arguments['course']:
            raise Exception('The course must be informed.')

        output_file = output_path/'moodle_users_completion_course.csv'
        self.course_id = self.input.arguments['course']

        self.output.message('Fetching users...')
        users = get_users_enrolled_in_course(self.course_id)

        self.output.message('Fecthing modules...')
        modules = self.get_course_modules()

        # Modules that are requirements to the course completion.
        modules_completion_requirement = [m['module_id']
                                          for m in modules if m['has_completion']]
        modules_completion_requirement.sort()

        header = ['Id usuário', 'Nome usuário', 'Nome Seção',
                  'Id módulo', 'Nome módulo', 'Módulo é requisito para conclusão', 'Concluiu o módulo', 'Concluiu o curso']
        save_csv_file(file_path=output_file, header=header)
        for u in users:
            rows = []
            self.output.message(f"Processing user {u['fullname']}")

            self.output.message('Fetching activities')
            activities = self.get_user_course_activities(u['id'])

            # Modules that were completed.
            modules_completed = [a['module_id']
                                 for a in activities if a['has_completed']]
            modules_completed.sort()

            # Check if the user completed 100% of course.
            # The logic is if the user completed all modules that are a requirement to the course.
            has_course_completed = 'Sim' if modules_completed == modules_completion_requirement else 'Não'

            for m in modules:
                has_completed = 'Sim' if m['module_id'] in modules_completed else 'Não'
                module_has_completion = 'Sim' if m['has_completion'] else 'Não'
                row = [
                    u['id'], u['fullname'], m['section_name'], m['module_id'], m['module_name'], module_has_completion, has_completed, has_course_completed
                ]
                rows.append(row)

            save_csv_file(file_path=output_file, rows=rows, mode='a')

        if self.input.arguments['upload_drive']:
            self.output.message('Uploading file to google drive...')
            upload_file_to_googledrive_labs_folder(output_file)

        self.output.message('Well done!')

    def get_course_modules(self):
        """
            Get the modules of a the course.
        """
        try:
            course_contents = get_course_contents(self.course_id)
            data = []
            for c in course_contents:
                for m in c['modules']:
                    data.append({
                        'section_name': c['name'],
                        'module_name': m['name'],
                        'module_id': m['id'],
                        # Indicate wether this module is a requirement for the course complestion.
                        'has_completion': 'completiondata' in m
                    })

            return data

        except MoodleFunctionException:
            return None

    def get_user_course_activities(self, user_id):
        """
            Get the user activity status for the course.
        """
        try:
            activities = get_course_activity_status(
                user_id, self.course_id)

            data = []
            for a in activities['statuses']:
                data.append({
                    'module_id': a['cmid'],
                    'has_completed': a['timecompleted'] != 0
                })

            return data
        except MoodleFunctionException:
            return None
