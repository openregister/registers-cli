# pylint: disable=missing-docstring
from click.testing import CliRunner
from registers import commands


def test_patch_create():
    register_filename = "tests/fixtures/further-education-college-uk.rsf"
    tsv_filename = "tests/fixtures/fec_patch.tsv"
    timestamp = "2019-03-31T00:00:00Z"
    expected = """
assert-root-hash	sha-256:f73ce68b4f90603b68ad41329699597134a5649a1bf577517e661d08eb8cfba7
add-item	{"further-education-college-uk":"109","name":"Herefordshire, Ludlow and North Shropshire College","region":"further-education-college-region-uk:1","start-date":"2018-11-01"}
append-entry	user	109	2019-03-31T00:00:00Z	sha-256:df74e0693d066cfdf5efa5d6bd3db54f41dc36144b25842d87df188719d29dc7
add-item	{"end-date":"2018-11-01","further-education-college-uk":"168","name":"North Shropshire College","region":"further-education-college-region-uk:1"}
append-entry	user	168	2019-03-31T00:00:00Z	sha-256:9e18661421bd83dadd8a17b28aed995f295352b75fb61f8b72ba0a08a3b0540f
add-item	{"end-date":"2018-11-20","further-education-college-uk":"2","name":"Accrington and Rossendale College","region":"further-education-college-region-uk:1"}
append-entry	user	2	2019-03-31T00:00:00Z	sha-256:158274b8160853556feb600b00bff5fa051d72085fb83792f8003e07c5f4b5f1
add-item	{"end-date":"2019-01-10","further-education-college-uk":"29","name":"Bracknell and Wokingham College","region":"further-education-college-region-uk:1"}
append-entry	user	29	2019-03-31T00:00:00Z	sha-256:3fc3b56631530e81bfe31a5c63ad0ffc605c0e5686bf4591919cabf0a4fe6918
add-item	{"further-education-college-uk":"254","name":"Wiltshire College and University Centre","region":"further-education-college-region-uk:1","start-date":"2019-07-19"}
append-entry	user	254	2019-03-31T00:00:00Z	sha-256:9631303cdfa452d5f382b2a3fbcd05dcef036c0f0ba7743127df2eeff5a61cf8
add-item	{"further-education-college-uk":"76","name":"EKC Group","region":"further-education-college-region-uk:1","start-date":"2018-08-01"}
append-entry	user	76	2019-03-31T00:00:00Z	sha-256:fe51e41743e91ead479cfe39d45c08fb4e65c6652030fcd508084651b19cfe38
add-item	{"further-education-college-uk":"205","name":"Solihull College & University Centre","region":"further-education-college-region-uk:1","start-date":"2018-10-01"}
append-entry	user	205	2019-03-31T00:00:00Z	sha-256:da2320979f5292ec646504f826e04fd7eb00ea068b40c513ef108cd2a1afe0f9
add-item	{"further-education-college-uk":"69","name":"DCG","region":"further-education-college-region-uk:1","start-date":"2018-11-12"}
append-entry	user	69	2019-03-31T00:00:00Z	sha-256:0c73c83d98cffe87e1ed5d0574145391ebecba7e57c2302f8dd0830fc1811a9a
add-item	{"further-education-college-uk":"196","name":"Unified Seevic Palmer's College (USP)","region":"further-education-college-region-uk:1","start-date":"2018-11-12"}
append-entry	user	196	2019-03-31T00:00:00Z	sha-256:9757e8330e7ce33ab55ec68d75e80e2b684a6f6b3c750e7bf703ff0edc10345a
add-item	{"further-education-college-uk":"313","name":"The Northern School of Art","region":"further-education-college-region-uk:1","start-date":"2018-09-01"}
append-entry	user	313	2019-03-31T00:00:00Z	sha-256:2b13d0314bcf1afd1c7fd760a3bfa4b620d28d6ad0a4b70f3c1ed9b0fcf09505
assert-root-hash	sha-256:470e653143735f8c71cd087058c9bff6aa136730627ba5ccc0b44b6bd024170a
""".lstrip()  # NOQA
    runner = CliRunner()
    result = runner.invoke(commands.patch.create_command,
                           ['--rsf', register_filename,
                            '--timestamp', timestamp,
                            tsv_filename])

    assert result.exit_code == 0
    assert result.output == expected


def test_patch_create_apply():
    orig_rsf = "tests/fixtures/further-education-college-uk.rsf"
    orig_tsv = "tests/fixtures/fec_patch.tsv"
    timestamp = "2019-03-31T00:00:00Z"
    runner = CliRunner()

    with open(orig_rsf, "r") as handler_rsf, open(orig_tsv, "r") as handler_tsv:  # NOQA
        register_filename = "fec.rsf"
        tsv_filename = "patch.rsf"
        expected = f"Appended 22 changes to {register_filename}\n"

        with runner.isolated_filesystem():
            with open(register_filename, 'w') as handler:
                handler.write(handler_rsf.read())

            with open(tsv_filename, 'w') as handler:
                handler.write(handler_tsv.read())

            result = runner.invoke(commands.patch.create_command,
                                   ['--rsf', register_filename,
                                    '--timestamp', timestamp,
                                    '--apply',
                                    tsv_filename])

            assert result.exit_code == 0
            assert result.output == expected
