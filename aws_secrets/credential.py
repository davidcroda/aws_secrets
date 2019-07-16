import json
import weakref
from json import JSONDecodeError

import boto3 as boto3


class AWSCredential:

    _instances = set()
    region_name = 'eu-west-1'

    def __init__(self, key):
        self.key = key
        self.client = AWSSession(self.region_name)

        self.value = None

        self._instances.add(weakref.ref(self))

    def __getitem__(self, item):
        self.resolve()
        return self.value[item]

    def resolve(self):
        if not self.value:
            self.value = self.client.get_secret(self.key)
            print(self.value)

    @classmethod
    def resolve_credentials(cls):
        for instance in cls._instances:
            instance().resolve()

    def __str__(self):
        self.resolve()
        if not self.value:
            raise RuntimeError('The secret could not be resolved')
        return str(self.value)


class AWSSession:

    instance = None

    def __new__(cls, *args, **kwargs):
        if not AWSSession.instance:
            AWSSession.instance = AWSSession.__AWSSession(*args, **kwargs)
        return AWSSession.instance

    class __AWSSession:
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
                try:
                    secret = json.loads(secret)
                except JSONDecodeError:
                    pass
            else:
                secret = get_secret_value_response['SecretBinary']

            return secret

