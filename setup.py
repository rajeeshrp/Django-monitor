from setuptools import setup, find_packages
import os

version = '0.1.2'

setup(
    name = 'django-monitor',
    version = version,
    description = "Django app to moderate model objects",
    long_description = open("README.rst").read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    keywords = 'django moderation models',
    author = 'Rajeesh Nair',
    author_email = 'rajeeshrnair@gmail.com',
    url = 'http://bitbucket.org/rajeesh/django-monitor',
    license = 'BSD',
    packages = find_packages('monitor'),
    package_dir = {'': 'monitor'},
    include_package_data = True,
    install_requires=[
        'setuptools',
    ],
    zip_safe = True,
)

