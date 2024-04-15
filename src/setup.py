from setuptools import setup, find_packages

setup(
    name='adpatcher',
    version='3.0.0',
    packages=find_packages(),
    install_requires=['colorama==0.4.6'],
    entry_points = {
        'console_scripts': ['patcher = adpatcher.__main__:main']
    }
)