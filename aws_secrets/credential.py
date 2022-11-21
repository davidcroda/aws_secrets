import json
import os
import weakref

import boto3 as boto3


class AWSCredential:

    _instances = set()
    _session = None
    region_name = None

    def __init__(self, key, region_name=None):
        self.key = key
        self.region_name = region_name or os.getenv('AWS_REGION', 'eu-west-1')

        if not AWSCredential._session:
            AWSCredential._session = AWSSession(self.region_name)

        self.value = None

        self._instances.add(weakref.ref(self))

    def resolve(self):
        if not self.value:
            self.value = self._session.get_secret(self.key)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    @property
    def is_binary(self):
        self.resolve()
        return 'binary' in self.value

    def __getitem__(self, item):
        self.resolve()
        return self.value[item]

    def __str__(self):
        self.resolve()
        if not self.value:
            raise RuntimeError('The secret could not be resolved')
        return str(self.value)

    @classmethod
    def resolve_credentials(cls):
        for instance in cls._instances:
            cred = instance()
            if cred is not None:
                cred.resolve()

    @classmethod
    def set_region(cls, region_name):
        cls.region_name = region_name

        # Reinitialize AWS session in new region
        if cls._session:
            cls._session = AWSSession(cls.region_name)


class AWSSession:
    def __init__(self, region_name):
        self.client = boto3.session.Session().client(
            service_name='secretsmanager',
            region_name=region_name
        )

    def get_secret(self, secret_name):
        get_secret_value_response = self.client.get_secret_value(
            SecretId=secret_name
        )

        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            secret = json.loads(secret)
        else:
            secret = {
                'binary': get_secret_value_response['SecretBinary']
            }

        return secret

