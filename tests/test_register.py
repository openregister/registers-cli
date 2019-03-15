import pytest
from registers.register import Register
from registers.rsf import parse


@pytest.fixture
def country_rsf():
    with open('tests/fixtures/country.rsf', 'r') as handle:
        return handle.readlines()


def test_load_commands():
    commands = parse("""assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
add-item	{"register-name":"Country"}
append-entry	system	register-name	2018-09-10T10:11:10Z	sha-256:9f21f032105bb320d1f0c4f9c74a84a69e2d0a41932eb4543c331ce73e0bb1fb
""".splitlines()) # NOQA
    actual = Register()
    actual.load_commands(commands)

    assert actual.stats() == {
        "data": {"total-entries": 0, "total-blobs": 0},
        "metadata": {"total-entries": 1, "total-blobs": 1}
    }


def test_collect_country(country_rsf):
    commands = parse(country_rsf)
    actual = Register()
    actual.load_commands(commands)

    assert actual.stats() == {
        "data": {"total-entries": 209, "total-blobs": 209},
        "metadata": {"total-entries": 18, "total-blobs": 16}
    }


def test_empty_records():
    register = Register()
    records = register.records()
    actual = len(records)

    assert actual == 0


def test_country_records(country_rsf):
    commands = parse(country_rsf)
    register = Register()
    register.load_commands(commands)
    records = register.records()
    actual = len(records)

    assert actual == 199


def test_country_schema(country_rsf):
    commands = parse(country_rsf)
    register = Register()
    register.load_commands(commands)
    schema = register.schema()

    assert schema.primary_key == "country"
    assert len(schema.attributes) == 6
