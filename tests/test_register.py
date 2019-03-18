import pytest
from registers import (rsf, Register, Attribute, Hash, Entry, Scope, Blob,
                       Record, Patch)
from registers.rsf import parse


@pytest.fixture
def country_rsf():
    with open('tests/fixtures/country.rsf', 'r') as handle:
        return handle.readlines()


@pytest.fixture
def country_register():
    commands = rsf.read('tests/fixtures/country.rsf')
    register = Register(commands)

    return register


def test_load_commands():
    commands = parse("""assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
add-item	{"register-name":"Country"}
append-entry	system	register-name	2018-09-10T10:11:10Z	sha-256:9f21f032105bb320d1f0c4f9c74a84a69e2d0a41932eb4543c331ce73e0bb1fb
""".splitlines()) # NOQA
    actual = Register(commands)

    assert actual.stats() == {
        "data": {"total-entries": 0, "total-blobs": 0},
        "metadata": {"total-entries": 1, "total-blobs": 1}
    }


def test_collect_country(country_register):
    assert country_register.stats() == {
        "data": {"total-entries": 209, "total-blobs": 209},
        "metadata": {"total-entries": 18, "total-blobs": 16}
    }


def test_empty_records():
    register = Register()
    records = register.records()
    actual = len(records)

    assert actual == 0


def test_country_records(country_register):
    records = country_register.records()
    actual = len(records)

    assert actual == 199


def test_country_schema(country_register):
    schema = country_register.schema()

    assert schema.primary_key == "country"
    assert len(schema.attributes) == 6
    assert isinstance(schema.attributes[0], Attribute)


def test_trail(country_register):
    key = "GB"
    expected = [Entry(
        key,
        Scope.User,
        "2016-04-05T13:23:05Z",
        Hash("sha-256", "6b18693874513ba13da54d61aafa7cad0c8f5573f3431d6f1c04b07ddb27d6bb"), # NOQA
        6
    )]

    actual = country_register.trail(key)

    assert actual == expected


def test_record(country_register):
    entry = Entry(
        "GB",
        Scope.User,
        "2016-04-05T13:23:05Z",
        Hash("sha-256", "6b18693874513ba13da54d61aafa7cad0c8f5573f3431d6f1c04b07ddb27d6bb"), # NOQA
        6
    )
    blob = Blob({
        "citizen-names": "Briton;British citizen",
        "country": "GB",
        "name": "United Kingdom",
        "official-name": "The United Kingdom of Great Britain and Northern Ireland" # NOQA
    })
    expected = Record(entry, blob)
    actual = country_register.record("GB")

    assert actual == expected


def test_patch_country(country_register):
    blobs = [
        Blob({
            "country": "AX",
            "name": "Atlantis",
            "end-date": "1000-01-01",
        })
    ]
    timestamp = "2019-03-21T07:21:00Z"
    patch = Patch(country_register.schema(), blobs, timestamp)
    country_register.apply(patch)
    records = len(country_register.records())

    assert records == 200
    assert country_register.stats() == {
        "data": {"total-entries": 210, "total-blobs": 210},
        "metadata": {"total-entries": 18, "total-blobs": 16}
    }
