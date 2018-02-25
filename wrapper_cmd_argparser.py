# Most of this code comes from https://codereview.stackexchange.com/questions/134333/using-argparse-module-within-cmd-interface
# thanks to the Ramon, the person who made the post
import tempfile, shlex
class WrapperCmdLineArgParser:
    def __init__(self):
        """Init decorator"""
        self.parser = None
        self.help_msg = ""

    def __call__(self, f):
        """Decorate 'f' to parse 'line' and pass options to decorated function"""
        self.parser = f(None, None, None, True)

        def wrapped_f(*args):
            try:
                line = shlex.split(args[1])
            except Exception as e:
                print("Error:", e)
                return

            try:
                parsed = self.parser.parse_args(line)
            except SystemExit:
                return
            f(*args, parsed=parsed)

        wrapped_f.__doc__ = self.__get_help(self.parser)
        return wrapped_f

    @staticmethod
    def __get_help(parser):
        """Get and return help message from 'parser.print_help()'"""
        f = tempfile.SpooledTemporaryFile(max_size=2048, mode='w')
        parser.print_help(file=f)
        f.seek(0)
        return f.read().rstrip()
