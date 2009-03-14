# -*- coding: cp1252 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
from appuifw import *
import e32
import graphics
import key_codes

class CanvasListBox(Canvas):
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    DARK_GREEN = (0,102,0)
    BLUE1 = (51,204,255)
    YELLOW = (255,255,102)

    XA = 0
    YA = 0
    XB = 0
    YB = 0
    
    SCROLL_BAR_W = 5
    SCROLL_BAR_COLOR = WHITE

    #SELECTION_RADIUS = 3
    #SELECTION_DIAMETER = 2*SELECTION_RADIUS
    #SELECTION_SCROLL_BAR_DIST = 3

    SELECTION_COLOR = DARK_GREEN

    TEXT_LEFT_MARGIN = 2
    TEXT_RIGHT_MARGIN = SCROLL_BAR_W
    TEXT_H = 12
    TEXT_LINE_SEP = 5
    TEXT_COLOR = YELLOW
    TEXT_FONT = 'dense'
    
    def __init__(self,elements,cbk=lambda:None):
        Canvas.__init__(self,
                        redraw_callback = self.redraw_list,
                        event_callback = self.event_list)
        self._screen = graphics.Image.new(self.size)
        self.XB, self.YB = self.size
        self.cbk = cbk
        self.set_list(elements)
        self.bind(key_codes.EKeyUpArrow, self.up_key)
        self.bind(key_codes.EKeyDownArrow, self.down_key)
        self.bind(key_codes.EKeySelect, self.cbk)
        
    def redraw_list(self,rect=None):
        self.clear_list()
        self.draw_scroll_bar()
        self.draw_selection_box()
        self.redraw_elements()

    def draw_scroll_bar(self):
        self._screen.rectangle((self.XB - self.SCROLL_BAR_W, self.YA, self.XB, self.YB),
                               outline = self.SCROLL_BAR_COLOR)
        list_size = len(self._proc_elements)
        if list_size:
            sz = (self.YB - self.YA)/list_size + 1 # rounding up always
            pos = self._current_sel*sz
            self._screen.rectangle((self.XB - self.SCROLL_BAR_W, pos, self.XB, pos + sz),
                                   outline = self.SCROLL_BAR_COLOR, fill = self.SCROLL_BAR_COLOR)            

    def draw_selection_box(self):
        if len(self._proc_elements):
            xa = 0
            xb = self.XB - self.TEXT_RIGHT_MARGIN
            ya = self.TEXT_LEFT_MARGIN
            for m in range(self._current_sel_in_view):
                n = self._selection_view[0] + m
                ya += self._proc_elements[n]['num_lines']*(self.TEXT_H + self.TEXT_LINE_SEP)
            yb = ya + self._proc_elements[self._selection_view[0] +
                                          self._current_sel_in_view]['num_lines']*(self.TEXT_H + self.TEXT_LINE_SEP)
            ya -= self.TEXT_LINE_SEP/2
            yb -= self.TEXT_LINE_SEP/2
            self._screen.rectangle((xa,ya,xb,yb),
                                   outline = self.SELECTION_COLOR,
                                   fill = self.SELECTION_COLOR)

    def redraw_elements(self):
        x = self.TEXT_LEFT_MARGIN
        y = self.TEXT_LEFT_MARGIN + self.TEXT_H
        n = self._selection_view[0]
        while y < self.YB and n < len(self._proc_elements):
        #for n in range(self._selection_view[0],self._selection_view[1]):
            ele = self._proc_elements[n]
            for m in range(ele['num_lines']):
                self._screen.text((x,y),ele['text'][m], fill = self.TEXT_COLOR, font = self.TEXT_FONT)
                y += self.TEXT_H + self.TEXT_LINE_SEP
            n += 1

    def calculate_sel_view(self):
        n = self._selection_view[0]
        y = self.TEXT_LEFT_MARGIN
        while y < self.YB and n < len(self._proc_elements):
            y += self._proc_elements[n]['num_lines']*(self.TEXT_H + self.TEXT_LINE_SEP)
            n += 1
        if y >= self.YB:
            # ensure all elements in view are visible
            n -= 1
        # base index is 0
        self._selection_view[1] = n - 1
        #print "sel view =",self._selection_view
            
    def up_key(self):
        if self._current_sel <= 0:
            return       
        #print "cursel, curselvw", self._current_sel, self._current_sel_in_view, self._selection_view
        n = self._current_sel - 1
        if n < self._selection_view[0]:
            self._selection_view[0] -= 1
            self.calculate_sel_view()
        else:
            self._current_sel_in_view -= 1
            
        self._current_sel = self._current_sel_in_view + self._selection_view[0]
        #print "cursel, curselvw", self._current_sel, self._current_sel_in_view , self._selection_view
        self.redraw_list()               

    def down_key(self):
        if self._current_sel >= (len(self._proc_elements) - 1):
            return
        #print "cursel, curselvw", self._current_sel, self._current_sel_in_view , self._selection_view
        n = self._current_sel + 1
        if n > self._selection_view[1]:
            # ensure that selected item in inside the view, increasing the begining until it fits
            while n > self._selection_view[1]:
                self._selection_view[0] += 1
                self.calculate_sel_view()
            self._current_sel_in_view = n - self._selection_view[0]
        else:
            self._current_sel_in_view += 1

        self._current_sel = n
        #self._current_sel_in_view + self._selection_view[0]
        #print "cursel, curselvw", self._current_sel, self._current_sel_in_view , self._selection_view
        self.redraw_list()            

    def build_entries(self,elements):
        self._proc_elements = []
        for text in elements:
            reg = {}
            reg['text'] = self.split_text(text)
            reg['num_lines'] = len(reg['text'])
            reg['height'] = reg['num_lines']*(self.TEXT_H + self.TEXT_LINE_SEP)
            self._proc_elements.append(reg)
            #print reg
            
    # modified version of TextRenderer.chop 
    # http://discussion.forum.nokia.com/forum/showthread.php?t=124666
    def split_text(self, text):
        lines = []
        text_left = text
        width = self.XB - self.TEXT_LEFT_MARGIN - self.TEXT_RIGHT_MARGIN
        while len(text_left) > 0: 
            bounding, to_right, fits = self.measure_text(text_left,
                                                         font=self.TEXT_FONT,
                                                         maxwidth=width,
                                                         maxadvance=width)
            
            if fits <= 0:
                lines.append(text_left)
                break
                    
            #print "tor:" + str(to_right) + " fits:" + str(fits)
            slice = text_left[0:fits]
        
            # How many chars we can skip at the end of the row
            # (whitespaces at the end of the row)
            adjust = 0
        
            if len(slice) < len(text_left):
                # find the separator character closest to the right
                rindex = -1
                for sep in u" .;:\\/-":
                    idx = slice.rfind(sep)
                    if idx > rindex:
                        rindex = idx
                if rindex > 0:
                    if slice[rindex] == u' ':
                        adjust = 1
                    slice = slice[0:rindex]
                                
            lines.append(slice)
            text_left = text_left[len(slice)+adjust:]
        
        return lines
    
    def event_list(self,ev):
        pass

    def clear_list(self):
        self._screen.clear(self.BLACK)
        self.blit(self._screen)

    def current(self):
        return self._current_sel

    def set_list(self,elements):
        self._current_sel = 0
        self._current_sel_in_view = 0
        self._selection_view = [0,0]
        self.build_entries(elements)        
        self.calculate_sel_view()
        self.redraw_list()
