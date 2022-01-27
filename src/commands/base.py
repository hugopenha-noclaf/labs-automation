import abc
from src.commands.input_output import InputInterface, OutputInterface


class BaseCommand(abc.ABC):
    description = 'Command description'

    def __init__(self, input_interface: InputInterface,  output_interface: OutputInterface) -> None:
        self.input = input_interface
        self.output = output_interface

    @abc.abstractmethod
    def execute(self):
        pass
