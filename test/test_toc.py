
import unittest



SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xml:lang="en"
        xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
<!-- The following four metadata items are required for all NCX documents,
including those conforming to the relaxed constraints of OPS 2.0 -->

    <meta name="dtb:uid" content="unique-id"/> <!-- same as in .opf -->
    <meta name="dtb:depth" content="3"/> <!-- 1 or higher -->
    <meta name="dtb:totalPageCount" content="0"/> <!-- must be 0 -->
    <meta name="dtb:maxPageNumber" content="0"/> <!-- must be 0 -->
  </head>

  <docTitle><text>document-title</text></docTitle>
  <docAuthor><text>A.N.Author</text></docAuthor>
  <docAuthor><text>
    U.LeWriteur
    </text></docAuthor>
  <navMap>
    <navPoint id="p" playOrder="1">
      <navLabel><text>Prologue</text></navLabel>
      <content src="prologue.html"/>
    </navPoint>

    <navPoint id="c1" playOrder="2">
      <navLabel><text>Chapter 1</text></navLabel>
      <content src="c1.html"/>
      <navPoint id="c1_1" playOrder="3">
        <navLabel><text>How Did I Get Here?</text></navLabel>
        <content src="c1.html#1"/>
        <navPoint id="c1_1_1" playOrder="4">
          <navLabel><text>How I Escaped</text></navLabel>
          <content src="c1.html#1_1"/>
        </navPoint>
      </navPoint>
    </navPoint>

    <navPoint id="c2" playOrder="5">
      <navLabel><text>Chapter 2</text></navLabel>
      <content src="c2.html"/>
    </navPoint>
  </navMap>
</ncx>"""

class TableOfContentsTestCase(unittest.TestCase):
    @staticmethod
    def _get_toc():
        from epub import toc
        return toc.TableOfContents
    
    @staticmethod
    def _get_navpoint():
        from epub import toc
        return toc.NavPoint
    
    def test_basic(self):
        """Basic TableOfContents model test"""
        toc = self._get_toc()('blblbl', 'Sample Contents', 'Sample Author')
        toc.nav_points.append(self._get_navpoint()('Prologue',
                'prologue.html'))
        np = self._get_navpoint()('Chapter 1', 'c1.html')
        toc.nav_points.append(np)
        np.nav_points.append(self._get_navpoint()('How I got here',
                'c1.html#how'))
        np = self._get_navpoint()('Chapter 2', 'c2.html')
        toc.nav_points.append(np)
        print toc.to_ncx()
        
    def test_parse(self):
        """Parse TableOfContents XML"""
        self.assertTrue(self._get_toc().from_string(SAMPLE).to_ncx())