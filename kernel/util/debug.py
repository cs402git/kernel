import gdb

import weenix
import weenix.info

class InfoCommand(weenix.Command):
    """usage: info <infofunc> [<data>]
    <infofunc> the info function to be called
    <data>     the first argument to <infofunc>, if unspecified NULL is used
    Prints the string generated by one of the kernel's info functions."""

    def __init__(self):
        weenix.Command.__init__(self, "info",
                                gdb.COMMAND_DATA,
                                gdb.COMPLETE_SYMBOL)

    def invoke(self, arg, tty):
        args = gdb.string_to_argv(arg)
        if (len(args) < 1 or len(args) > 2):
            gdb.write("{0}\n".format(self.__doc__))
            raise gdb.GdbError("invalid arguments")
        gdb.write(weenix.info.string(args[0], args[1] if (len(args) > 1) else None))

InfoCommand()

class DbgCommand(weenix.Command):
    """usage: dbg [<modes>]
    <modes>  any number of whitespace seperated debug modes
    When no arguments are given prints a list of all active debug
    modes. If any debug modes are listed they are added to the
    current debug modes. If a listed mode is prefixed with a
    '-' it is removed instead of added."""

    def __init__(self):
        weenix.Command.__init__(self, "dbg",
                                gdb.COMMAND_DATA)

    def _modes(self):
        i = 0
        l = list()
        while (gdb.parse_and_eval("dbg_tab[{0}]".format(i))["d_name"] != 0):
            mode = gdb.parse_and_eval("dbg_tab[{0}]".format(i))
            i += 1
            l.append(mode["d_name"].string())
        return l

    def invoke(self, arg, tty):
        if (len(arg.strip()) == 0):
            info = weenix.info.string("dbg_modes_info")
            if (len(info) == 0):
                gdb.write("No active modes.\n")
            else:
                gdb.write("{0}\n".format(weenix.info.string("dbg_modes_info")))
        else:
            modes = self._modes()
            for mode in arg.split():
                name = mode[1:] if (mode.startswith("-")) else mode
                if (not name in modes):
                    gdb.write("warning: skipping non-existant mode \"{0}\"\n"
                              .format(name))
                else:
                    weenix.eval_func("dbg_add_mode", "\"{0}\"".format(mode))

    def complete(self, line, word):
        l = self._modes()
        l = filter(lambda x: x.startswith(word), l)
        for used in line.split():
            if (used.startswith("-")):
                used = used[1:]
            l = filter(lambda x: x != used, l)
        l.sort()

        return l

DbgCommand()
