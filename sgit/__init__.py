from collections import OrderedDict
import io
import json
import os
import os.path
import shlex
import subprocess
import sys

CMD = 'command="{user}",no-port-forwarding,' \
      'no-X11-forwarding,no-agent-forwarding,no-pty'

CFG_TMPL = """\
{
  "users": {},
  "admins": [],
  "root": "/srv/git",
  "repos": {}
}
"""

class SgitException(Exception):
    pass

def prop(k):
    def pset(k):
        def wrapper(self, v):
            self._data[k] = v
        return wrapper

    def pget(k):
        def wrapper(self):
            return self._data[k]
        return wrapper
    return property(pget(k), pset(k))

class SgitConfig:
    @classmethod
    def with_defaults(cls, path):
        data = json.loads(CFG_TMPL, object_pairs_hook=OrderedDict)
        return cls(data, path)

    @classmethod
    def load(cls, path):
        with open(os.path.join(path, 'config.json')) as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
        return cls(data, path)

    def __init__(self, data, path):
        self._data = data
        self._path = path

    root = prop('root')
    users = prop('users')
    admins = prop('admins')
    repos = prop('repos')

    def resolve_path(self, repo_path):
        return os.path.join(self.root, repo_path)

    def generate_auth_keys_file(self):
        out = io.StringIO()
        for user, key in self.users.items():
            out.write("%s %s\n" % (CMD.format(user=user), key))
        return out.getvalue()

    def save(self):
        path = self._path
        with open(os.path.join(path, 'config.json'), 'w') as f:
            json.dump(self._data, f, indent=2)
        with open(os.path.join(path, 'ssh_keys'), 'w') as f:
            f.write(self.generate_auth_keys_file())

class Sgit:
    @classmethod
    def with_defaults(cls, cfg_path):
        config = SgitConfig.with_defaults(cfg_path)
        config.save()
        return cls(cfg_path)

    def __init__(self, user, cfg_path):
        self.config = SgitConfig.load(cfg_path)
        if user not in self.config.users:
            raise SgitException("User '%s' is not a valid user." % user)
        self.user = user

    def can_push_repo(self, repo_path):
        return user in self.config.repos[repo_path]['users']

    def can_pull_repo(self, repo_path):
        return self.can_push_repo(repo_path)

    def create_repo(self, repo_path):
        if self.user not in self.config.admins:
            raise SgitException(
                "User '%s' does not have correct permissions." % self.user)

        if repo_path in self.config.repos:
            raise SgitException("Repo '%s' already exists." % repo_path)

        subprocess.check_call(['git', 'init', '--bare',
            self.config.resolve_path(repo_path)])

        self.config.repos[repo_path] = {
            'users': []
        }

        self.config.save()

    def create_user(self, username, ssh_key):
        self.config.users[username] = ssh_key
        self.config.save()

    def add_users_to_repo(self, repo_path, users=[]):
        if self.user not in self.config.admins:
            raise SgitException(
                "User '%s' does not have correct permissions." % self.user)

        if repo_path not in self.config.repos:
            raise SgitException("Repo '%s' does not exist." % repo_path)

        repo = self.config.repos[repo_path]
        for user in users:
            if user not in self.config.users:
                raise SgitException("User '%s' does not exist." % user)

        for user in users:
            if user not in repo['users']:
                repo['users'].append(user)

        self.config.save()
