sgit
====

Roll your own git hosting with minimal effort.

Features
--------

Supports multiple users, access control on a per-repo basis, remote
management of repositories all from the command line, and only requires
the creation of a single user on your server.

Access control is implemented as a key-value pair of usernames and SSH
public keys. Users in the ``admins`` list have extra permissions for
repository management.

Repositories can be created and users can be added remotely to the
server with a simple to use command line interface *(which has not yet
been implemented!)*

**This is not done enough to be usable for anyone yet. Be patient
please.**

License
-------

BSD 2-clause. See LICENSE.
