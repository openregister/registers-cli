from math import ceil
from hashlib import sha256
import pytest
from registers import rsf, merkle, Register, Entry, Scope


def expected_height(n):
    if n in [0, 1]:
        return 1

    return ceil((n / 2) + 1)


def test_empty():
    tree = merkle.Tree([])

    assert tree.root_hash == merkle.hash_empty(sha256)


def test_even_tree():
    tree = merkle.Tree([b"a", b"b", b"c", b"d"])

    assert tree.root_hash.hex() == ("33376a3bd63e9993708a84ddfe6c28ae"
                                    "58b83505dd1fed711bd924ec5a6239f0")


@pytest.mark.parametrize("test_input,expected",
                         [([], 1),
                          ([b"a"], 1),
                          ([b"a", b"b"], 2),
                          ([b"a", b"b", b"c"], 3),
                          ([b"a", b"b", b"c", b"d"], 3),
                          ([b"a", b"b", b"c", b"d", b"e"], 4)])
def test_tree_height(test_input, expected):
    tree = merkle.Tree(test_input)

    assert tree.height == expected_height(len(test_input))
    assert tree.height == expected


leaves = [bytes([]),
          bytes([0x00]),
          bytes([0x10]),
          bytes([0x20, 0x21]),
          bytes([0x30, 0x31]),
          bytes([0x40, 0x41, 0x42, 0x43]),
          bytes([0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57]),
          bytes([0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67,
                 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f])]


@pytest.mark.parametrize("test_input,height,expected",
                         [(leaves[0:1], 1, "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d"), # NOQA
                          (leaves[0:2], 2, "fac54203e7cc696cf0dfcb42c92a1d9dbaf70ad9e621f4bd8d98662f00e3c125"), # NOQA
                          (leaves[0:3], 3, "aeb6bcfe274b70a14fb067a5e5578264db0fa9b51af5e0ba159158f329e06e77"), # NOQA
                          (leaves[0:4], 3, "d37ee418976dd95753c1c73862b9398fa2a2cf9b4ff0fdfe8b30cd95209614b7"), # NOQA
                          (leaves[0:5], 4, "4e3bbb1f7b478dcfe71fb631631519a3bca12c9aefca1612bfce4c13a86264d4"), # NOQA
                          (leaves[0:6], 4, "76e67dadbcdf1e10e1b74ddc608abd2f98dfb16fbce75277b5232a127f2087ef"), # NOQA
                          (leaves[0:7], 4, "ddb89be403809e325750d3d263cd78929c2942b7942a34b77e122c9594a74c8c"), # NOQA
                          (leaves, 4, "5dc9da79a70659a9ad559cb701ded9a2ab9d823aad2f4960cfe370eff4604328")]) # NOQA
def test_root_hash(test_input, height, expected):
    tree = merkle.Tree(test_input)

    assert tree.root_hash.hex() == expected
    assert tree.height == height


def test_entry_root_hash():
    entry = Entry("SU", Scope.User, "2016-04-05T13:23:05Z",
                  "sha-256:e94c4a9ab00d951dadde848ee2c9fe51628b22ff2e0a88bff4cca6e4e6086d7a",  # NOQA
                  1)

    tree = merkle.Tree([entry.bytes()])
    expected = tree.root_hash.hex()

    assert expected == "a2002581c7402683e8197faafaefb9ba1f0ca48cee2d6ff461ab086b703472e5" # NOQA


@pytest.fixture
def country_register():
    commands = rsf.read('tests/fixtures/country.rsf')
    register = Register(commands)

    return register


def test_register_consistency(country_register):
    leaves = [entry.bytes() for entry
              in country_register.log.entries]

    tree = merkle.Tree(leaves)
    actual = tree.root_hash.hex()
    expected = ("3bacea769627d20ed9a2cfde54173da3"
                "c9d630b3fc9ed80431a1cee2196c8a4a")

    assert actual == expected
