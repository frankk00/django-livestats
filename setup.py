from setuptools import setup, find_packages
import os

CLASSIFIERS = []

setup(
    author="Kristian Oellegaard",
    author_email="kristian@oellegaard.com",
    name='django-livestats',
    version='0.0.2',
    description='A django livestats framework',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.2',
    ],
    packages=find_packages(exclude=["project", "project.*"]),
    include_package_data=True,
    zip_safe = False,
)
