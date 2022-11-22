import json
import logging
import os
import weakref

import boto3 as boto3


LOGGER = logging.getLogger(__name__)


class AWSCredential:

    _instances = set()
    _session = None
    _config = None
    _region_name = None

    def __init__(self, key, region_name=os.getenv('AWS_REGION', 'us-east-1'), config=None):
        self.key = key

        if not AWSCredential._region_name:
            AWSCredential._region_name = region_name

        if not AWSCredential._config and config:
            AWSCredential._config = config

        if not AWSCredential._session:
            AWSCredential.create_session()

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
    def create_session(cls):
        cls._session = AWSSession(cls._region_name, cls._config)

    @classmethod
    def resolve_credentials(cls):
        for instance in cls._instances:
            cred = instance()
            if cred is not None:
                cred.resolve()

    @classmethod
    def set_region(cls, region_name):
        cls._region_name = region_name

        # Reinitialize AWS session in new region
        if cls._session:
            cls.create_session()

    @classmethod
    def set_config(cls, config):
        cls._config = config

        # Reinitialize AWS session in new region
        if cls._session:
            cls.create_session()


class AWSSession:
    def __init__(self, region_name, config=None):
        self.client = boto3.session.Session().client(
            service_name='secretsmanager',
            region_name=region_name,
            config=config
        )

    def get_secret(self, secret_name):
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_name
            )
        except Exception:
            LOGGER.error("Error resolving secret %s", secret_name)
            raise


        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            secret = json.loads(secret)
        else:
            secret = {
                'binary': get_secret_value_response['SecretBinary']
            }

        return secret

