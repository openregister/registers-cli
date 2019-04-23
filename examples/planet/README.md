# Planet example

This example shows the mechanics of creating a register from scratch. The data
is the [list of planets as defined in the
Wikipedia](https://en.wikipedia.org/wiki/Planet).


## Setup

[Install the `registers` command line interface](../../README.md#Install).


## Structure of the example

This example has:

* The **data** in TSV and CSV we will add to the register in `data/`.

Note that the filenames could be anything, the content is what's relevant.

Also note that any command from now on is assumed to be in the
`examples/planet` directory part of the
[`registers-cli`](https://github.com/openregister/registers-cli) repository.


## Initialise the register

Let's create a new register:

```sh
registers init --rsf planet_register.rsf planet
```

The command above will prompt the question "Do you want to add an attribute?",
we want to say yes so we can add some attributes to the schema.

For the first attribute, we want it to have an id `name`, a datatype `string`,
a cardinality `1` and a description "The name of the planet". This means the
records in the register will be able to have a field "name" expecting a single
string as a value.

Note that all attributes in a Register are optional with the exception of the
primary key.

We will add two more attributes, `start-date` and `end-date` both of type
`datetime` and cardinality `1`. The descriptions should on the lines of "The
date the astronomical body was accepted as a planet." and "The date the
astronomical body was rejected as a planet.".

After saying "N" to the last "Do you want to add an attribute?" question we
will get a file `planet.rsf` in the current directory. If we check the
content it should look similar to this:

```
assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
add-item	{"name":"planet"}
append-entry	system	name	2019-04-09T13:24:11Z	sha-256:d320f5ff3b0fa489974d0d7f0d647bf50c953de6f16ba53a019c81612b621bcf
add-item	{"cardinality":"1","datatype":"string","field":"planet"}
append-entry	system	field:planet	2019-04-09T13:24:11Z	sha-256:3e75fcecb3ecebb2cf3484df1abe182dd27b6ada92b2a24b729e1de334bfbebc
add-item	{"cardinality":"1","datatype":"string","field":"name","text":"The name of the planet"}
append-entry	system	field:name	2019-04-09T13:24:11Z	sha-256:7517836d09e09b78d117325aeb201114c961f63940d191556f488f6968a41b73
add-item	{"cardinality":"1","datatype":"datetime","field":"start-date","text":"The date the astronomical body was accepted as a planet."}
append-entry	system	field:start-date	2019-04-09T13:24:11Z	sha-256:63c65b67a4892135f7b39aaec51d2ee56c54807ac5eb86272ceb6979803cd0b4
add-item	{"cardinality":"1","datatype":"datetime","field":"end-date","text":"The date the astronomical body was rejected as a planet."}
append-entry	system	field:end-date	2019-04-09T13:24:11Z	sha-256:ec83a5b919ce554b331fb2f1197d310bee52857457968faa5be600a5e5be6e69
```


Let's see the register metadata in a more readable form:

```sh
registers context show planet.rsf
```

And the schema:

```sh
registers schema show planet.rsf
```

From this we know that any data we want to add must have the primary key
`planet` and can have any of: `name`, `start-date`, `end-date`.


We can also check that in fact there is no data yet:

```sh
registers record list planet.rsf
```


## Add some data

The following section is similar to the [web color example](../web-color).
Check it out if you want to know more about patches of data.

Let's add the planet list from the 19th century onwards:

```sh
registers patch create --apply --rsf planet.rsf data/1807.tsv
registers patch create --apply --rsf planet.rsf data/1854.tsv
registers patch create --apply --rsf planet.rsf data/1930.csv
registers patch create --apply --rsf planet.rsf data/2006.csv
```

The list of records contains all 13 bodies that have been considered planets
at some point:

```sh
registers record list --format csv planet.rsf
```

To conclude, we can see that although there are 13 records, the register
contains 19 entries that keep the history of changes.
