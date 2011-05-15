import unittest

SAMPLE_OPF = """<?xml version="1.0"?>
<opf:package version="2.0"
        xmlns:opf="http://www.idpf.org/2007/opf"
        unique-identifier="bookid">
    <opf:metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>My Wookie Book</dc:title>
        <dc:creator opf:file-as="Smith, Mark"
            opf:role="aut">Mark Smith</dc:creator>
        <dc:identifier id="bookid">urn:uuid:unique-id</dc:identifier>
        <dc:language>en-GB</dc:language>
    </opf:metadata>
    <opf:manifest>
        <opf:item id="page_1"
            href="index.html"
            media-type="application/xhtml+xml" />
        <opf:item id="cover"
            href="cover.jpg"
            media-type="image/jpeg" />
    </opf:manifest>
    <opf:spine toc="ncx">
        <opf:itemref idref="page_1" />
    </opf:spine>
</opf:package>"""

class PublicationTestCase(unittest.TestCase):
    def _get_pub_class(self):
        import epub.publication
        return epub.publication.Publication
    
    def _get_pub_instance(self, *args, **kwargs):
        return self._get_pub_class()(*args, **kwargs)
    
    def test_opf(self):
        """Basic Publication serialisation test."""
        p = self._get_pub_instance('unique-id', 'The Sedan Chair',
                'Mark Smith', 'Smith, Mark')
        p.lang = 'en-GB'
        p.add_item('index.html')
        p.add_item('cover.jpg')
        print p.as_opf()
    
    def test_mime_exception(self):
        """
        Exception raised when an spine-item is added with the wrong mime-type
        """
        p = self._get_pub_instance('unique-id', 'The Sedan Chair',
                'Mark Smith', 'Smith, Mark')

        self.assertRaises(RuntimeError, p.add_item,
                'cover.jpg', spine_item=True)
    
    def test_parsing(self):
        """Can parse Publication from string"""
        p = self._get_pub_class().from_string(SAMPLE_OPF)
        print p.as_opf()