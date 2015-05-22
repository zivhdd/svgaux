from xml.etree import ElementTree 
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import os

## patch for CDATA support

def CDATA(text=None):
    element = ElementTree.Element('![CDATA[')
    element.text = text
    element.tail = ""
    return element

ElementTree._original_serialize_xml = getattr(ElementTree, "_original_serialize_xml", None) or  ElementTree._serialize_xml

def _serialize_xml(write, elem, encoding, qnames, namespaces):
    if elem.tag == '![CDATA[':
        write("<%s%s]]>%s" % (elem.tag, elem.text, elem.tail))
        return
    return ElementTree._original_serialize_xml(
         write, elem, encoding, qnames, namespaces)
ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml



def astext(obj, formatter=str):    
    method = getattr(obj, "astext", None)
    if (method):
        return method(formatter)
    return formatter(obj)
    

class TextItems(object):
    def __init__(self, *args):
        self.items = args

    def astext(self, formatter):
        return "".join([astext(x, formatter) for x in self.items])

    def __str__(self):
        return self.astext(str)

class SEnum(object):
    def __init__(self, *args):
        self.__dict__.update(dict(zip(args, args)))
        
class TransformCls(object):
    def __getattribute__(self, name):
        if (name.startswith("_")):
            return object.__getattribute__(self, name)

        return lambda *args: TextItems(*([name, "("] + self._join(args) + [")"]))

    def _join(self, lst):
        res = []
        for item in lst:
            res += [item, " "]
        return res[:-1]

(lambda *args: "%s(%s)" % (name, " ".join(map(str, args))))

TAGS = SEnum("rect", "circle", "path", "g", "polygon")
Transform = TransformCls()

    
class Shape(object):

    KEYWORDS = set(["class"])
    def __init__(self, tag, **kargs):
        self.tag = tag
        self.attributes = {}
        self.cls = None
        self.transform = None
        self.update(**kargs)
    
    def update(self, cls=None, transform=None, **kargs):
        self.attributes.update(kargs)
        if (cls):
            self.cls = cls
        if (transform):
            self.transform = transform

    def asElement(self, formatter=str):
        elm = Element(self.tag)        
        elm.attrib.update(dict(map(lambda x: (x[0], astext(x[1], formatter)), self.attributes.items())))
        if (self.cls):
            elm.attrib["class"] = self.cls
        if (self.transform):
            transform = (self.transform if (type(self.transform) == list) 
                         else [self.transform])
            
            elm.attrib["transform"] = " ".join([astext(x, formatter) for x in transform])
        return elm
    

class Group(Shape):
    def __init__(self, tag, items=[], **kargs):
        Shape.__init__(self, tag, **kargs)
        self.items = [] + items

    def groupTag(self):
        return "g"

    def asElement(self, formatter=str):
        elm = Shape.asElement(self, formatter=formatter)
        for x in self.inner(formatter=formatter):
            elm.append(x)
        return elm

    def inner(self, formatter):
        return [x.asElement(formatter) for x in self.items]

    def append(self, obj):
        self.items.append(obj)

class Rule(object):
    def __init__(self, selector, **declerations):
        self.selector = selector
        self.declerations = declerations
        
    
class SVG(Group):
    def __init__(self, css_rules=None, **kargs):
        attributes = { "xmlns" : "http://www.w3.org/2000/svg", 
                       "xmlns:xlink" : "http://www.w3.org/1999/xlink" }
        attributes.update(**kargs)    
        Group.__init__(self, tag="svg", **attributes)
        self.css_rules = css_rules

    def inner(self, formatter):
        res = Group.inner(self, formatter)
        if (self.css_rules):
            css_elm = Element("style")
            css_elm.attrib["type"] = "text/css"
            
            css_text = "\n"
            for rule in self.css_rules:
                css_text += "\t%s {\n" % rule.selector
                for prop, value in rule.declerations.items():
                    css_text += "\t\t%s : %s;\n" % (prop, value)
                css_text += "\t}\n"
            css_elm.append(CDATA(css_text))
            res =  [css_elm] + res
        return res



def apply_size_units(svg, units):
    if ("viewBox" in svg.attributes):
        raise Exception("viewBox allready set")
    svg.update(width = "%s%s" % (int(svg.attributes["width"]), units),
               height = "%s%s" % (int(svg.attributes["height"]), units),
               viewBox = TextItems(0, " ", 0, " ", 
                                   svg.attributes["width"], 
                                   " ",
                                   svg.attributes["height"]))
    

def prettyxml(elm):
    return minidom.parseString(tostring(elm)).toprettyxml()
        
def wrappWithHTML(elm):
    html = Element("html")
    body = Element("body")
    html.append(body)
    body.append(elm)
    return html


def save_svg(svg, path, html_name=None):
    fh = file(path, "w")
    obj = svg.asElement()
    #if (html):
    #    obj = wrappWithHTML(obj)
    fh.write(prettyxml(obj))
    fh.close()
    if (html_name):
        html_path = os.path.join(os.path.dirname(path), html_name)
        fh = file(html_path, "w")
        fh.write('<html><body><img src="%s"/></body></html>' %
        os.path.basename(path))
        fh.close()

