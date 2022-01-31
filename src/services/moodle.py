import requests
import json
from typing import Optional, Union, Dict, List
from src.settings import moodle


def call_moodle_function(function_name: str, params: Optional[Dict] = None) -> Union[List[Dict], Dict]:
    """
        Make a request to the moodle API.
        :param function_name: The moodle function.
        :param params: Function params.
    """
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


def get_course_contents(course_id):
    """
        Get details from a course.
    """
    return call_moodle_function('core_course_get_contents', {'courseid': course_id})


def get_users_enrolled_in_course(course_id):
    """
        Get user from a course.
    """
    return call_moodle_function('core_enrol_get_enrolled_users', {'courseid': course_id})


def get_courses():
    """
        Get all courses.
    """
    return call_moodle_function('core_course_get_courses')


def get_course_activity_status(user_id, course_id):
    """
        Get user activity status from a course.
    """
    return call_moodle_function('core_completion_get_activities_completion_status', params={'userid': user_id, 'courseid': course_id})


class MoodleFunctionException(Exception):
    pass
