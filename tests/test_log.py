import pytest
from registers.log import collect
from registers.rsf import parse


@pytest.fixture
def country_rsf():
    with open('tests/fixtures/country.rsf', 'r') as handle:
        return handle.readlines()


def test_collect():
    commands = parse("""assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
add-item	{"register-name":"Country"}
append-entry	system	register-name	2018-09-10T10:11:10Z	sha-256:9f21f032105bb320d1f0c4f9c74a84a69e2d0a41932eb4543c331ce73e0bb1fb
""".splitlines()) # NOQA
    actual = collect(commands)

    assert actual["data"].stats() == {"total-entries": 0, "total-blobs": 0}
    assert actual["metadata"].stats() == {"total-entries": 1, "total-blobs": 1}


def test_collect_country(country_rsf):
    actual = collect(parse(country_rsf), relaxed=True)

    assert actual["data"].stats() == {"total-entries": 209, "total-blobs": 209}
    assert actual["metadata"].stats() == {"total-entries": 18, "total-blobs": 16} # NOQA


def test_collect_duplicate():
    commands = """
add-item	{"citizen-names":"Briton;British citizen","country":"GB","name":"United Kingdom","official-name":"The United Kingdom of Great Britain and Northern Ireland"}
append-entry	user	GB	2019-04-03T00:00:00Z	sha-256:6b18693874513ba13da54d61aafa7cad0c8f5573f3431d6f1c04b07ddb27d6bb
add-item	{"citizen-names":"Briton;British citizen","country":"GB","name":"United Kingdom","official-name":"The United Kingdom of Great Britain and Northern Ireland"}
append-entry	user	GB	2019-04-03T00:00:00Z	sha-256:6b18693874513ba13da54d61aafa7cad0c8f5573f3431d6f1c04b07ddb27d6bb
""".strip().splitlines() # NOQA
    result = collect(parse(commands))
    actual = result["errors"]

    assert len(actual) == 1
