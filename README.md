## Registers CLI

The Registers CLI lets you manage your registers expressed as Register
Serialisation Format (RSF).


## Install

Ensure that you have Python +3.6 installed on your machine.

```sh
pip3 install --user "git+https://github.com/openregister/registers-cli#egg=registers"
```

### Troubleshooting

* **Pip is not up to date**: Ensure you have pip up to date:
  `pip3 install -U pip`.
* **The 'registers' distribution was not found**: This is likely to be
  Pip configuration issue. Read more here:
  https://pip.pypa.io/en/stable/user_guide/#user-installs
* **There are conflicting dependencies**: Python manages dependencies
  centrally. Typically, if you need to isolate them, you would use some sort
  of virtualenv.


## Getting started

Check out the [`examples/`](./examples) directory.


## Development

### Dependencies

* Python 3.7.
* [Pipenv](https://pipenv.readthedocs.io/en/latest/).


Install the development dependencies:

```sh
pipenv install --dev
```

Ensure everything works:

```sh
make check lint test
```

To try the CLI without installing it you can use the `reg` wrapper. For
example, to get the schema for the country register:

```sh
pipenv run ./reg schema show tests/fixtures/country.rsf
```

If you need to get more RSF files you can get them from
`https://github.com/openregister/registry-data`.


## Licence

Unless stated otherwise, the codebase is released under [the MIT licence](./LICENSE).

The data is [© Crown
copyright](http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/copyright-and-re-use/crown-copyright/)
and available under the terms of the [Open Government
3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
licence.
