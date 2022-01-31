from src.services.moodle import MoodleFunctionException, get_course_contents, get_courses
from src.commands.base import BaseCommand
from src.utils import remove_html_tags, save_csv_file, upload_file_to_googledrive_labs_folder
from src.settings import output_path


class GetCoursesWithModules(BaseCommand):
    description = 'Get the list of courses with their modules.'

    def execute(self):
        """
            This command fetches all courses and with their modules.
        """
        output_file = output_path/'moodle_courses_with_modules.csv'

        header = ['Id curso', 'Nome curso',
                  'Nome curso abreviado', 'Categoria curso', 'Sumário curso', 'Id seção', 'Nome Seção', 'Sumário seção', 'Id módulo', 'Nome módulo']

        save_csv_file(file_path=output_file, header=header)

        rows = []
        self.output.message('Fetching courses...')
        courses = self.get_courses()

        for c in courses:
            self.output.message(f"Fetching modules for course {c['name']}")
            modules = self.get_course_modules(c['id'])

            for m in modules:
                row = [
                    c['id'], c['name'], c['short_name'], c['category_id'], c['summary'], m['section_id'], m[
                        'section_name'], m['section_summary'],  m['module_id'], m['module_name']
                ]
                rows.append(row)

        self.output.message('Saving output file...')
        save_csv_file(file_path=output_file, rows=rows, mode='a')

        if self.input.arguments['upload_drive']:
            self.output.message('Uploading file to google drive...')
            upload_file_to_googledrive_labs_folder(output_file)

        self.output.message('Well done!')

    def get_courses(self):
        """
            Fetch the courses.
        """
        try:
            courses = get_courses()
            data = []

            for c in courses:
                data.append({
                    'id': c['id'],
                    'name': c['fullname'],
                    'short_name': c['shortname'],
                    'category_id': c['categoryid'],
                    'summary': remove_html_tags(c['summary'])
                })

            return data
        except MoodleFunctionException:
            return []

    def get_course_modules(self, course_id):
        """
            Fetch the course modules.
        """
        try:
            sections = get_course_contents(course_id)
            data = []
            for s in sections:
                for m in s['modules']:
                    data.append({
                        'section_summary': remove_html_tags(s['summary']),
                        'section_name': s['name'],
                        'section_id': s['section'],
                        'module_name': m['name'],
                        'module_id': m['id'],
                    })

            return data
        except MoodleFunctionException:
            return []
