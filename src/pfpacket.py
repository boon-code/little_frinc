import socket
import Queue
import threading
import re
import os
import time
import curl
import pfextractor
import curl
import kill_except

UPDATE_INTERVAL = 0.5
FILENAME_RE = re.compile(".*/([^/]*)")
EXCEED_MSG = 'You have exceeded the download limit.'

INIT = 'none'
WAITING = 'wait'
LOADING = 'dl'
DOWNLOADED = 'dl-done'
EXTRACTING = 'ex'
FINISHED = 'fin'
ERROR = 'err'
KILLED = 'kill'

def mklist(*elements):
    return elements

class pf_packet(object):
    
    def __init__(self, name, repeated=False):
        "Initialize packet - struct."
        
        self._name = name
        self._links = []
        self._firstfile = ''
        self._dl_links = Queue.Queue()
        self._msg = None
        self._status = INIT
        self._run = True
        self._lock = threading.RLock()
        self._dl_count = 0
        self._repeated = repeated
        self._successful_links = []
    
    def add(self, link):
        "Adds link to packet."
        
        self._lock.acquire()
        try:
            if link in self._links:
                return False
            else:
                if self._firstfile == '':
                    self._firstfile = FILENAME_RE.search(link).group(1)
                
                self._links.append(link)
                self._dl_links.put(link)
                return True
        finally:
            self._lock.release()
    
    def has_name(self, name):
        
        self._lock.acquire()
        try:
            return (self._name == name)
        finally:
            self._lock.release()
    
    def status(self):
        "Get status line message."
        
        self._lock.acquire()
        try:
            text = self._name + " {files: %d/%d " % (self._dl_count, 
                                                     len(self._links))
            if self._repeated:
                text += ", vielleicht wurde die Datei schonmal runtergeladen?"
            if self._msg:
                text += (", %s " % self._msg)
            text += (", status: %s}" % self._status)
            
            if not self._run:
                text += " killed packet must be reset..."
            
        finally:
            self._lock.release()
        
        return text
    
    def set_waiting(self):
        "Tries to set status to wait."
        
        self._lock.acquire()
        try:
            if self._status in (WAITING, LOADING, DOWNLOADED, EXTRACTING, FINISHED):
                return False
            else:
                self._status = WAITING
                return True
        finally:
            self._lock.release()
    
    def reset(self, force=False):
        "Just resets status to default..."
        
        self._lock.acquire()
        try:
            if self._status in (FINISHED, ERROR, KILLED):
                
                self._status = INIT
                self._run = True
                self._dl_links = Queue.Queue()
                
                if force:
                    self._successful_links = []
                    self._dl_count = 0
                else:
                    self._dl_count = len(self._successful_links)
                
                for link in self._links:
                    if not (link in self._successful_links):
                        self._dl_links.put(link)
                
                return True
                    
        finally:
            self._lock.release()
        
        return False
    
    def is_finished(self):
        
        self._lock.acquire()
        try:
            if self._status == FINISHED:
                return True
            else:
                return False
        finally:
            self._lock.release()
    
    def get_name(self):
        "Get packet name."
        
        # lock isn't needed
        self._lock.acquire()
        try:
            return self._name
        finally:
            self._lock.release()
    
    def __has_exceeded(self, filepath):
        
        if os.stat(filepath).st_size < 1000000:
            f = open(filepath)
            try:
                data = f.read()
                if data.find(EXCEED_MSG) >= 0:
                    return True
            finally:
                f.close()
        
        return False
                
    
    def download(self, dl_dir, cookie, *curl_param):
        
        self._lock.acquire()
        try:
            if self._status in (KILLED, LOADING, 
                EXTRACTING, FINISHED, ERROR):
                
                return False
            else:
                self._status = LOADING
                self._msg = None
        finally:
            self._lock.release()
        
        try:
            while 1:
                link = self._dl_links.get(timeout=0)
                filename = FILENAME_RE.search(link).group(1)
                dest = os.path.join(dl_dir, filename)
                
                dl = curl.curl(link, dest, cookie=cookie, args=curl_param)
                status = dl.update()
                
                while status[curl.STATUS_RUNNING]:
                    status = dl.update()
                    self._lock.acquire()
                    try:
                        self._msg = str(status)
                        run = self._run
                    finally:
                        self._lock.release()
                    
                    if not run:
                        dl.kill()
                        self._lock.acquire()
                        try:
                            self._status = KILLED
                        finally:
                            self._lock.release()
                        return False
                    
                    time.sleep(UPDATE_INTERVAL)
                
                if self.__has_exceeded(dest):
                    self._status = ERROR
                    self._msg = "Maybe exceeded the daily limit..."
                    return False
                
                if status[curl.STATUS_RETURN] == 0:
                    self._successful_links.append(link)
                
                self._dl_count += 1
                
        except Queue.Empty:
            pass
        
        self._lock.acquire()
        try:
            self._status = DOWNLOADED
        finally:
            self._lock.release()
        
        return True
    
    def __update_extractor(self, status):
        
        self._lock.acquire()
        try:
            self._msg = str(status)
            if not self._run:
                self._status = KILLED
                raise kill_except.KillException()
        finally:
            self._lock.release()
    
    
    def extract(self, source, dest, pwds):
        
        self._lock.acquire()
        try:
            if self._status in (KILLED, LOADING,
                 EXTRACTING, FINISHED, ERROR):
                
                return False
            else:
                self._status = EXTRACTING
                self._msg = None
        finally:
            self._lock.release()
            
        extr_obj = pfextractor.extractor(source, dest, pwds)
         
        result = extr_obj.extract(self._firstfile, proc = self.__update_extractor)
        
        self._lock.acquire()
        try:
            if self._status == KILLED:
                return False
            
            if result:
                self._status = FINISHED
                return True
            else:
                self._status = ERROR
                return False
        finally:
            self._lock.release()
    
    def kill(self):
        
        self._lock.acquire()
        try:
            self._run = False
        finally:
            self._lock.release()
