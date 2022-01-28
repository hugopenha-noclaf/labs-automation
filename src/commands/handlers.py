from src.commands.moodle.get_users_completion_course import GetUsersCompletionCourse
from src.commands.input_output import InputInterface, OutputInterface
from src.commands.moodle.get_courses_with_modules import GetCoursesWithModules
from src.commands.moodle.get_user_course_activities import GetUserCourseActivities
from src.commands.moodle.get_users_activity import GetUsersActivity


handlers = {
    'moodle:users_getactivity': GetUsersActivity,
    'moodle:users_getcourseactivities': GetUserCourseActivities,
    'moodle:courses_getall': GetCoursesWithModules,
    'moodle:course_completion_status': GetUsersCompletionCourse
}


def handler_command(command_name: str, input_interface: InputInterface, output_interface: OutputInterface):
    if command_name not in handlers:
        if command_name != None:
            output_interface.message(f'Command [{command_name}] not found!!\n')
        output_interface.message('Available commands:\n')

        for k in handlers.keys():
            output_interface.message(f"- {k} \n\t {handlers[k].description}")
        return

    command = handlers[command_name]
    command = command(input_interface, output_interface)
    command.execute()
