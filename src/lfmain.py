#!/usr/bin/env python
""" lfmain.py --

 UI generated by GUI Builder Build 146 on 2010-04-12 18:18:23 from:
    /media/data/hubi/code/python/little-frinc/src/lfmain.ui
 This file is auto-generated.  Only the code within
    '# BEGIN USER CODE (global|class)'
    '# END USER CODE (global|class)'
 and code inside the callback subroutines will be round-tripped.
 The 'main' function is reserved.
"""

from Tkinter import *
from lfmain_ui import Lfmain

# BEGIN USER CODE global
import tkMessageBox

UPDATE_TIME = 1000
EXIT_TEXT = "Are you sure you want to exit? There are unfinished packets"
# END USER CODE global

class CustomLfmain(Lfmain):
    pass

    # BEGIN CALLBACK CODE
    # ONLY EDIT CODE INSIDE THE def FUNCTIONS.

    # _butAdd_command --
    #
    # Callback to handle _butAdd widget option -command
    def _butAdd_command(self, *args):
        
        links = self._lsLinks.get(0, 'end')
        if len(links) <= 0:
            return
        
        result = self._man.padd(links)

    # _butClearall_command --
    #
    # Callback to handle _butClearall widget option -command
    def _butClearall_command(self, *args):
        pass

    # _butExit_command --
    #
    # Callback to handle _butExit widget option -command
    def _butExit_command(self, *args):
        
        if self._app.warn_unfinished:
            
            for i in self._man.get_packets():
                if not i.is_finished():
                    if tkMessageBox.askyesno("Exit Little-Frinc?", EXIT_TEXT):
                        self._app.exit()
                    return
        
        self._app.exit()

    # _butHistory_command --
    #
    # Callback to handle _butHistory widget option -command
    def _butHistory_command(self, *args):
        pass

    # _butKillpacket_command --
    #
    # Callback to handle _butKillpacket widget option -command
    def _butKillpacket_command(self, *args):
        
        curr = self._lsPackets.curselection()
        if len(curr) > 0:
        	curr = curr[0]
        	name = self._lsPackets.get(curr)
        	self._man.pkill(name)

    # _butPwd_command --
    #
    # Callback to handle _butPwd widget option -command
    def _butPwd_command(self, *args):
        
        self._app.show_pwd()

    # _butRemove_command --
    #
    # Callback to handle _butRemove widget option -command
    def _butRemove_command(self, *args):
        
        curr = self._lsLinks.curselection()
        
        curr = [i for i in curr]
        curr.sort(reverse = True)
        
        for i in curr:
            self._lsLinks.delete(i)

    # _butResetsoft_command --
    #
    # Callback to handle _butResetsoft widget option -command
    def _butResetsoft_command(self, *args):
        
        curr = self._lsPackets.curselection()
        if len(curr) > 0:
        	curr = curr[0]
        	name = self._lsPackets.get(curr)
        	self._man.preset(name)

    # _butStart_command --
    #
    # Callback to handle _butStart widget option -command
    def _butStart_command(self, *args):
        
        curr = self._lsPackets.curselection()
        if len(curr) > 0:
        	curr = curr[0]
        	name = self._lsPackets.get(curr)
        	self._man.pstart(name)

    # _lsLinks_xscrollcommand --
    #
    # Callback to handle _lsLinks widget option -xscrollcommand
    def _lsLinks_xscrollcommand(self, *args):
        pass

    # _lsLinks_yscrollcommand --
    #
    # Callback to handle _lsLinks widget option -yscrollcommand
    def _lsLinks_yscrollcommand(self, *args):
        pass

    # _lsPackets_xscrollcommand --
    #
    # Callback to handle _lsPackets widget option -xscrollcommand
    def _lsPackets_xscrollcommand(self, *args):
        pass

    # _sclPackets_command --
    #
    # Callback to handle _sclPackets widget option -command
    def _sclPackets_command(self, *args):
        pass

    # _txData_xscrollcommand --
    #
    # Callback to handle _txData widget option -xscrollcommand
    def _txData_xscrollcommand(self, *args):
        pass

    # _txData_yscrollcommand --
    #
    # Callback to handle _txData widget option -yscrollcommand
    def _txData_yscrollcommand(self, *args):
        pass

    # _txLog_xscrollcommand --
    #
    # Callback to handle _txLog widget option -xscrollcommand
    def _txLog_xscrollcommand(self, *args):
        pass

    # _txLog_yscrollcommand --
    #
    # Callback to handle _txLog widget option -yscrollcommand
    def _txLog_yscrollcommand(self, *args):
        pass

    # END CALLBACK CODE

    # BEGIN USER CODE class
    
    def __nmsg(self, msg):
    	self._txLog.delete('0.0', 'end')
    	self._txLog.insert('end', msg)
    
    def __amsg(self, msg):
    	self._txLog.insert('end', msg)
    
    def __update_packets(self, root):
    	
    	# update listbox
        lnames = self._lsPackets.get(0, 'end')
        pnames = [i.get_name() for i in self._man.get_packets()]
    		
        ran = range(len(lnames))
        ran.sort(reverse = True)
    		
        for i in ran:
            name = self._lsPackets.get(i)
            if not name in pnames:
                self._lsPackets.delete(i)
        
        for name in pnames:
            if not name in lnames:
                self._lsPackets.insert('end', name)
        
        # update label
        curr = self._lsPackets.curselection()
        if len(curr) > 0:
            curr = self._lsPackets.get(curr[0])
            for i in self._man.get_packets():
                if i.has_name(curr):
                    self._labStatus.config(
                        text="\n".join(i.status().split(' ')))
    
    	root.after(UPDATE_TIME, self.__update_packets, root)
    
    def __past_and_scan(self, event):
        
        self._txData.delete('0.0', 'end')
        event.widget.event_generate("<<Paste>>")
        self.__scan()
    
    def __scan(self):
        
        data = self._txData.get('0.0', 'end')
        links = pfscan.scanlinks(data)
        links = pfutil.resolve_links(links)
        
        foundlinks = self._lsLinks.get(0, 'end')
        for link in links:
            if (not link in foundlinks) and (link != ''):
                self._lsLinks.insert('end', link)

    
    def __init__(self, app):
        
        self._app = app
        self._man = app.manager
        root = self._app.root
        
        Lfmain.__init__(self, root
        )
        self._sclPackets["command"] = self._lsPackets.yview
        # bindings...
        root.bind("<Control_L>v", self.__past_and_scan)
        self._txData.bind("<Button-3>", self.__past_and_scan)
        
        root.after(UPDATE_TIME, self.__update_packets, root)
    # END USER CODE class

def main():
    # Standalone Code Initialization
    # DO NOT EDIT
    try: userinit()
    except NameError: pass
    root = Tk()
    demo = CustomLfmain(root)
    root.title('lfmain')
    try: run()
    except NameError: pass
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.mainloop()

if __name__ == '__main__': main()
