# -*- coding: utf-8 -*-

"""
Methods to overload pretty print and whitespace management from xml minidom.

It is due to a bug in xml.dom.minidom, and thus, the presented solution is a
hack. It should be reverted to normal behavior when minidom will be updated.
"""

__author__ = 'marco'

import xml.dom.minidom


def remove_whitespace_nodes(node, unlink=False):
    """Removes all of the whitespace-only text decendants of a DOM node.

    When creating a DOM from an XML source, XML parsers are required to
    consider several conditions when deciding whether to include
    whitespace-only text nodes. This function ignores all of those
    conditions and removes all whitespace-only text descendants of the
    specified node. If the unlink flag is specified, the removed text
    nodes are unlinked so that their storage can be reclaimed. If the
    specified node is a whitespace-only text node then it is left
    unmodified.

    """
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == 3 and not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whitespace_nodes(child, unlink)

    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()


def _fixed_writexml(self, writer, indent='', addindent='', newl=''):
    """Hackish way to have a real pretty print.

    See http://goo.gl/GrHqL

    Very hackish. May break after further update of minidom

    param:
        indent = current indentation
        addindent = indentation to add to higher levels
        newl = newline string

    """
    writer.write(indent + '<' + self.tagName)

    attrs = self._get_attributes()  # IGNORE:W0212
    a_names = attrs.keys()
    a_names.sort()

    for a_name in a_names:
        writer.write(' %s=\'' % a_name)

        xml.dom.minidom._write_data(writer, attrs[a_name].value)  # IGNORE:W0212
        writer.write('\'')
    if self.childNodes:
        if len(self.childNodes) == 1 \
          and self.childNodes[0].nodeType == xml.dom.minidom.Node.TEXT_NODE:
            writer.write('>')
            self.childNodes[0].writexml(writer, '', '', '')
            writer.write('</%s>%s' % (self.tagName, newl))
            return
        writer.write('>%s' % (newl))
        for node in self.childNodes:
            node.writexml(writer, indent + addindent, addindent, newl)
        writer.write('%s</%s>%s' % (indent, self.tagName, newl))
    else:
        writer.write('/>%s' % (newl))

# replace minidom's function with ours
xml.dom.minidom.Element.writexml = _fixed_writexml


def write_to_file(doc, name, mode='a'):
    """Write a pretty print version of doc in a file."""
    doc.toprettyxml()
    doc.writexml(open(name, mode), indent='', addindent='    ', newl='\n')