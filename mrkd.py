#!/usr/bin/env python

import configparser
import io
import jinja2
import mistune
import mistune_contrib.highlight
import os
import pkg_resources
import plac
import pygments.formatters
import pygments.styles
import re
import string
import sys


lines = lambda *a: '\n'.join(a)+'\n'


class ReferenceLexer(mistune.InlineLexer):
    def enable_reference(self):
        self.rules.reference = re.compile(r'^([A-Za-z-_.]+)\((\d+)\)')
        self.default_rules.insert(0, 'reference')
        self.rules.text = re.compile(
            r'^[\s\S]+?(?=[\\<!\[_*`~]|[A-Za-z-_.]+\(\d|https?://| {2,}\n|$)')

    def output_reference(self, m):
        return self.renderer.reference(m.group(1), m.group(2))


class RoffRenderer(mistune.Renderer):
    def __init__(self, name, sect, index):
        super(RoffRenderer, self).__init__()
        self.name = name
        self.sect = sect
        self.index = index

    def reference(self, text, section):
        return f'{self.double_emphasis(text)}({section})'

    # Block level.

    def block_code(self, code, lang):
        return lines(
            '.nf',
            self.block_quote(code.replace('\\', '\\\\')),
            '.fi',
        )

    def block_html(self, html):
        return '\n'

    def block_quote(self, text):
        return lines(
            '.RS',
            text,
            '.RE',
        )

    def header(self, text, level, raw=None):
        if level == 1:
            if '--' not in raw:
                sys.exit(f'Invalid header: {raw}')
            self.description = raw.split('--', 1)[1].strip()
            return lines(
                f'.TH "{self.name.upper()}" "{self.sect}" "" "" "{self.name}"',
                '.SH NAME',
                f'{text.replace("--", "-")}',
            )
        else:
            return lines(
                f'.SH {text}'
            )

    def hrule(self):
        return lines('.HL')

    def list(self, body, ordered=True):
        if ordered:
            count = 1
            buf = io.StringIO()

            assert body[0] == '\0'
            for chunk in body.split('\0')[1:]:
                buf.write(f'.IP {count}\\.')
                buf.write(chunk)
                count += 1

            return lines(
                '.RS',
                buf.getvalue(),
                '.RE'
            )
        else:
            return lines(
                '.RS',
                body.replace('\0', '.IP \\[bu]'),
                '.RE'
            )

    def list_item(self, text):
        return lines(
            '\0',
            text,
        )

    def paragraph(self, text):
        return lines('', text, '')

    # Inline level.

    def autolink(self, link, is_email=False):
        return self.link(link, None, None)

    def codespan(self, text):
        return self.double_emphasis(text)

    def double_emphasis(self, text):
        return f'\\fB{text}\\fR'

    def emphasis(self, text):
        return f'\\fI{text}\\fR'

    def linebreak(self):
        assert 0

    def link(self, link, title, content):
        if content is None:
            return f'{self.emphasis(link)}'
        elif title is None:
            return f'{self.double_emphasis(content)} ({self.emphasis(link)})'
        else:
            return f'{self.double_emphasis(content)} ({title}: {self.emphasis(link)})'

    def strikethrough(self, text):
        return self.text(text)

    def text(self, text):
        return text.replace('\\', '\\\\').replace('.', '\.')

    def inline_html(self, text):
        return ''


class HtmlRenderer(mistune.Renderer, mistune_contrib.highlight.HighlightMixin):
    def __init__(self, name, sect, index):
        super(HtmlRenderer, self).__init__()
        self.name = name
        self.sect = sect
        self.index = index

        self.options['inlinestyles'] = False

    def reference(self, text, section):
        result = f'{self.double_emphasis(text)}({section})'
        key = f'{text}({section})'
        if key in self.index:
            result = f'<a href="{self.index[key]}">{result}</a>'

        return result

    def block_code(self, code, lang):
        return mistune_contrib.highlight.HighlightMixin.block_code(self, code, lang)

    def header(self, text, level, raw=None):
        post = ''
        if level == 1:
            if '--' not in raw:
                sys.exit(f'Invalid header: {raw}')
            self.description = raw.split('--', 1)[1].strip()
            post, text = text.replace('--', '-'), 'NAME'
            level = 2

        chars = set(string.ascii_letters + string.digits + '_-.')
        ref = ''.join(c for c in raw.replace(' ', '-') if c in chars).lower()
        return lines(
            f'<h{level} id="{ref}">'
                f'<a class="hl" href="#{ref}">{text}</a>'
            f'</h{level}>',
            post,
        )


def entry_point(source: 'The source man page',
                output: 'The output file',
                name: ('The name to use for the man page', 'option'),
                section: ('The section to use for the man page', 'option'),
                template: ('The HTML template file to use', 'option'),
                index: ('An index file to use for HTML links', 'option'),
                format: ('The output format', 'option', None, str,
                         ['html', 'roff']) = 'roff'):
    m = re.match(r'(.*).(\d).[^.]+$', os.path.basename(source))
    if m is None:
        if name is None or section is None:
            sys.exit('Both -name and -section must be passed for invalid filenames.')
    else:
        if name is None:
            name = m.group(1)
        if section is None:
            section = m.group(2)

    if index is not None:
        index_config = configparser.ConfigParser()
        with open(index) as fp:
            index_config.read_file(fp)

        try:
            index_data = index_config['Index']
        except KeyError:
            sys.exit('Index file must contain an [Index] section.')
    else:
        index_data = {}

    renderers = {
        'roff': RoffRenderer,
        'html': HtmlRenderer,
    }
    renderer = renderers[format](name, section, index_data)

    inline = ReferenceLexer(renderer)
    inline.enable_reference()

    with open(source) as fp:
        result = mistune.markdown(fp.read(), inline=inline, renderer=renderer)

    if format == 'html':
        if template is None:
            template_data = pkg_resources.resource_string(__name__, 'template.html') \
                                         .decode('utf-8')
        else:
            with open(template) as fp:
                template_data = template.read()

        style = pygments.styles.get_style_by_name('friendly')
        fm = pygments.formatters.get_formatter_by_name('html', style=style)

        result = jinja2.Template(template_data).render(
            name=name,
            section=section,
            description=getattr(renderer, 'description', ''),
            content=result,
            pygments_css=fm.get_style_defs(),
        )

    if output == '-':
        print(result)
    else:
        with open(output, 'w') as fp:
            fp.write(result)


def main():
    plac.call(entry_point)


if __name__ == '__main__':
    main()
