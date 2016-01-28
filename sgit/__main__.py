import argparse
import os
import os.path
import shlex
import subprocess
import sys

from . import Sgit

PATHS = [
    os.environ.get('SGIT_PATH', None),
    os.path.expanduser('~/.sgit'),
    '/etc/sgit'
]

GIT_CMDS = {
    'git-receive-pack': 'push',
    'git-upload-pack': 'pull'
}

def get_cfg_path():
    for path in PATHS:
        if path is None:
            continue
        if os.path.isdir(path):
            return path
    raise Exception("No config path found!")

def get_ssh_cmd():
    return os.environ.get('SSH_ORIGINAL_COMMAND', None)

def get_sgit_shell_argparse():
    a = argparse.ArgumentParser()
    s = a.add_subparsers(dest='cmd')

    n = s.add_parser('create-repo')
    n.add_argument('path')

    n = s.add_parser('create-user')
    n.add_argument('username')
    n.add_argument('ssh_key')

    n = s.add_parser('add-users-to-repo')
    n.add_argument('path')
    n.add_argument('users', nargs='+')

    return a

def sgit_shell():
    if len(sys.argv) < 3 or sys.argv[1] != '-c':
        return 255
    sys.stderr.write("%r\n" % sys.argv)
    sys.stderr.flush()

    a = get_sgit_shell_argparse()

    user = sys.argv[2]
    sgit = Sgit(user, get_cfg_path())

    orig_cmd = get_ssh_cmd()
    if orig_cmd is None:
        return 1
    sys.stderr.write("%r\n" % orig_cmd)
    sys.stderr.flush()

    # Handle ordinary git ssh calls
    cmd_args = shlex.split(orig_cmd)
    first = cmd_args[0]
    if first in GIT_CMDS:
        if (GIT_CMDS[first] == 'push' and sgit.can_push_repo(cmd_args[1])) or \
                (GIT_CMDS[first] == 'pull' and sgit.can_pull_repo(cmd_args[1])):
            sys.stderr.write("%r\n" % cmd_args)
            sys.stderr.flush()
            subprocess.check_call(['git-shell', '-c'] + cmd_args)
            sys.stderr.write("Done!\n")
            sys.stderr.flush()
        else:
            return 2

    # Handle sgit world
    args = a.parse_args(shlex.split(orig_cmd))
    if args.cmd == 'create-repo':
        sgit.create_repo(args.path)
    elif args.cmd == 'create-user':
        sgit.create_user(args.username, args.ssh_key)
    elif args.cmd == 'add-users-to-repo':
        sgit.add_users_to_repo(args.path, args.users)
    else:
        return 3

def sgit():
    print("TODO!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {sgit,sgit-shell} [-h] ...")

    if sys.argv[1] == 'sgit':
        sgit()
    elif sys.argv[1] == 'sgit-shell':
        sgit_shell(sys.argv[2])
