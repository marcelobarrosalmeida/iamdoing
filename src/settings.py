# -*- coding: utf-8 -*-
from appuifw import *
from window import Dialog
from socket import select_access_point, access_point, access_points, set_default_access_point
from wmutil import *
import key_codes
from persist import DB

__all__ = [ "sel_access_point", "TwitterSettings", "ProxySettings", "Settings" ]

def sel_access_point():
    """ Select the default access point. Return True if the selection was
        done or False if not
    """
    aps = access_points()
    if not aps:
        note(u"Could't find any access point.","error")
        return False
    
    ap_labels = map( lambda x: x['name'], aps )
    item = popup_menu( ap_labels, u"Access points:" )
    if item is None:
        note(u"At least one access point is required.","error")
        return False
    
    apo = access_point( aps[item]['iapid'] )
    set_default_access_point( apo )
    
    return True

class TwitterSettings(Dialog):
    def __init__(self, cbk):
        self.twitter_user = DB["twitter_user"]             
        self.twitter_password = DB["twitter_pass"]

        self.last_idx = 0
        body =  Listbox( [ (u"",u"") ], self.update_value )
        menu = [( u"Cancel", self.cancel_app )]
        
        Dialog.__init__(self, cbk, u"Twitter settings", body,  menu)

        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
        
    def refresh(self):
        Dialog.refresh(self)
        values = [ (u"Twitter username", self.twitter_user), \
                   (u"Twitter password", u"*"*len( self.twitter_password ) ) ]
        app.body.set_list( values, self.last_idx )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx                  
        if idx == 0:
            user = query(u"Twitter username","text", self.twitter_user)
            if user is not None:
                self.twitter_user = user
            else:
                self.twitter_user = u""
        elif idx == 1:
            password = query(u"Twitter password","code", self.twitter_password)
            if password is not None:
                self.twitter_password = password
            else:
                self.twitter_password = u""
        self.refresh()

class ProxySettings(Dialog):
    def __init__(self, cbk):
        self.proxy_enabled = DB["proxy_enabled"]
        self.proxy_address = DB["proxy_addr"]
        self.proxy_port = int(DB["proxy_port"])
        self.proxy_user = DB["proxy_user"]             
        self.proxy_password = DB["proxy_pass"]

        self.last_idx = 0
        body =  Listbox( [ (u"",u"") ], self.update_value )
        menu = [( u"Cancel", self.cancel_app )]
        
        Dialog.__init__(self, cbk, u"Proxy settings", body,  menu)

        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
        
    def refresh(self):
        Dialog.refresh(self)
        values = [ (u"Enabled", self.proxy_enabled  ), \
                   (u"Address", self.proxy_address ), \
                   (u"Port", unicode( self.proxy_port ) ), \
                   (u"Username", self.proxy_user), \
                   (u"Password", u"*"*len( self.proxy_password ) ) ]

        app.body.set_list( values, self.last_idx )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx
        
        if idx == 0:
            if self.proxy_enabled == u"True":
                self.proxy_enabled = u"False"
            else:
                self.proxy_enabled = u"True"
        elif self.proxy_enabled == u"True":
            if idx == 1:
                addr = query(u"Proxy address:","text", self.proxy_address)
                if addr is not None:
                    self.proxy_address = addr
            elif idx == 2:
                port = query(u"Proxy port:","number", self.proxy_port)
                if port is not None:
                    self.proxy_port = port                         
            elif idx == 3:
                user = query(u"Proxy username:","text", self.proxy_user)
                if user is not None:
                    self.proxy_user = user
                else:
                    self.proxy_user = u""
            elif idx == 4:
                password = query(u"Proxy username:","code", self.proxy_password)
                if password is not None:
                    self.proxy_password = password
                else:
                    self.proxy_password = u""
        self.refresh()

class Settings(Dialog):
    def __init__(self,cbk):
        self.dlg = None
        items = [ ( u"Twitter",u""),
                  ( u"Proxy", u""),
                  ( u"Access Point", u"") ]

        Dialog.__init__(self, cbk, u"Settings", Listbox( items, self.update_value ) )

        self.bind(key_codes.EKeyRightArrow, self.update_value)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)        

    def update_value(self):
        idx = self.body.current()
        ( self.twitter, self.proxy, self.access_point)[idx]()

    def twitter_cbk(self):
        self.lock_ui()
        if not self.dlg.cancel:
            DB["twitter_user"] = self.dlg.twitter_user
            DB["twitter_pass"] = self.dlg.twitter_password
            DB.save()
        self.unlock_ui()
        self.refresh()
        return True
    
    def twitter(self):
        self.dlg = TwitterSettings( self.twitter_cbk )
        self.dlg.run()
        
    def proxy_cbk(self):
        self.lock_ui()
        if not self.dlg.cancel:
            DB["proxy_enabled"]= self.dlg.proxy_enabled
            DB["proxy_addr"] = self.dlg.proxy_address
            DB["proxy_user"] = self.dlg.proxy_user
            DB["proxy_pass"] = self.dlg.proxy_password
            DB["proxy_port"] = utf8_to_unicode( str(self.dlg.proxy_port) )
            DB.save()
        self.unlock_ui()
        self.refresh()
        return True
        
    def proxy(self):
        self.dlg = ProxySettings( self.proxy_cbk )
        self.dlg.run()

    def access_point(self):
        sel_access_point()
    
