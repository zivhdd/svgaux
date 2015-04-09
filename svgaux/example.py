from svgaux import *

css = [Rule(".cut", stroke = "#006600", fill="white")]
svg = SVG(css_rules=css, width="800", height="800")
svg.append(Shape(TAGS.rect, x=0, y=0, width=800, height=800, cls="cut"))
notes = Group(transform=Transform.translate(200, 200))
svg.append(notes)
for i in xrange(15):
    height = 40 + i*5
    rect = Shape(TAGS.rect, cls="cut", x=0, y=-height, width="35", height=height,
                 transform=Transform.rotate(i*15, 12.5, 160))
    notes.append(rect)

outf = file("example.html", "w")
res = prettyxml(wrappWithHTML(svg.asElement()))
print res
print >>outf, res
outf.close()

