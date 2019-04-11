from io import StringIO
from registers import Blob, Entry, Hash, Scope, Record
from registers.commands import utils


def test_record_json():
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
    expected = ('{"GB":{"index-entry-number":"6","entry-number":"6",'
                '"entry-timestamp":"2016-04-05T13:23:05Z","key":"GB",'
                '"item":[{"citizen-names":"Briton;British citizen",'
                '"country":"GB","name":"United Kingdom",'
                '"official-name":"The United Kingdom of Great Britain '
                'and Northern Ireland"}]}}')
    stream = StringIO()
    utils.serialise_json(record, stream, compact=True)
    stream.seek(0)
    actual = stream.read()

    assert actual == expected
