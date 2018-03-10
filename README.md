# mrkd

Write man pages using Markdown, and convert them to Roff or HTML.

## Installation

```
$ pip install mrkd
```

## Usage

```
$ mrkd my-file.1.md my-file.1
```

Syntax is `mrkd [options...] input-file output-file`. The name and section number will
automatically be derived from the input file, though you can override them using
`-name my-name` and `-section my-section`, respectively.

Change the format to HTML using `-format html`:

```
$ mrkd my-file.1.md -format html my-file.1.html
```

You can override the HTML template (see `template.html` for an example) using `-template`.

In order to setup HTML links, you can set up an index file like so:

```ini
[Index]
my-page(1)=my-page.1.html
```

Then, when you do the following in your Markdown files:

```
something something (see my-page(1))
```

mrkd will automatically pick up the link and connect it via the index file. Pass it via
the `-index` argument:

```
$ mrkd -f html -index index.ini my-file.1.md my-file.1.html
```

See the `test` directory for an example.
