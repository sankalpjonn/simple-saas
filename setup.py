import os
from setuptools import find_packages, setup

setup(
    name='simple-saas',
    version='1.0.3',
    packages=find_packages(),
    include_package_data=True,
    description='A django app for boiler plate code of any generic saas tool',
    author='Sankalp Jonna',
    author_email='sankalp@50k.tech',
    install_requires=
        [
            'Django',
            'djangorestframework',
        ]
)
