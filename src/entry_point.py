import argparse
import traceback
import sys


from src.commands.input_output import InputInterface, OutputInterface
from src.commands.handlers import handler_command


def entry_point():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='?',
                        help='The command you want to run')

    parser.add_argument('--upload-drive', action='store_true',
                        help='Whether the outfile should be sent to google drive')

    parser.add_argument('--user', action='store',
                        help='Id of the moodle\'s user')

    parser.add_argument('--course', action='store',
                        help='Id of the course\'s user')

    args = parser.parse_args()

    try:
        output_interface = OutputInterface()
        input_interface = InputInterface(vars(args))
        handler_command(args.command, input_interface, output_interface)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
