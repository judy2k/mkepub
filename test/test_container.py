#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
from StringIO import StringIO
import unittest

import epub.format.container as ec

SAMPLE = """<?xml version="1.0"  encoding="UTF-8"?>
<container version="1.0"
        xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
        xmlns:py="http://genshi.edgewall.org/">
  <rootfiles>
    <rootfile full-path="/a/path" media-type="application/oebps-package+xml" />
  </rootfiles>
</container>"""

class ContainerTestCase(unittest.TestCase):
    def test_read(self):
        """container.xml parsing"""
        # From string:
        c = ec.Container.from_string(SAMPLE)
        rf = c.rootfiles
        self.assertEqual(1, len(rf))
        self.assertEqual(('/a/path', "application/oebps-package+xml"), rf[0])
        
        # From stream:
        s = StringIO(SAMPLE)
        c = ec.Container(s)
        rf = c.rootfiles
        self.assertEqual(1, len(rf))
        self.assertEqual(('/a/path', "application/oebps-package+xml"), rf[0])
        del s
        
        # From file:
        of, path = tf = tempfile.mkstemp()
        try:
            os.close(of)
            with open(path, 'w') as s:
                s.write(SAMPLE)
            with open(path) as s:
                c = ec.Container(s)
                rf = c.rootfiles
                self.assertEqual(1, len(rf))
                self.assertEqual(
                        ('/a/path', "application/oebps-package+xml"), rf[0])
        except:
            os.unlink(path)
            raise
    
    def test_output(self):
        c = ec.Container()
        c.add_rootfile('/contents.opf')
        print c.as_epub_container()