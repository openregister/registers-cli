from registers.blob import Blob
from registers.entry import Entry, Scope
from registers.hash import Hash
from registers.record import Record


def test_json_repr():
    entry = Entry(
        "GB",
        Scope.User,
        "2016-04-05T13:23:05Z",
        Hash("sha-256", "6b18693874513ba13da54d61aafa7cad0c8f5573f3431d6f1c04b07ddb27d6bb"), # NOQA
        6
    )
    blob = Blob({
        "country": "GB",
        "official-name": "The United Kingdom of Great Britain and Northern Ireland", # NOQA
        "name": "United Kingdom",
        "citizen-names": "Briton;British citizen"
    })
    record = Record(entry, blob)
    expected = '{"GB":{"index-entry-number":"6","entry-number":"6","entry-timestamp":"2016-04-05T13:23:05Z","key":"GB","item":[{"citizen-names":"Briton;British citizen","country":"GB","name":"United Kingdom","official-name":"The United Kingdom of Great Britain and Northern Ireland"}]}}' # NOQA
    actual = record.to_json()
    print(actual)

    assert actual == expected
