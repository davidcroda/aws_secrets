AWS Secrets
-----------

This library allows you to use credentials stored in AWS Secrets Manager within
your code. It will lazily resolve secret values when they are evaluated, or resolve
all secrets when AWSCredential.resolve_secrets() is called.

Usage
=====

.. code-block:: python

    from aws_secrets import AWSCredential
    db = AWSCredential('path/to/key')

    # credential is resolved here
    print(db['username'])

    secret_one = AWSCredential('path/to/key_one')
    secret_two = AWSCredential('path/to/key_one')

    # both credentials are resolved here
    AWSCredential.resolve_secrets()
    print(secret_one)
    print(secret_two)
