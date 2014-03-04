"""
The main command-line entry point.
"""

import sys
import argparse
from rez import __version__



p = argparse.ArgumentParser(
    description='Rez command-line tool',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subps = p.add_subparsers(dest="cmd")
subparsers = {}


# lazily loads subcommands, gives faster load time
subcmd = (sys.argv[1:2] + [None])[0]
def subcommand(fn):
    def _fnull(*nargs, **kwargs):
        pass
    def _fn(*nargs, **kwargs):
        fn(*nargs, **kwargs)
    if fn.__name__ == ("add_%s" % str(subcmd)):
        return _fn
    else:
        return _fnull

def _add_common_args(subp):
    subp.add_argument("--debug", dest="debug", action="store_true",
                      help=argparse.SUPPRESS)

def _subcmd_name(cli_name):
    if cli_name in ("exec",):
        return cli_name+'_'
    else:
        return cli_name.replace('-','_')

@subcommand
def add_settings(parser):
    parser.add_argument("-p", "--param", type=str,
                        help="print only the value of a specific parameter")
    parser.add_argument("--pp", "--packages-path", dest="pkgs_path", action="store_true",
                        help="print the package search path, including any "
                        "system paths")

@subcommand
def add_context(parser):
    from rez.system import system
    from rez.shells import get_shell_types
    formats = get_shell_types() + ['dict']

    parser.add_argument("--print-request", dest="print_request", action="store_true",
                        help="print only the request list, including implicits")
    parser.add_argument("--print-resolve", dest="print_resolve", action="store_true",
                        help="print only the resolve list")
    parser.add_argument("-g", "--graph", action="store_true",
                        help="display the resolve graph as an image")
    parser.add_argument("--pg", "--print-graph", dest="print_graph", action="store_true",
                        help="print the resolve graph as a string")
    parser.add_argument("--wg", "--write-graph", dest="write_graph", type=str,
                        metavar='FILE', help="write the resolve graph to FILE")
    parser.add_argument("--pp", "--prune-package", dest="prune_pkg", metavar="PKG",
                        type=str, help="prune the graph down to PKG")
    parser.add_argument("--pc", "--prune-conflict", dest="prune_conflict", action="store_true",
                        help="prune the graph down to show conflicts only")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print more information about the context. "
                        "Ignored if --interpret is used.")
    parser.add_argument("-i", "--interpret", action="store_true",
                        help="interpret the context and print the resulting code")
    parser.add_argument("-f", "--format", type=str, choices=formats,
                        help="print interpreted output in the given format. If "
                        "None, the current shell language (%s) is used. If 'dict', "
                        "a dictionary of the resulting environment is printed. "
                        "Ignored if --interpret is False" % system.shell)
    parser.add_argument("--no-env", dest="no_env", action="store_true",
                        help="interpret the context in an empty environment")
    parser.add_argument("FILE", type=str, nargs='?',
                        help="rex context file (current context if not supplied)")

@subcommand
def add_env(parser):
    from rez.system import system
    from rez.shells import get_shell_types
    shells = get_shell_types()
    print_types = ("resolve", "context", "script", "dict")

    parser.add_argument("--sh", "--shell", dest="shell", type=str, choices=shells,
                        help="target shell type, defaults to the current shell "
                        "(%s)" % system.shell)
    parser.add_argument("--rcfile", type=str,
                        help="source this file instead of the target shell's "
                        "standard startup scripts, if possible")
    parser.add_argument("--norc", action="store_true",
                        help="skip loading of startup scripts")
    parser.add_argument("-c", "--command", type=str,
                        help="read commands from string")
    parser.add_argument("-s", "--stdin", action="store_true",
                        help="read commands from standard input")
    parser.add_argument("--ni", "--no-implicit", dest="no_implicit",
                        action="store_true",
                        help="don't add implicit packages to the request")
    parser.add_argument("--nl", "--no-local", dest="no_local", action="store_true",
                        help="don't load local packages")
    parser.add_argument("--bo", "--bootstrap-only", dest="bootstrap_only",
                        action="store_true",
                        help="only load bootstrap packages. Implies --ni and --nl.")
    parser.add_argument("--print", type=str, dest="print_", metavar="TYPE",
                        choices=print_types,
                        help="print information about the resolved environment, "
                        "rather than spawning it")
    parser.add_argument("-t", "--time", type=str,
                        help="ignore packages released after the given time. "
                        "Supported formats are: epoch time (eg 1393014494), "
                        "or relative time (eg -10s, -5m, -0.5h, -10d)")
    parser.add_argument("--mf", "--max-fails", dest="max_fails", type=int,
                        default=-1, metavar='N',
                        help="exit when the number of failed configuration "
                        "attempts exceeds N")
    parser.add_argument("-o", "--output", type=str,
                        help="store the context into an rxt file, instead of "
                        "starting an interactive shell. Note that this will "
                        "also store a failed resolve")
    parser.add_argument("--rxt", "--context", dest="rxt", type=str,
                        help="use a previously saved context. Resolve settings, "
                        "such as PKG, --ni etc are ignored in this case")
    parser.add_argument("--rv", "--resolve-verbosity", dest="resolve_verbosity",
                        type=int, default=0,
                        help="print debugging info during the resolve process")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="run in quiet mode")
    parser.add_argument("PKG", type=str, nargs='*',
                        help='packages to use in the target environment')

@subcommand
def add_exec(parser):
    from rez.system import system
    from rez.shells import get_shell_types
    formats = get_shell_types() + ['dict']

    parser.add_argument("-f", "--format", type=str, choices=formats,
                        help="print output in the given format. If None, the "
                        "current shell language (%s) is used. If 'dict', a "
                        "dictionary of the resulting environment is printed"
                        % system.shell)
    parser.add_argument("--no-env", dest="no_env", action="store_true",
                        help="interpret the code in an empty environment")
    parser.add_argument("--pv", "--parent-variables", dest="parent_vars",
                        type=str, metavar='VARS',
                        help="comma-seperated list of environment variables to "
                        "update rather than overwrite on first reference. If "
                        "this is set to the special value 'all', all variables "
                        "will be treated this way")
    parser.add_argument("FILE", type=str,
                        help='file containing rex code to execute')

@subcommand
def add_test(parser):
    parser.add_argument("--shells", action="store_true",
                        help="test shell invocation")
    parser.add_argument("-v", "--verbosity", type=int, default=2,
                        help="set verbosity level")

@subcommand
def add_bootstrap(parser):
    from rez.shells import get_shell_types
    from rez.system import system
    shells = get_shell_types()
    parser.add_argument("--install-path", dest="install_path", type=str,
                        help="create a production-ready install of Rez in the "
                        "given path")
    parser.add_argument("--sh", "--shell", dest="shell", type=str, choices=shells,
                        help="target shell type of the install, defaults to the "
                        "current shell (%s)" % system.shell)


def _add_subcommand(cmd, help):
    subp = subps.add_parser(cmd, help=help)
    _add_common_args(subp)
    globals()["add_%s" % cmd](subp)
    subparsers[cmd] = subp


def run():
    _add_subcommand("settings",
                    "Print current rez settings.")
    _add_subcommand("context",
                    "Print information about the current rez context, or a "
                    "given context file.")
    _add_subcommand("env",
                    "Open a rez-configured shell, possibly interactive.")
    _add_subcommand("exec",
                    "Execute some Rex code and print the interpreted result")
    _add_subcommand("bootstrap",
                    "Rez installation-related operations")
    _add_subcommand("test",
                    "Run unit tests")

    p.add_argument("-V", "--version", action="version",
                   version="Rez %s" % __version__)

    opts = p.parse_args()
    cmd = opts.cmd
    exec("from rez.cli.%s import command" % _subcmd_name(cmd))

    exc_type = None if opts.debug else Exception
    try:
        returncode = command(opts, subparsers[cmd])
    except NotImplementedError as e:
        import traceback
        raise Exception(traceback.format_exc())
    except exc_type as e:
        print >> sys.stderr, "rez: %s: %s" \
                             % (e.__class__.__name__, str(e))
        sys.exit(1)

    sys.exit(returncode or 0)
