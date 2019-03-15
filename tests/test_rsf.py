from registers import rsf


def test_serde():
    with open('tests/fixtures/country.rsf', 'r') as file:
        expected = file.read()
        commands = rsf.read('tests/fixtures/country.rsf')
        actual = rsf.dump(commands)

        assert actual == expected
