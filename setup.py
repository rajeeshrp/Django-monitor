from setuptools import setup, find_packages

setup(
    name = 'django-monitor',
    version = "0.2a",
    description = "Django app to moderate model objects",
    long_description = open("README.rst").read(),
    install_requires = [
        "django >= 1.1",
    ],
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
    author = "Rajeesh Nair",
    author_email = 'rajeeshrnair@gmail.com',
    url = 'http://bitbucket.org/rajeesh/django-monitor',
    license = 'BSD',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = True,
)

