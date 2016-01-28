from setuptools import setup

with open('README.rst') as f:
    desc = f.read()

setup(
    name = "sgit",
    version = "0.1.0",
    packages = ['sgit'],
    author = "Brendan Molloy",
    author_email = "brendan+pypi@bbqsrc.net",
    description = "Serve git repositories with ease",
    license = "BSD-2-Clause",
    keywords = ["git", "server"],
    url = "https://github.com/bbqsrc/sgit",
    long_description=desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ],
    entry_points = {
        'console_scripts': [
            'sgit = sgit.__main__:sgit',
            'sgit-shell = sgit.__main__:sgit_shell'
        ]
    }
)
