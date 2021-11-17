from argparse import ArgumentParser


class Arguments:
    def __init__(self, programDescription: str):
        self.parser = ArgumentParser(description=programDescription)

    def add(self, args: str, inputType: type, help: str):
        assert args != None
        assert inputType != None
        assert help != None
        assert len(args) > 0
        assert len(help) > 0
        assert type(args) is str
        assert type(help) is str
        assert type(inputType) is type

        self.parser.add_argument(args, help=help, type=inputType)
        return self

    def __getattr__(self, name: str):
        assert name != None
        assert type(name) is str

        return self.parser.parse_args().__getattribute__(name)
