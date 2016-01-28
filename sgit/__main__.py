import argparse
import os
import os.path
import shlex
import sys

from . import Sgit

PATHS = [
    os.path.expanduser('~/.sgit'),
    '/etc/sgit'
]

GIT_CMDS = ['git-receive-pack', 'git-upload-pack']

def get_cfg_path():
    for path in PATHS:
        cfg_path = os.path.join(path, 'config.json')
        if os.path.exists(cfg_path):
            return path
    raise Exception("No config path found!")

def get_ssh_cmd():
    return sys.environ.get('SSH_ORIGINAL_COMMAND', None)

def get_sgit_shell_argparse():
    a = ArgumentParser()
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

def sgit_shell(user):
    a = ArgumentParser()

    sgit = Sgit(user, get_cfg_path())

    orig_cmd = get_ssh_cmd()
    if orig_cmd is None:
        return 1

    # Handle ordinary git ssh calls
    first_arg = orig_cmd.split(' ', 1)[0]
    if first_arg in GIT_CMDS:
        if sgit.can_push_repo():
            os.execvp('git', ['shell', '-c'] + shlex.split(cmd))
        else:
            return 1

    # Handle sgit world
    args = a.parse_args(shlex.split(orig_cmd))
    if args.cmd == 'create-repo':
        sgit.create_repo(args.path)

    elif args.cmd == 'create-user':
        sgit.create_user(args.username, args.ssh_key)

    elif args.cmd == 'add-users-to-repo':
        sgit.add_users_to_repo(args.path, args.users)

    else:
        return 1

def sgit():
    print("TODO!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {sgit,sgit-shell} [-h] ...")

    if sys.argv[1] == 'sgit':
        sgit()
    elif sys.argv[1] == 'sgit-shell':
        sgit_shell(sys.argv[2])
