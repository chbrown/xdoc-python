from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))

setup(
    name='docxtex',
    version='0.3.0',
    author='Christopher Brown',
    author_email='io@henrian.com',
    url='http://henrian.com',
    keywords='',
    description='',
    long_description='',
    classifiers=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'docx2tex = docxtex:main',
        ],
    },
)
