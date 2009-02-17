# -*- coding: utf-8 -*-
import re, time, os
import key_codes
from appuifw import *
import appuifw
from window import Application
from about import About
from settings import Settings, sel_access_point
from wmutil import *
from wmglobals import VERSION, DEFDIR
from persist import DB
from s60twitter import TwitterApi


__all__ = [ "Iamdoing" ]
__author__ = "Marcelo Barros de Almeida (marcelobarrosalmeida@gmail.com)"
__version__ = VERSION
__copyright__ = "Copyright (c) 2009- Marcelo Barros de Almeida"
__license__ = "GPLv3"

class Iamdoing(Application):
    
    def __init__(self):
        menu = [ (u"Setting", self.settings),
                 (u"About", self.about),
                 (u"Close", self.close_app)]
        self.body = Listbox([(u"", u"")], self.check_update_value )
        Application.__init__(self,  u"I am doing ...", self.body, menu )
        self.dlg = None
        self.twitter_user = ""
        self.twitter_password = ""
        self.proxy = ""
        self.twitter_api = None
        self.page = 1
        self.headlines = [(u"",u"")]
        self.timeline = {}
        self.last_idx = 0
        self.tooltip = appuifw.InfoPopup()
        sel_access_point()
        self.check_conn_params()

        self.bind(key_codes.EKeyRightArrow, self.inc_page)
        self.bind(key_codes.EKeyLeftArrow, self.dec_page)
        self.bind(key_codes.EKeyUpArrow, self.key_up)
        self.bind(key_codes.EKeyDownArrow, self.key_down)
        
    def check_conn_params(self):
        if DB["proxy_enabled"] == u"True":
            user = unicode_to_utf8( DB["proxy_user"] )
            addr = unicode_to_utf8( DB["proxy_addr"] )
            port = unicode_to_utf8( DB["proxy_port"] )
            user = unicode_to_utf8( DB["proxy_user"] )
            pwrd = unicode_to_utf8( DB["proxy_pass"] )
            
            if user:
                self.proxy = "http://%s:%s@%s:%s" % (user,pwrd,addr,port)
            else:
                self.proxy = "http://%s:%s" % (addr,port)
        else:
            self.proxy = ""
            
        self.twitter_user = DB["twitter_user"]             
        self.twitter_password = DB["twitter_pass"]
        self.twitter_api = TwitterApi(self.twitter_user,
                                      self.twitter_password,
                                      self.proxy)
    def inc_page(self):
        if not self.ui_is_locked():
            self.page += 1
            self.refresh_timeline()

    def dec_page(self):
        if not self.ui_is_locked():
            self.page -= 1
            if self.page < 1:
                self.page = 1
            else:
                self.refresh_timeline()
                
    def key_up(self):
        if not self.ui_is_locked():
            p = app.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title(u"[%d/%d] Page %d" % (p+1,m,self.page))
            self.tooltip.show(self.headlines[p][1], (0,30), 1750, 0.25, appuifw.EHLeftVTop )

    def key_down(self):
        if not self.ui_is_locked():
            p = app.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title(u"[%d/%d] Page %d" % (p+1,m,self.page))
            self.tooltip.show(self.headlines[p][1], (30,30), 1750, 0.25, appuifw.EHLeftVTop )

    def check_update_value(self):
        if not self.ui_is_locked():
            self.update_value()
            
    def update_value(self):
        idx = self.body.current()
        self.last_idx = idx
        menu = []
        if self.timeline.has_key(self.page):
            menu += [(u"Details", self.details),
                     (u"Send update", self.send_update)]
        if not self._is_mine(idx) and self.timeline.has_key(self.page):
            menu += [(u"Reply", self.reply)]
        if self._has_link(idx):
            menu += [(u"Follow links", self.follow_links)]
        if self._is_mine(idx):
            menu += [(u"Delete",self.delete)]
        menu += [(u"Refresh", self.refresh_pages)]
            
        op = popup_menu(map( lambda x: x[0], menu ), u"Menu:")
        if op is not None:
            map(lambda x: x[1], menu)[op]()

    def _has_link(self,idx):
        idx = self.body.current()
        if self.timeline.has_key(self.page):
            msg = self.timeline[self.page][idx][u'text']
            http = re.compile(u"http://\S+", re.IGNORECASE)
            links = re.findall(http, msg)
            if links:
                return True
        return False
    
    def _is_mine(self,idx):
        idx = self.body.current()
        if self.timeline.has_key(self.page):
            if self.timeline[self.page][idx][u'user'][u'screen_name'] == self.twitter_user:
                return True
        return False
    
    def details(self):
        idx = self.body.current()
        txt = self.headlines[idx][0] + u"\n" + self.headlines[idx][1]
        note(txt,"info")

    def refresh_pages(self):
        self.timeline = {}
        self.page = 1
        self.refresh_timeline()
        
    def refresh_timeline(self):
        if not self.timeline.has_key(self.page):
            self.lock_ui(u"Downloading page %d..." % self.page)
            try:
                self.timeline[self.page] = self.twitter_api.get_friends_timeline(self.page)
            except:
                note(u"Impossible to download page %d..." % self.page,"error")
                self.unlock_ui()
                self.refresh()
                return
            self.unlock_ui()
                
        self.headlines = []
        for msg in self.timeline[self.page]:
            r1 = msg[u'user'][u'screen_name']
            if msg[u'in_reply_to_screen_name']:
                r1 += u" to %s" % msg[u'in_reply_to_screen_name']
            r1 += u" %s" % self.twitter_api.human_msg_age(msg[u'created_at'])
            r2 = msg[u'text']
            self.headlines.append((r1,r2))
        self.last_idx = 0
        self.refresh()

    def send_update(self): pass
    def send_tweet_to_tweeter(self): pass
    def reply(self): pass
    def follow_links(self):
        idx = self.body.current()
        msg = self.timeline[self.page][idx][u'text']
        http = re.compile(u"http://\S+", re.IGNORECASE)
        links = re.findall(http, msg)
        if len(links) == 1:
            link = links[0]
        else:
            op = popup_menu(links,u"Which link?")
            if op is not None:
                link = links[op]
            else:
                return
        # prepare html file
        name = "html_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
        name = os.path.join(DEFDIR, "cache", name)
        try:
            fp = open(name,"wt")
            fp.write('<html>\n')
            fp.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n')
            fp.write('<head><title>Redirecting...</title></head>\n')
            fp.write('<body><script>document.location="%s"</script></body>' % link)
            fp.write('</html>')
            fp.close()
        except:
            note(u"Impossible to create html file","error")
            return
        viewer = Content_handler(self.refresh)
        try:
            viewer.open(name)
        except:
            note(u"Impossible to launch browser","error")
        
    def delete(self): pass
    
    def settings(self):
        def cbk():
            self.check_conn_params()
            self.refresh()
            return True              
        self.dlg = Settings(cbk)
        self.dlg.run()

    def close_app(self):
        ny = popup_menu( [u"Yes", u"No"], u"Exit ?" )
        if ny is not None:
            if ny == 0:
                self.clear_cache()
                Application.close_app(self)

    def refresh(self):
        Application.refresh(self)
        idx = self.body.current()
        if not self.headlines:
            self.headlines = [(u"", u"")]
        self.last_idx = min( self.last_idx, len(self.headlines)-1 )
        app.body.set_list(self.headlines, self.last_idx)
        self.set_title(u"Page %d" % (self.page))

    def clear_cache(self):
        not_all = False
        cache = os.path.join(DEFDIR, "cache")
        entries = os.listdir( cache )
        for e in entries:
            fname = os.path.join(cache,e)
            if os.path.isfile( fname ):
                try:
                    os.remove( fname )
                except:
                    not_all = True
        if not_all:
            note(u"Not all files in %s could be removed. Try to remove them later." % cache,"error")

    def about(self):
        def cbk():
            self.refresh()
            return True        
        self.dlg = About(cbk)
        self.dlg.run()
        
if __name__ == "__main__":

    imd = Iamdoing()
    imd.run()
