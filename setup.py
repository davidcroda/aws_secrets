from setuptools import setup

setup(
    name='aws_secrets',
    version='0.1.2',
    packages=['aws_secrets'],
    url='https://github.com/davidcroda/aws_secrets',
    license='MIT',
    author='David Roda',
    author_email='davidcroda@gmail.com',
    description='Python library for resolving secrets from AWS Secrets Manager',
    install_requires=[
        'boto3'
    ]
)
