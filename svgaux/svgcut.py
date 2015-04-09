from xml.etree import ElementTree 
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# patch for CDATA support

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


class SEnum(object):
    def __init__(self, *args):
        self.__dict__.update(dict(zip(args, args)))

class TransformCls(object):
    def __getattribute__(self, name):
        return (lambda *args: "%s(%s)" % (name, " ".join(map(str, args))))

TAGS = SEnum("rect", "circle", "path")
Transform = TransformCls()

    
class Shape(object):

    KEYWORDS = set(["class"])
    def __init__(self, tag, **kargs):
        self.tag = tag
        self.attributes = {}
        self.update(**kargs)
    
    def update(self, cls=None, transform=None, **kargs):
        self.attributes.update(kargs)
        self.cls = cls
        self.transform = transform

    def asElement(self):
        elm = Element(self.tag)        
        elm.attrib.update(dict(map(lambda x: (x[0], str(x[1])), self.attributes.items())))
        if (self.cls):
            elm.attrib["class"] = self.cls
        if (self.transform):
            transform = (self.transform if (type(self.transform) == str) 
                         else [self.transform])
            elm.attrib["transform"] = transform 
        return elm
    

class Group(Shape):
    def __init__(self, items=[], **kargs):
        Shape.__init__(self, self.groupTag(), **kargs)
        self.items = [] + items

    def groupTag(self):
        return "g"

    def asElement(self):
        elm = Shape.asElement(self)
        for x in self.inner():
            elm.append(x)
        return elm

    def inner(self):
        return [x.asElement() for x in self.items]

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
        Group.__init__(self, **attributes)
        self.css_rules = css_rules

    def inner(self):
        res = Group.inner(self)
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

    def groupTag(self):
        return "svg"


        
def prettyxml(elm):
    return minidom.parseString(tostring(elm)).toprettyxml()
        
def wrappWithHTML(elm):
    html = Element("html")
    body = Element("body")
    html.append(body)
    body.append(elm)
    return html


        

