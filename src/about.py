from window import Dialog
from appuifw import *
import key_codes

from wmglobals import VERSION

__all__ = [ "About" ]

class About(Dialog):
    def __init__(self,cbk):
        self.items = [ ( u"Iamdoing %s" % VERSION, u"A Twitter client" ),
                       ( u"Author", u"Marcelo Barros de Almeida" ),
                       ( u"Email", u"marcelobarrosalmeida@gmail.com" ),
                       ( u"Source code", u"http://iamdoing.googlecode.com" ),
                       ( u"License", u"GNU GPLv3" ),
                       ( u"Warning", u"Use at your own risk" ) ]

        values = map( lambda x: (x[0], x[1]), self.items )
        
        Dialog.__init__(self, cbk, u"About", Listbox( values, self.show_info ) )
        
        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.show_info)

    def show_info(self):
        idx = app.body.current()
        note( self.items[idx][1],"info" )
        

