#!/usr/bin/env python3
# coding: utf-8
import argparse, sys, signal
import json
import time
from random import randrange as rand
import _thread

import selenium.common.exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

def perror(fmt, *args): print(fmt, *args, file=sys.stderr);

class Driver():
    def __init__ (self, args, headless = False):
        # instance options
        self.options = Options()
        self.options.headless = headless
        [self.options.add_argument(a) for a in args]
    
        #print(repr(self.options.arguments))
    
        self.instance = Chrome('./chromedriver', options=self.options)

class imnothere:
    _interval   = 10
    _threads    = None
    _nthreads   = 5
    _opened     = []

    class ErrException(Exception):
        def __init__ (self, m):
            perror(m)
            pass

    def getdriver(self, config):
        driver = Driver(
                (None if 'arguments' not in config else config['arguments']),
                headless = (False if 'headless' not in config else
                config['headless'])
            )
        return driver.instance

    def _new_tab(self, n, url):
        self.driver.switch_to.window(self.driver.window_handles[0]) 
        self.driver.execute_script("window.open('','','')")
        
        handle = self.driver.window_handles[len(self.driver.window_handles)-1]
        print("opening tab %s" % handle) 
        self.driver.switch_to.window(handle)
        self.driver.get(url)
        return handle

    def _close_tab(self, w):
        if len(self.driver.window_handles) <= 1:
            return None
        i = 1
        for handle in self.driver.window_handles[1:]:
            if handle == w:
                print("closing %i %s" % (i,w))
                self.driver.switch_to.window(self.driver.window_handles[i])
                #self.driver.execute_script('window.close();')
                self.driver.close()
                break
            i+=1

    def new_activity(self, n, activity):
        # record opened URL
        if activity['url'] not in self._opened:
            self._opened.append(activity['url'])
        else:
            # check if URL should be opened once
            if 'once' in activity and activity['once'] == True:
                return None
        
        window = self._new_tab(n, activity['url'])

        # action on page
        if 'action' in activity:
            action = activity['action']
            if action.startswith('js:'):
                js_path = action[action.index(':')+1:]
                try:
                    js = open(js_path, 'r').read()
                    self.driver.execute_script(js)
                except Exception as e:
                    print(e)
                    self._close_tab(window)
                    pass
            elif action.startswith('work:'):
                work_path = action[action.index(':')+1:]
                try:
                    work = open(work_path, 'r').read()
                    while exec(work, {'driver': self.driver, 'Keys': Keys}):
                        pass
                except Exception as e:
                    print(e)
                    self._close_tab(window)
                    pass

        # if standby number starts with ~ then it will be a random time within
        # that range of seconds
        if 'standby' in activity:
            standby = activity['standby']
            
            if standby.startswith('~'):
                standby = rand(1, int(standby[1:]))
            print("sleeping {}".format(standby))
            time.sleep(int(standby))
            self._close_tab(window)
       
        self._opened.append(activity['url'])
        self._nthreads+=1

    def start(self):
        # parse config
        try:
            c = open(self.config_path, 'r').read()
            self.config = json.loads(c)

            if 'interval' not in self.config:
                self.config['interval'] = self._interval
        except Exception as e:
            raise self.ErrException(e)
        
        if len(self.config['urls']) == 0:
            raise self.ErrException('No URLs set.')
        self.driver = self.getdriver(self.config)

        try:
            while True:
                urls_n = len(self.config['urls'])
                
                url = self.config['urls'][rand(urls_n)]
                
                try: 
                    while self._nthreads == 0:
                        pass
                    self._nthreads-=1
                    _thread.start_new_thread( self.new_activity,
                        (self._nthreads, url,) )
                except selenium.common.exceptions.NoSuchWindowException:
                    # window was closed?
                    break
                time.sleep(rand(3,self.config['interval'])) # from >3
        except KeyboardInterrupt as k:
            raise self.ErrException(k)
            pass

        return None

    def __init__(self, path):
        self.config_path = path

def parseargs(args):
    parser = argparse.ArgumentParser(description = 'Network white noise.')
    parser.add_argument('--config', help='config JSON', type=str)
    if len(args) < 2:
        parser.print_help()
        return None

    a = parser.parse_args()
    inh = imnothere(a.config)
    return inh

def main():
    inh = parseargs(sys.argv)
    if not inh:
        return 1

    # start
    try:
        inh.start()
    except inh.ErrException:
        inh.driver.quit()
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
