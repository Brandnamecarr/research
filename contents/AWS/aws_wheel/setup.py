from setuptools import setup, find_packages

setup(
    name='aws_utilities',
    version='0.0.1',
    description='Utilities for AWS',
    author='Brandon Carr',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console-scripts': [
            "test-command = commands.cli:test_command"
        ]
    }
)