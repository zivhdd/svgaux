from svgaux import *


SIDES = SEnum("WIDTH", "HEIGHT", "DEPTH")

class Case:
    
    def __init__(self, width, depth, height, thickness, tab, cls):
        self.width = width
        self.depth = depth
        self.height = height
        self.thickness = thickness
        self.tab = tab
        self.cls = cls

    def pmove(self, x, y, abs=False):

        if (abs):
            self.pos = (x,y)
        else:
            self.pos = (self.pos[0] + x, self.pos[1] + y)

        return ["M", self.pos[0], ",", self.pos[1], ""]

    def pline(self, z, factor, yaxis, abs=False):
        
        if yaxis:
            coords = [0, z*factor]
        else:
            coords = [z*factor, 0]
        
        if (abs):
            self.pos = coords
        else:
            self.pos = (self.pos[0] + coords[0], self.pos[1] + coords[1])
        return ["L", self.pos[0], ",", self.pos[1], " "]

    def part(self, hsize, vsize, hlead=True, vlead=True, 
             level=[False, False, False, False],
             px=0, py=0, gap=0):

        hsteps = hsize / self.tab
        hsteps += (hsteps + 1)% 2
        htab = float(hsize) / hsteps
        vsteps = vsize / self.tab
        vsteps += (vsteps + 1) % 2
        vtab = float(vsize) / vsteps

        items = self.pmove(px, py, abs=True)
        offs = [-1,1][vlead] ;
        items += self.pmove((not hlead) * self.thickness, 
                            self.thickness * (not vlead))
        debt = self.thickness * (not vlead)

        tabs = (htab, vtab)
        leads = (hlead, vlead)
        steps = (hsteps, vsteps)
        
        for itr in xrange(4):

            dirc = [-1,1][itr<2]
            axis = itr % 2
            step_axis = 1 - axis
            step_dir = [-1, 1, 1, -1][itr]
            debt = self.thickness * (not leads[axis])
            offs = [-1,1][leads[1-axis]] ;
            for i in xrange(steps[axis] - 1):
                items += self.pline((tabs[axis] - debt), dirc, axis)
                debt = 0

                if (not level[itr]):
                    offs = -offs;
                    items += self.pline(self.thickness, offs*step_dir, step_axis)
            items += self.pline((tabs[axis] - (not leads[axis]) * self.thickness), 
                                dirc, axis)
            debt = (offs < 0) * self.thickness

        items.append(" Z")
        return Shape(TAGS.path, cls=self.cls,
                     d = TextItems(*items))


    def recalc_tab(self, size):
        steps = int(float(size) / self.tab)
        steps += (steps + 1) % 2
        tab = float(size) / steps
        return tab, steps

    def top(self, **kargs):
        return self.part(self.width, self.depth, False, False, **kargs)
    
    def front(self, **kargs):
        return self.part(self.width, self.height, False, True, **kargs)

    def side(self, **kargs):
        return self.part(self.depth, self.height, True, True, **kargs)

    def front_trails_on_bottom(self, lead=True, ly = 0):
        htab, steps = self.recalc_tab(self.width)
        grp = Group(TAGS.g)
        for idx in xrange(steps):            
            if (idx % 2 != lead):
                grp.append(Shape(TAGS.rect, x = idx * htab, y = ly, width = htab, 
                                 height = self.thickness, cls="cut"))
        return grp
            
    def front_trails_on_side(self, lead=False, lx = 0):
        tab, steps = self.recalc_tab(self.height)
        grp = Group(TAGS.g)
        for idx in xrange(steps):            
            if (idx % 2 != lead):
                grp.append(Shape(TAGS.rect, y = idx * tab, x = lx, height = tab, 
                                 width = self.thickness, cls="cut"))
        return grp
        
        


