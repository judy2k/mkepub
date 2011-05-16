
xhtmlns = 'http://www.w3.org/1999/xhtml'
xhtml = '{%s}' % xhtmlns

nsmap = {
    'xhtml': xhtmlns,
    'cont': 'urn:oasis:names:tc:opendocument:xmlns:container',
}

def replace_tag_with_contents(tag):
    parent = tag.getparent()
    if tag.getprevious() is not None and tag.text:
        if tag.getprevious().tail:
            tag.getprevious().tail += ' ' + tag.text
        else:
            tag.getprevious().tail = ' ' + tag.text
    elif tag.text:
        if parent.text:
            parent.text += ' ' + tag.text
        else:
            parent.text =  tag.text
    for child in tag:
        tag.addprevious(child)
    if tag.tail:
        if tag.getprevious() is not None:
            if tag.getprevious().tail:
                tag.getprevious().tail += ' ' + tag.tail
            else:
                tag.getprevious().tail = ' ' + tag.tail
        else:
            if parent.text is not None:
                parent.text += ' ' + tag.tail
            else:
                parent.text = tag.tail
    tag.getparent().remove(tag)


def reparent_contents(old_parent, new_parent):
    new_parent.append(old_parent)
    replace_tag_with_contents(old_parent)
 
def is_empty(tag):
    return len(tag) == 0 and (tag.text is None or tag.text.strip() == '')

def xpath_func(tree, nsmap=nsmap):
    def nsxpath(path):
        return tree.xpath(path, namespaces=nsmap)
    return nsxpath