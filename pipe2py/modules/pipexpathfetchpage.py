# pipexpathfetchpage.py
# vim: sw=4:ts=4:expandtab

import re

from urllib2 import urlopen
from html5lib import parse
from lxml import etree
from pipe2py import util
from pipe2py.lib.dotdict import DotDict


def pipe_xpathfetchpage(context=None, _INPUT=None, conf=None, **kwargs):
    """XPath Fetch Page module

    _INPUT -- not used since this does not have inputs.

    conf:
       URL -- url object contain the URL to download
       xpath -- xpath to extract
       html5 -- use html5 parser?
       useAsString -- emit items as string?

       Description: http://pipes.yahoo.com/pipes/docs?doc=sources#XPathFetchPage

       TODOS:
        - don't retrieve pages larger than 1.5MB
        - don't retrieve if page is not indexable.
    """
    conf = DotDict(conf)
    urls = util.listize(conf['URL'])

    for item in _INPUT:
        for item_url in urls:
            url = util.get_value(DotDict(item_url), DotDict(item), **kwargs)
            url = util.get_abspath(url)
            f = urlopen(url)

            # TODO: it seems that Yahoo! converts relative links to
            # absolute. This needs to be done on the content but seems to
            # be a non-trival task python?
            content = unicode(f.read(), 'utf-8')

            if context and context.verbose:
                print '............Content .................'
                print content
                print '...............EOF...................'

            xpath = conf.get('xpath', **kwargs)

            if 'html5' in conf:
                value = conf.get('html5', **kwargs)
                html5 = value == 'true'
            else:
                html5 = False

            if 'useAsString' in conf:
                value = conf.get('useAsString', **kwargs)
                use_as_string = value == 'true'
            else:
                use_as_string = False


            if html5:
                # from lxml.html import html5parser
                # root = html5parser.fromstring(content)
                root = parse(
                    content,
                    treebuilder='lxml',
                    namespaceHTMLElements=False
                )
            else:
                root = etree.HTML(content)

            res_items = root.xpath(xpath)

            if context and context.verbose:
                print 'XPathFetchPage: found count items:', len(res_items)

            for res_item in res_items:
                i = util.etree_to_pipes(res_item) #TODO xml_to_dict(res_item)

                if context and context.verbose:
                    print '--------------item data --------------------'
                    print i
                    print '--------------EOF item data ----------------'

                if use_as_string:
                    yield {'content' : unicode(i)}
                else:
                    yield i

        if item.get('forever'):
            # _INPUT is pipeforever and not a loop,
            # so we just yield our item once
            break