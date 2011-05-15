# -*- coding: utf-8 -*-

"""
Provides TableOfContents, which can be used to generate or parse epub
NCX files.
"""

import jinja2
from lxml import etree

import epub.format

__all__ = ['TableOfContents', 'NavPoint']

NSMAP = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
NCX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xml:lang="en"
        xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
<!-- The following four metadata items are required for all NCX documents,
including those conforming to the relaxed constraints of OPS 2.0 -->

    <meta name="dtb:uid" content="{{unique_id|e}}"/> <!-- same as in .opf -->
    <meta name="dtb:depth" content="{{depth|e}}"/> <!-- 1 or higher -->
    <meta name="dtb:totalPageCount" content="0"/> <!-- must be 0 -->
    <meta name="dtb:maxPageNumber" content="0"/> <!-- must be 0 -->
  </head>

  <docTitle><text>{{docTitle|e}}</text></docTitle>
  {% for author in docAuthors -%}
  <docAuthor><text>{{author|e}}</text></docAuthor>
  {% endfor %}
  <navMap>
    {%- macro render_nav_point(np) -%}
    <navPoint {% if np.cls %}class="{{np.cls|e}}"{% endif %}
              id="{{np.point_id|e}}" playOrder="{{np.play_order|e}}">
      <navLabel><text>{{np.label|e}}</text></navLabel>
      <content src="{{np.link|e}}"/>
      {% for sp in np.nav_points %}
        {{ render_nav_point(sp) }}
      {%- endfor %}
    </navPoint>
    {%- endmacro -%}
    {% for nav_point in nav_points %}
    {{ render_nav_point(nav_point) }}
    {%- endfor %}
  </navMap>

</ncx>
"""

class TableOfContents(object):
    """An NCX file holds the table of contents for a publication."""
    
    tmpl = jinja2.Template(NCX_TEMPLATE)
    
    def __init__(self, unique_id, title, authors):
        """
        Create a TableOfContents with the provided properties.
        
        `unique_id` should be the same as that stored in the OPF file.
        """
        self.unique_id = unique_id
        self.title = title
        self.authors = ([authors] if isinstance(authors, basestring)
                else authors)
        self.nav_points = []
        self.npcount = 0

    @classmethod
    def from_file(cls, path_or_stream):
        """
        Parse an NCX file indicated by `path_or_stream`, which should be a
        path to a file, or should be a file-like object, and return a new
        TableOfContents for this data.
        """
        return cls.from_tree(etree.parse(path_or_stream))
    
    @classmethod
    def from_string(cls, xml_string):
        """
        Parse the provided NCX XML string, and return a new TableOfContents
        for this data.
        """
        return cls.from_tree(etree.fromstring(xml_string))
    
    @classmethod
    def from_tree(cls, root):
        """
        Create a new TableOfContents from the NCX data stored under the 
        lxml.etree document `root`.
        """
        def xpath(path, root=root):
            "Utility method for executing xpath with a useful namespace-map."
            return root.xpath(path, namespaces=NSMAP)
        
        unique_id = xpath(
                '/ncx:ncx/ncx:head/ncx:meta[@name="dtb:uid"]/@content'
                )[0].strip()
        title = xpath('/ncx:ncx/ncx:docTitle/ncx:text/text()')[0].strip()
        authors = [a.strip() for a in xpath(
                '/ncx:ncx/ncx:docAuthor/ncx:text/text()')]
        
        result = cls(unique_id, title, authors)
        
        def parse_nav_point(parent, node):
            """
            Internal method used to extract a NavPoint (and all contained
            NavPoints, recursively) from an XML node.
            """
            label = xpath('ncx:navLabel/ncx:text/text()', node)[0]
            link = xpath('ncx:content/@src', node)[0]
            point_id = xpath('@id', node)[0]
            clz = xpath('@class', node) or None
            npoint = NavPoint(label, link, point_id, clz)
            parent.nav_points.append(npoint)
            
            for sub_node in xpath('ncx:navPoint', node):
                parse_nav_point(npoint, sub_node)
            
        for node in xpath('/ncx:ncx/ncx:navMap/ncx:navPoint'):
            parse_nav_point(result, node)
        
        return result
    
    def depth(self):
        """
        Calculate the depth of this TableOfContents.
        """
        if self.nav_points:
            return max([np.depth() for np in self.nav_points])
        else:
            return 0
    
    def depth_first(self):
        """
        Iterate through the NavPoints in this object in a depth-first order.
        """
        for npoint in self.nav_points:
            for innerpoint in npoint.depth_first():
                yield innerpoint

    def _number_nav_points(self):
        """
        Used to number nav-points before writing out to NCX, which requires
        this value to be set correctly on all navPoints.
        """
        for index, npoint in enumerate(self.depth_first()):
            npoint.play_order = index + 1

    def to_ncx(self):
        """
        Return an XML string conforming to the Daisy NCX standard, suitable
        for embedding in an epub file.
        """
        self._number_nav_points()
        result = self.tmpl.render(
                docTitle=self.title,
                docAuthors=self.authors,
                nav_points=self.nav_points,
                unique_id=self.unique_id,
                depth=self.depth())
        
        return result


class NavPoint(object):
    """Represents a navPoint node in the NCX file's navMap section."""
    def __init__(self, label, link, point_id=None, cls=None):
        self.label = label
        self.link = link
        self.play_order = -1
        self.point_id = point_id or epub.format.random_id()
        self.cls = cls
        self.nav_points = []
    
    def depth_first(self):
        """
        Iterate through this NavPoint and all contained NavPoints in a
        depth-first order.
        """
        yield self
        for subpoint in self.nav_points:
            for innerpoint in subpoint.depth_first():
                yield innerpoint
    
    def depth(self):
        """
        Calculate the depth of this sub-tree of NavPoints.
        """
        if not self.nav_points:
            return 1
        else:
            return 1 + max([np.depth() for np in self.nav_points])
 