#!/usr/bin/python

import time
import threading
import logging
import curses
import sys

class StdOutWrapper:
    text = ""
    fifoText = [""]
    anzahlFIFO = 16
    logger = logging.getLogger('Maischen')

    def write(self,txt):
        if not txt:
            return
        if txt.lstrip().rstrip('\n'):
            try:
                #txt3 = txt.decode("utf-8", "ignore")
                self.logger.info(txt.lstrip().rstrip('\n'))
                #txt2 = txt.decode("utf-8", "strict")
            except Exception as e:
                self.logger.warning("Log Error!")
        self.text += txt
        self.text = '\n'.join(self.text.split('\n')[-self.anzahlFIFO:])  #limit to 30
        
    def getText(self):
        return self.text
        
    def get_text(self,beg,end):
        return '\n'.join(self.text.split('\n')[beg:end])
        
    def lineCount(self):
        return self.text.count('\n')
        
    def flush(self):
        self.clear()
    
    def clear(self):
        self.text = ""
        
    def addFIFOLines(self, lines):
        lines = list(lines)
        if len(lines) > 0:
            for i in range(0, len(lines)):                          # old to new
                msg = lines[i]
                if msg != "":
                    self.fifoText.append(msg)                       # append the msg
                    if len(self.fifoText) > self.anzahlFIFO:
                        self.fifoText.pop(0)                        # drop oldest
        return self.fifoText
        
class Console(threading.Thread):
    def __init__(self,  mystdout = 0):
        threading.Thread.__init__(self)
        self.running=True
        self.logger = logging.getLogger('Maischen')
        
        if type(mystdout) is StdOutWrapper:
            self.mystdout = mystdout
            sys.stdout = self.mystdout
            sys.stderr = self.mystdout 

            self.stdscr = curses.initscr()
            curses.noecho()             # no print of pressed keys
            curses.cbreak()             # no line-buffer
            curses.curs_set(0)          # no blinking curser
            #stdscr.keypad(1)            # Escape-Sequenzen activated

            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

            #stdscr.bkgd(curses.color_pair(1))
            #stdscr.refresh()

            self.win_MAXLINES = 20
            self.win_MAXCOLS = 100
            self.win = curses.newwin(self.win_MAXLINES, self.win_MAXCOLS)            # lines, cols
            self.win.bkgd(curses.color_pair(2))          # Farbpaar YELLOW/Black
            self.win.box()                               # Rahmen

            self.win.refresh()
            self.updateInterval = 250 # in ms
            
        else:
            self.mystdout = 0
            self.updateInterval = 1000 # in ms
            
        self.temp = 0.0
        
        print("#Console initialized")
        
    def run(self):
        #cnt = 0
        while self.running:
            lastUpdate = int(round(time.time() * 1000))
            
            if self.mystdout != 0:
                self.win.box()                            # Rahmen
                
                t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                tempstring = t + " @ %.2f C" % self.temp
            
                self.win.addstr(1, 2, tempstring)
                self.win.clrtoeol()
                
                lines = self.mystdout.getText().split('\n')
                
                #if len(lines) > 0:
                #    lines = self.mystdout.addFIFOLines(lines)
                #    
                #lines = self.mystdout.fifoText
                
                # std output ab line 3
                for i in range(0, len(lines)):
                    if i < self.win_MAXLINES - 3:
                        if len(lines[i]) < self.win_MAXCOLS:
                            self.win.addstr(i + 3, 2, lines[i])            # print to line, col
                            self.win.clrtoeol()
                        else:
                            msg = lines[i]
                            self.win.addstr(i + 3, 2, msg[0:self.win_MAXCOLS-5]+'...')
                            self.win.clrtoeol()
                    else:
                        print(lines[i])
                    
                self.win.refresh()
                
            else:   # std console
                
                if (self.temp != -1.0):
                    t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    print ("\r\x1b[K", end=''),
                    print ("%s @ %.2f C " % (t, self.temp), end='', flush=True)
                
            while int(round(time.time() * 1000)) < lastUpdate + self.updateInterval:
                time.sleep(0.05)
        self.quit()
        
    def quit(self):
        
        if self.mystdout != 0:
            curses.nocbreak()
            #self.stdscr.keypad(0)
            curses.echo()
            curses.endwin()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            sys.stdout.write(self.mystdout.getText())
            self.logger.info("Conosle quit!\nRest gets printed....:")
            self.logger.info(self.mystdout.getText())
        
