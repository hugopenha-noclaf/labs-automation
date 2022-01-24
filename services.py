class InputInterface:
    def __init__(self, arguments):
        self.arguments = arguments


class OutputInterface:
    def message(self, msg):
        print(msg)

    def error(self, msg):
        print(f'ERROR> {msg}')
