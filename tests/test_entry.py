from registers.entry import Entry, Scope
from registers.hash import Hash


def test_json_repr():
    entry = Entry(
        "GB",
        Scope.User,
        "2016-04-05T13:23:05Z",
        Hash("sha-256", "6b18693874513ba13da54d61aafa7cad0c8f5573f3431d6f1c04b07ddb27d6bb"), # NOQA
        6
    )
    expected = '[{"index-entry-number":"6","entry-number":"6","entry-timestamp":"2016-04-05T13:23:05Z","key":"GB","item-hash":["sha-256:6b18693874513ba13da54d61aafa7cad0c8f5573f3431d6f1c04b07ddb27d6bb"]}]' # NOQA
    actual = entry.to_json()

    assert actual == expected
