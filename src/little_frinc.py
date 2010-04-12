#! /usr/bin/env python
#  little frinc

DEBUG_ = True

from Tkinter import *

from lfmain import CustomLfmain
from pfpwd import CustomPfpwd

import sys
import os
import threading
import time
import platform

import pfmanager
import pfdetainer

NOTIFY_TIME = 4000
USE_PYNOTIFY = False

if platform.system() == 'Windows':
    print "ohh... windows... naja..."
    CONFIG_HOST = CONFIG_HOST.strip('.local')
    print "ohne curl & unrar in der PATH variable geht aber bitte garnix"

def global_report(msg):
    print msg

try:
    if not USE_PYNOTIFY:
        raise Exception("don't use pynotify")
    
    import pynotify
    if not pynotify.init("pfgui"):
        raise Exception("init notify failed")
    
    def global_report(msg):
        notify = pynotify.Notification("pfgui", msg)
        notify.set_timeout(NOTIFY_TIME)
        notify.show()
        print msg
    
except:
    pass

class application(object):
    
    def __init__(self, cfg_path):
        
        if 'NPYCK_' in globals():
            self._npyck = True
        else:
            self._npyck = False
        
        self._cfg = self.__loadconfig(cfg_path)
        
        if self._cfg.has_key('cfg'):
            self.detainer = pfdetainer.file_detainer(self._cfg['cfg'])
            self.warn_unfinished = False
        else:
            self.warn_unfinished = True
            self.detainer = pfdetainer.mem_detainer()
        
        self.manager = pfmanager.manager(self._cfg, self.detainer,
            load_pending=True)
        self.root = Tk()
        # self will be passed
        self._main_gui = CustomLfmain(self)
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self._pwd_tk = None
        self._pwd_gui = None
    
    def mainloop(self):
        
        self.root.mainloop()
    
    def show_pwd(self):
        
        if self._pwd_tk is None and self._pwd_gui is None:
            self._pwd_tk = Tk()
            self._pwd_tk.protocol('WM_DELETE_WINDOW', self.close_pwd)
            self._pwd_gui = CustomPfpwd(self._pwd_tk, self)
            
            self._pwd_tk.mainloop()
    
    def close_pwd(self):
        
        self._pwd_tk.quit()
        self._pwd_tk.destroy()
        self._pwd_tk = None
        self._pwd_gui = None
    
    def pwd_list(self):
        
        return self._cfg['pwd']
    
    def __loadconfig(self, cfg_path):
        
        data = None
        
        if self._npyck:
            data = NPYCK_.ne_read(cfg_path)
        
        if data is None:
            f = open(cfg_path, "r")
            data = f.read()
            f.close()
        
        cfg = {}
        
        for line in data.split('\n'):
            line = line.strip('\r')
            if line.startswith('from'):
                cfg['from'] = line.lstrip('from').strip(' ')
            elif line.startswith('to'):
                cfg['to'] = line.lstrip('to').strip(' ')
            elif line.startswith('pwd'):
                cfg['pwd'] = line.lstrip('pwd').strip(' ').split(' ')
            elif line.startswith('cfg'):
                cfg['cfg'] = line.lstrip('cfg').strip(' ')
        
        data = None
        
        if self._npyck:
            data = NPYCK_.read("rapidshare-cookie")
        
        if data is None:
            f = open(os.path.join(cfg['cfg'], "rapidshare-cookie"), 'r')
            data = f.read()
            f.close()
        
        cfg['rapid-share'] = data
        
        return cfg
        
    def report(self, msg):
        
        global_report(msg)

    def exit(self):
        
        self.root.quit()
        self.manager.kill()
        #sys.exit()
        
def main(args):
    "The main entry-point."
    
    path = "config.txt"
    if len(args) > 0:
        path = args[0]
    
    app = application(path)
    app.mainloop()

if __name__ == "__main__": main(sys.argv[1:])

