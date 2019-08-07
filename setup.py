"""The setup.py file for Rhino Container Hack CLI."""

from setuptools import setup


LONG_DESCRIPTION = """
Rhino Container Hack CLI is a tool for testing security of container environments.
""".strip()

SHORT_DESCRIPTION = """
Rhino Container Hack CLI is a tool for testing security of container environments.""".strip()

DEPENDENCIES = [
    'boto3',
    'docker',
    'PyInquirer',
    'pyfiglet',
    'fire'
]

TEST_DEPENDENCIES = []

VERSION = '0.1.0'
URL = 'https://github.com/RhinoSecurityLabs/container-hack'

setup(
    name='container hack',
    version=VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,

    author='Rhino Assessment Team',
    author_email='pacu@rhinosecuritylabs.com',
    license='BSD 3-Clause',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Pentesters',
        'Topic :: Penetration Testing :: Tool :: Python Modules',

        'License :: OSI Approved :: BSD 3-Clause',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
    ],

    keywords='AWS ECS ECR EKS GCP AZURE kubernetes k8s docker container pentesting tool',

    packages=['modules'],

    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
)