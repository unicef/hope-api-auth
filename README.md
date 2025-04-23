HOPE-API-AUTH
=============

+----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
| Menu                 | Link                                                                                                                                                      |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
| Coverage Development | [![codecov](https://codecov.io/gh/unicef/hope-api-auth/branch/develop/graph/badge.svg?token=sytM1cd8Zj)](https://codecov.io/gh/unicef/hope-api-auth)                                                                                                                                    |
| Coverage Stable      | [![codecov](https://codecov.io/gh/unicef/hope-api-auth/branch/master/graph/badge.svg?token=sytM1cd8Zj)](https://codecov.io/gh/unicef/hope-api-auth)                                                                                                                                    |
| Issue tracker        | https://github.com/unicef/hope-api-auth/issues                                                                                                          |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+

Installation
------------

    pip install hope-api-auth


Setup
-----

Add ``hope_api_auth`` to ``INSTALLED_APPS`` in settings

    INSTALLED_APPS = [
        'hope_api_auth',
    ]


Coding Standards
----------------

To run checks on the code to ensure code is in compliance

    $ ruff check
    $ ruff format


Testing
-------

Testing is important and tests are located in `tests/` directory and can be run with;

    $ uv run pytest test

Coverage report is viewable in `build/coverage` directory, and can be generated with;
