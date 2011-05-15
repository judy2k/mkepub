# -*- coding: utf-8 -*-

# TODO: spine_item should not be contained in ManifestItem

"""
Provides the Publication class, which can be used to parse or generate
epub-compliant OPF files.
"""

import jinja2
from lxml import etree

import epub.format

__all__ = ['Publication']

NSMAP = {
    'opf':'http://www.idpf.org/2007/opf',
    'dc':'http://purl.org/dc/elements/1.1/',

}

OPF_TEMPLATE = """<?xml version="1.0"?>
<opf:package version="2.0" xmlns:opf="http://www.idpf.org/2007/opf"
        unique-identifier="bookid">
    <opf:metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{{pub.title}}</dc:title>
        {%- for author,fileas in pub.authors %}
        <dc:creator opf:file-as="{{fileas}}" opf:role="aut">{{author}}</dc:creator>
        {%- endfor %}
        <dc:identifier id="bookid">urn:uuid:{{pub.unique_id}}</dc:identifier>
        <dc:language>{{pub.lang}}</dc:language>
    </opf:metadata>
    <opf:manifest>
        {%- for item in pub.items %}
        <opf:item id="{{item.item_id}}"
            href="{{item.href}}"
            media-type="{{item.media_type}}" />
        {%- endfor %}
    </opf:manifest>
    <opf:spine toc="ncx">
        {%- for spine_item in pub.spine_items %}
        <opf:itemref idref="{{spine_item.item_id}}" />
        {%- endfor %}
    </opf:spine>
</opf:package>"""


# Lookup for file-extension -> mime-type:
MIME_MAP = {
    'html': 'application/xhtml+xml',
    'xhtml': 'application/xhtml+xml',
    'css': 'text/css',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'svg': 'image/svg',
    'ncx': 'application/x-dtbncx+xml',
    'txt': 'text/plain',
    'pdf': 'application/pdf',
}


class Publication(object):
    """Encapsulates an OPF file, which describes the files that make up
    an e-book.
    
    All documents that make up a publication must be included in the OPF file's
    manifest, including images, css, etc.  The spine contains references to the
    'content' documents in the order that they should be displayed linearly."""
    
    tmpl = jinja2.Template(OPF_TEMPLATE)
    lang = 'en-US'
   
    def __init__(self, unique_id, title, author, fileas):
        """
        Create a Publication with the provided characteristics.
        """
        self.unique_id = unique_id
        self.title = title
        self.authors = [(author, fileas)]
        self.items = []
        self.spine_items = []
    
    @property
    def item_ids(self):
        """List of all item ids in the OPF file."""
        return [item.item_id for item in self.items] 
   
    def generate_id(self):
        """
        Returns a randomly-generated id-string, suitable for use as a
        unique-id for a manifest item.
        """
        item_id = epub.format.random_id()
        # Just ensure id is unique - may save problems in rare occasions:
        while item_id in self.item_ids:
            item_id = epub.random_id()
        return item_id
   
    def get_item(self, item_id):
        """
        Return the ManifestItem used internally to store manifest data for the
        item with the provided `item_id`
        """
        return [i for i in self.items if i.item_id == item_id][0]
   
    def add_item(self, href, item_id=None, spine_item=None, media_type=None):
        """Adds an item to the OPF document's manifest.
        
        href should be the path to the item relative to the location of the OPF
        file. If no item_id is provided, one will be automatically generated.
        If the item has a 'content' media-type, such as XML, it will be added
        to the spine section automatically, unless spine_item is set to False.
        If media_type is not provided, it will attempt to lookup a suitable
        value based on the item's file extension."""
        
        item = ManifestItem(href, item_id, spine_item, media_type)
        
        item.ensure_valid(self.generate_id)
        if item.item_id in self.item_ids:
            raise RuntimeError(
                    "Item with id '%s' is already in OPF file." % item_id)
        
        self.items.append(item)

        if item.spine_item:
            self.spine_items.append(item)
        
        return item.item_id

    def append_to_spine(self, item_id):
        """Append the item with the provided `item_id` to the spine."""
        item = self.get_item(item_id)
        item.spine_item = True
        self.spine_items.append(item)

    @classmethod
    def from_string(cls, xml_string):
        """
        Create a new Publication parsed from the provided `xml_string`.
        """
        return cls.from_root(etree.fromstring(xml_string))
    
    @classmethod
    def from_root(cls, root):
        """
        Create a new Publication parsed from the provided lxml.etree document.
        """
        def xpa(path, top=root):
            "Utility function to run xpath with a useful namespace-map."
            return top.xpath(path, namespaces=NSMAP)
        
        meta = xpa('/opf:package/opf:metadata')[0]
        
        title = xpa('dc:title/text()', meta)[0]
        unique_id = xpa('dc:identifier/text()', meta)[0]
        author = xpa('dc:creator[@opf:role="aut"]/text()', meta)[0]
        fileas = xpa('dc:creator[@opf:role="aut"]/@opf:file-as', meta)[0]

        result = cls(unique_id, title, author, fileas)
        result.lang = xpa('dc:language/text()', meta)[0]
        
        for item in xpa('/opf:package/opf:manifest/opf:item'):
            item_id = xpa('@id', item)[0]
            href = xpa('@href', item)[0]
            media_type = xpa('@media-type', item)[0]
            result.add_item(href, item_id, False, media_type)
        
        for spine_id in xpa('/opf:package/opf:spine/opf:itemref/@idref'):
            result.append_to_spine(spine_id)
        
        return result
    
    def as_opf(self):
        """
        Return an XML string, in the epub OPF format.
        """
        result = self.tmpl.render(pub=self)
        return result


class ManifestItem(object):
    """
    Internal object used to validate and store information related to a single
    manifest item.
    """
    def __init__(self, href, item_id=None, spine_item=None, media_type=None):
        """
        Create a ManifestItem with the specified properties. Sensible defaults
        are generated for each of the optional parameters based on other
        properties of the object.
        
        If an attempt is made to create an invalid ManifestItem, such as a
        spine-item with an unsupported media-type, a RuntimeError will be
        raised.
        """
        self.href = href
        self.item_id = item_id
        
        self.media_type = media_type
        
        if media_type is None and '.' in href:
            ext = href[href.rfind('.')+1:]
            media_type = MIME_MAP.get(ext, None)
        if media_type is None:
            raise RuntimeError("Do not know media-type for file %s" % href)
        self.media_type = media_type
        
        if spine_item is None and is_spine_mime(media_type):
            # NCX files shouldn't be added to the spine:
            spine_item = True
        elif spine_item and not is_spine_mime(media_type):
            raise RuntimeError("Cannot create a ManifestItem with "
                    "media-type=%r and spine=True" % media_type)
        
        self.spine_item = spine_item

    def ensure_valid(self, id_provider):
        """
        Uses the specified `id_provider`, which should be a function that
        takes no parameters and returns a suitable unique ID, to set the
        item_id for this ManifestItem.
        """
        if not self.item_id:
            self.item_id = id_provider()


def is_spine_mime(media_type):
    """Returns true if the provided mime-type is considered a 'content'
    type, such as HTML.  The result is not expected to be definitive,
    it's just a useful check to allow sensible behaviour in common cases.
    """
    return media_type in ['application/x-dtbook+xml',
            'application/xhtml+xml', 'text/x-oeb1-document']