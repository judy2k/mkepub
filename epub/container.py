# -*- coding: utf-8 -*-

"""
Provides the `Container` class, which can be used to generate epub-compliant
container.xml files.
"""

import jinja2
from lxml import etree

__all__ = ['Container']

NSMAP = { 'c': 'urn:oasis:names:tc:opendocument:xmlns:container' }
CONTAINER_XML_TEMPLATE = """<?xml version="1.0"  encoding="UTF-8"?>
<container version="1.0"
           xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
  <rootfiles>
    {%- for rf_path, media_type in rootfiles %}
    <rootfile full-path="{{rf_path}}"
              media-type="{{media_type}}" />
    {%- endfor %}
  </rootfiles>
</container>"""


class Container(object):
    """Abstraction of the file stored at  META-INF/container.xml, which stores
    a link to the rootfile (usually an OPF file)."""
    
    container_ns = "{urn:oasis:names:tc:opendocument:xmlns:container}"
    tmpl = jinja2.Template(CONTAINER_XML_TEMPLATE)
   
    def __init__(self, path_or_stream=None):
        """
        Create a new Container. If path_or_stream is not none, the resource
        specified (either a path to a file, or a file-like object) is parsed to
        initialise the Container object.
        """
        self.rootfiles = []
        if path_or_stream:
            self.parse(path_or_stream)
            
    @classmethod
    def from_string(cls, xml_string):
        """
        Create a new Container, populated by parsing the XML contained
        in xml_string.
        """
        instance = cls()
        instance.parse_string(xml_string)
        return instance
        
    @classmethod
    def from_tree(cls, root):
        """
        Create a new Container, populated using an lxml.etree document.
        """
        instance = cls()
        instance.parse_tree(root)
        return instance
    
    def parse(self, path_or_stream):
        """
        Populate the Container using the XML contained in the resource
        specified by `path_or_stream` (either a path to a file, or a
        file-like object).
        """
        self.parse_tree(etree.parse(path_or_stream))
    
    def parse_string(self, xml_string):
        """
        Populate the Container by parsing the XML contained in `xml_string`.
        """
        self.parse_tree(etree.fromstring(xml_string))
        
    def parse_tree(self, root):
        """
        Populate the Container using an lxml.etree document.
        """
        for rfile in root.xpath('//c:container/c:rootfiles/c:rootfile',
                namespaces=NSMAP):
            self.rootfiles.append(
                    (rfile.attrib['full-path'], rfile.attrib['media-type']))
    
    def add_rootfile(self, rootfile,
            media_type="application/oebps-package+xml"):
        """Add the provided path to the rootfiles section of the container.xml
        file this object represents."""
        self.rootfiles.append((rootfile, media_type))
   
    def as_epub_container(self):
        """
        Return a string containing XML in the epub standard's container.xml
        format.
        """
        return self.tmpl.render(rootfiles=self.rootfiles)