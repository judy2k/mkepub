# -*- coding: utf-8 -*-

"""
A module for creating epub files (although designed so that it may deal with)
other formats in the future.

    epub.format.Epub :: A class for creating OCF-compliant epub files.
    epub.format.Container :: A simple encapsulation of an epub container.xml
        file, capable of parsing and generating said file format.
    epub.format.TableOfContents :: A class for encapsulating toc data, capable of
        parsing or generating NCX files.
    epub.format.Publication :: Encapsulates the manifest and reading-order
        of a single publication, and can parse and generate OPF files.
"""

import random
import zipfile
from epub.format.container import Container
from epub.format.toc import TableOfContents
from epub.format.publication import Publication

__all__ = ['Epub', 'Container', 'TableOfContents', 'Publication']

# The random id-generator picks characters from the following string:
ID_COMPONENTS = "abcdefghijklmnopqrstuvwxyz"

class Epub(object):
    """
    Creates and manages epub files. Currently only capable of writing OCF
    archives, not capable of reading them.
    
    Initialise with Epub('path-to-file'), and then use write(path), and
    writestr(path, bytes) to add content. Epub does not itself manage essential
    epub contents, such as container.xml and the necessary OPF files.
    
    Epub has been written as a context-manager, and is therefore compatible
    with the `with` statement introduced in Python 2.6.
    """
    
    def __init__(self, path):
        self.file = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        # path -> content
        self.contents = {}
        
        # If it's a new file, we add the necessary first file:
        mtzi = zipfile.ZipInfo('mimetype')
        mtzi.compress_type = zipfile.ZIP_STORED
        self.file.writestr(mtzi, 'application/epub+zip')
    
    def write(self, path, archive_path=None):
        """Write the real file at `path` into the archive at `archive_path`."""
        self.file.write(path, archive_path)
        
    def writestr(self, archive_path, fbytes):
        """Create a file in the archive with fbytes as content."""
        self.file.writestr(archive_path, fbytes)
    
    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        self.close()
        # Any exception will be re-raised:
        return False

    def close(self):
        """Close and finalise the open Epub file."""
        self.file.close()


def random_id(length=8, id_components=ID_COMPONENTS):
    """
    Generate a random ID string from the string provided as id_components.
    """
    return ''.join([random.choice(id_components) for _ in range(length)])