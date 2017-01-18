import metadata_parser
try:
    from urllib.parse import urlparse
    # from urllib.parse import urlencode
except ImportError:
    from urlparse import urlparse
    # from urllib import urlencode

import unittest

if False:
    import logging
    l = logging.getLogger()
    l2 = logging.getLogger('metadata_parser')
    l.setLevel(logging.DEBUG)
    l2.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    l.addHandler(ch)
    l2.addHandler(ch)


URLS_VALID = [
    'http://example.com',
    'http://example.com/',
    'http://example.com/one',
    'http://example.com/one/two.html',
    'http://foo.example.com',
    'http://example.com:80',
    'http://example.com:80/',
    'http://example.com:80/one',
    'http://example.com:80/one/two.html',
    'http://192.168.1.1',
    'http://192.168.1.1/',
    'http://192.168.1.1:80',
    'http://192.168.1.1:8080',
    'http://192.168.1.1:80/',
    'http://192.168.1.1:8080/',
    'http://192.168.1.1:80/a.html',
    'http://192.168.1.1:8080/a.html',

    'https://example.com',
    'https://example.com/',
    'https://example.com/one',
    'https://example.com/one/two.html',
    'https://foo.example.com',
    'https://example.com:80',
    'https://example.com:80/',
    'https://example.com:80/one',
    'https://example.com:80/one/two.html',
    'https://192.168.1.1',
    'https://192.168.1.1/',
    'https://192.168.1.1:80',
    'https://192.168.1.1:8080',
    'https://192.168.1.1:80/',
    'https://192.168.1.1:8080/',
    'https://192.168.1.1:80/a.html',
    'https://192.168.1.1:8080/a.html',
]

URLS_VALID_CONDITIONAL = [
    'http://localhost',
    'http://localhost:80',
    'http://localhost:8000',
    'http://localhost/foo',
    'http://localhost:80/foo',
    'http://localhost:8000/foo',
    'https://localhost',
    'https://localhost:80',
    'https://localhost:8000',
    'https://localhost/foo',
    'https://localhost:80/foo',
    'https://localhost:8000/foo',

    'http://127.0.0.1',
    'http://127.0.0.1:80',
    'http://127.0.0.1:8000',
    'http://127.0.0.1/foo',
    'http://127.0.0.1:80/foo',
    'http://127.0.0.1:8000/foo',
    'https://127.0.0.1',
    'https://127.0.0.1:80',
    'https://127.0.0.1:8000',
    'https://127.0.0.1/foo',
    'https://127.0.0.1:80/foo',
    'https://127.0.0.1:8000/foo',

    'http://0.0.0.0',
    'http://0.0.0.0:80',
    'http://0.0.0.0:8000',
    'http://0.0.0.0/foo',
    'http://0.0.0.0:80/foo',
    'http://0.0.0.0:8000/foo',
    'https://0.0.0.0',
    'https://0.0.0.0:80',
    'https://0.0.0.0:8000',
    'https://0.0.0.0/foo',
    'https://0.0.0.0:80/foo',
    'https://0.0.0.0:8000/foo',
]

URLS_INVALID = [
    'http://example_com',
    'http://example_com/',
    'http://example_com/one',
    'http://999.999.999.999/',
    'http://999.999.999.999.999/',
    'http://999.999.999.999.999:8080:8080',

    'https://example_com',
    'https://example_com/',
    'https://example_com/one',
    'https://999.999.999.999/',
    'https://999.999.999.999.999/',
    'https://999.999.999.999.999:8080:8080',
]


class TestUrlParsing(unittest.TestCase):
    """
    python -m unittest tests.url_parsing.TestUrls

    Ensures URLs are parsed correctly as valid/invalid
    """
    def test_urls_valid(self):
        for i in URLS_VALID:
            parsed = urlparse(i)
            self.assertTrue(metadata_parser.is_parsed_valid_url(parsed))

    def test_urls_invalid(self):
        for i in URLS_INVALID:
            parsed = urlparse(i)
            self.assertFalse(metadata_parser.is_parsed_valid_url(parsed))

    def test_urls_valid_conditional(self):
        for i in URLS_VALID_CONDITIONAL:
            parsed = urlparse(i)
            self.assertFalse(metadata_parser.is_parsed_valid_url(parsed, require_public_netloc=True, allow_localhosts=False))
            self.assertTrue(metadata_parser.is_parsed_valid_url(parsed, require_public_netloc=False, allow_localhosts=True))


class TestAbsoluteUpgrades(unittest.TestCase):
    """
    python -m unittest tests.url_parsing.TestAbsoluteUpgrades

    Ensures URLs are parsed correctly as valid/invalid
    """

    def test_none_returns_none(self):
        absolute = metadata_parser.url_to_absolute_url(None, url_fallback=None)
        self.assertEquals(absolute, None)

    def test_nothing(self):
        absolute = metadata_parser.url_to_absolute_url('http://example.com', url_fallback='http://example.com')
        self.assertEquals(absolute, 'http://example.com')

    def test_upgrade(self):
        absolute = metadata_parser.url_to_absolute_url('a.html', url_fallback='http://example.com')
        self.assertEquals(absolute, 'http://example.com/a.html')

    def test_fallback(self):
        absolute = metadata_parser.url_to_absolute_url(None, url_fallback='http://example.com')
        self.assertEquals(absolute, 'http://example.com')


class _DocumentCanonicalsMixin(object):
    def _MakeOne(self, url):
        """generates a canonical document"""
        doc_base = """<html><head>%(head)s</head><body></body></html>"""
        canonical_base = """<link rel='canonical' href='%(canonical)s' />"""
        _canonical_html = canonical_base % {'canonical': url, }
        _doc_html = doc_base % {'head': _canonical_html, }
        return _doc_html


class TestDocumentCanonicals(unittest.TestCase, _DocumentCanonicalsMixin):
    """
    python -m unittest tests.url_parsing.TestDocumentCanonicals
    """

    def test_canonical_simple(self):
        """someone did their job"""
        url = None
        rel_canonical = 'https://example.com/canonical'
        rel_expected = 'https://example.com/canonical'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_canonical_upgrade(self):
        """someone else did their job. not as good, but did their job"""
        url = 'https://example.com'
        rel_canonical = '/canonical'
        rel_expected = 'https://example.com/canonical'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_upgrade_invalid_root(self):
        """
        you had one job...
        """
        url = 'https://example.com'
        rel_canonical = 'http://localhost:8080'
        rel_expected = 'https://example.com'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_upgrade_invalid_file(self):
        """
        you had one job...
        if someone lists the canonical as an invalid domain, remount the right domain

        python -m unittest tests.url_parsing.TestDocumentCanonicals.test_upgrade_invalid_file
        """
        url = 'https://example.com/a'
        rel_canonical = 'http://localhost:8080'
        rel_expected = 'https://example.com'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_upgrade_invalid_file_b(self):
        """
        you had one job...
        if someone lists the canonical as a different file on an invalid domain, remount the right domain
        """
        url = 'https://example.com/a'
        rel_canonical = 'http://localhost:8080/b'
        rel_expected = 'https://example.com/b'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_readme_scenario(self):
        """
        you had one job...
        if someone lists the canonical as an invalid domain, remount the right domain

        python -m unittest tests.url_parsing.TestDocumentCanonicals.test_readme_scenario
        """
        url = 'https://example.com/a'
        rel_canonical = 'http://localhost:8000/alt-path/to/foo'
        rel_expected = 'https://example.com/alt-path/to/foo'
        rel_expected_legacy = rel_canonical
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)

        # ensure we replace the bad domain with the right one
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

        # ensure support for the legacy behavior...
        parsed_url = parsed.get_discrete_url(require_public_global=False)
        self.assertEquals(parsed_url, rel_expected_legacy)


class TestDocumentCanonicalsRelative(unittest.TestCase, _DocumentCanonicalsMixin):
    """
    python -m unittest tests.url_parsing.TestDocumentCanonicalsRelative
    python -m unittest tests.url_parsing.TestDocumentCanonicalsRelative.test_upgrade_local_a
    python -m unittest tests.url_parsing.TestDocumentCanonicalsRelative.test_upgrade_local_b
    """

    def test_upgrade_local_a(self):
        """
        """
        url = 'https://example.com/nested/A.html'
        rel_canonical = '/nested/B.html'
        rel_expected = 'https://example.com/nested/B.html'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_upgrade_local_b(self):
        """
        """
        url = 'https://example.com/nested/A.html'
        rel_canonical = 'B.html'
        rel_expected = 'https://example.com/nested/B.html'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_upgrade_local_bb(self):
        """
        """
        url = 'https://example.com/nested/A.html'
        rel_canonical = 'path/to/B.html'
        rel_expected = 'https://example.com/nested/path/to/B.html'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)

    def test_upgrade_local_c(self):
        """
        """
        url = 'https://example.com/nested/A.html'
        rel_canonical = '/B.html'
        rel_expected = 'https://example.com/B.html'
        html_doc = self._MakeOne(rel_canonical)
        parsed = metadata_parser.MetadataParser(url=url, html=html_doc)
        parsed_url = parsed.get_discrete_url()
        self.assertEquals(parsed_url, rel_expected)
