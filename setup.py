from setuptools import setup, find_packages

setup(
    name='xdoc',
    version='0.4.1',
    author='Christopher Brown',
    author_email='io@henrian.com',
    url='http://henrian.com',
    keywords='',
    description='',
    long_description='',
    classifiers=[],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'lxml'
    ],
    entry_points={
        'console_scripts': [
            'xdoc = xdoc.cli:main',
        ],
    },
)
