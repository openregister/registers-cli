# Web color example

This example shows the mechanics of applying patches to a register. The data
is the list of web colors as defined by the [W3C](https://www.w3c.org), in
particular [HTML4](https://www.w3.org/TR/1999/REC-html401-19991224/) and
[CSS Color Module Level 3](https://www.w3.org/TR/css-color-3/).


## Setup

Ensure that you have Python +3.6 installed on your machine.

Then, install the `registers` command line interface:

```sh
pip3 install --user "git+https://github.com/openregister/registers-cli#egg=registers"
```

Then verify it works:

```sh
$ registers --help
Usage: registers [OPTIONS] COMMAND [ARGS]...

  registers lets you manage a Register represented as a Register
  Serialisation Format (RSF).
```

### Troubleshooting

* **The 'registers' distribution was not found**: This is likely to be
  Pip configuration issue. Read more here:
  https://pip.pypa.io/en/stable/user_guide/#user-installs
* **There are conflicting dependencies**: Python manages dependencies
  centrally. Typically, if you need to isolate them, you would use some sort
  of virtualenv.


## Structure of the example

This example has:

* The **register** for the web colors in `src/web-color.rsf`.
* The **data** in TSV we will add to the register in `data/`.

Note that the filenames could be anything, the content is what's relevant.

Also note that any command from now on is assumed to be in the
`examples/web-color` directory part of the
[`registers-cli`](https://github.com/openregister/registers-cli) repository.


## The initial metadata

A register needs some metadata before you can add data into it. In particular:
the register identifier and the schema that any data needs to conform to.

Let's see the metadata available in the web color register:

```sh
registers context show src/web-color.rsf
```

And the schema:

```sh
registers schema show src/web-color.rsf
```

From this we know that any data we want to add must have the primary key
`web-color` (which happens to be the registers identifier as well) and can
have any of: `name`, `start-date`, `end-date`.


We can also check that in fact there is no data yet:

```sh
registers record list src/web-color.rsf
```


## The first patch

The first tsv, `data/01.tsv`, has the list of web colors defined in HTML4.

To be able to apply the patch to the register we need to transform the TSV
into an RSF patch:

```sh
registers patch create --rsf src/web-color.rsf data/01.tsv > patch_01.rsf
```

Now you can apply the patch to the register:

```sh
registers patch apply --rsf src/web-color.rsf patch_01.rsf
```

This last command _appends_ the content of the patch to the register so now
we have some records to list. So now let's get the records as CSV:

```sh
registers record list --format csv src/web-color.rsf
```


## The second patch

The second tsv, `patches/02.tsv`, has the list of web colors defined in CSS3.

This time, let's apply the patch at the same time as we create it:

```sh
registers patch create --apply --rsf src/web-color.rsf data/02.tsv
```

If we check the context again we'll see that there are 138 records in there:

```sh
registers context show src/web-color.rsf
```

We could also get the record for green yellow, identified by `ADFF2F`, its
hexadecimal code:

```sh
registers record show --format json --rsf src/web-color.rsf ADFF2F
```


## Publish the register

The [Registers Specification V1](https://spec.openregister.org/v1) describes
a REST API that any published register should comply with.

In this example we will use Netlify to host our data and to add a bit of route
handling to align with the reference implementation (ORJ) custom behaviour.

```sh
registers build --target netlify src/web-color.rsf
```

This command creates all the necessary files for a static deployment. Given
that the register identifier is `web-color` you should expect a
`build/web-color` directory.

Now we can log in our [Netlify](https://www.netlify.com/) account and drag and
drop the `web-color` folder in a new site.

Once the status is "PUBLISHED" you will have a working register API deployed.
