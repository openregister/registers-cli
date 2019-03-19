from registers import Blob, Hash


def test_digest():
    """Should generate a digest following the canonical V1 rules."""

    blob = Blob({"register-name": "Country"})
    expected = Hash(
        "sha-256",
        "9f21f032105bb320d1f0c4f9c74a84a69e2d0a41932eb4543c331ce73e0bb1fb"
    )

    assert blob.digest() == expected


def test_utf8_digest():
    blob = Blob({
        "citizen-names": "Citizen of the Ivory Coast",
        "country": "CI",
        "name": "Ivory Coast",
        "official-name": "The Republic of Côte D’Ivoire"
    })
    expected = Hash(
        "sha-256",
        "b3ca21b3b3a795ab9cd1d10f3d447947328406984f8a461b43d9b74b58cccfe8"
    )

    assert blob.digest() == expected
