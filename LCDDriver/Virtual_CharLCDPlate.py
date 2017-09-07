#!/usr/bin/python
import pygame

class Virtual_CharLCDPlate():
    NO_TRUNCATE       = 0
    TRUNCATE          = 1
    TRUNCATE_ELLIPSIS = 2

    # Port expander input pin definitions
    SELECT                  = 0 # SPACE
    RIGHT                   = 1
    DOWN                    = 2
    UP                      = 3
    LEFT                    = 4

    # LED colors
    OFF                     = (0, 0, 0)
    RED                     = (255, 0, 0)
    GREEN                   = (0, 255, 0)
    BLUE                    = (0, 0, 255)
    YELLOW                  = (255, 255, 0) #RED + GREEN
    TEAL                    = (0, 255, 255) #GREEN + BLUE
    VIOLET                  = (255, 0, 255) #RED + BLUE
    WHITE                   = (255, 255, 255) #RED + GREEN + BLUE
    ON                      = OFF #RED + GREEN + BLUE

    def __init__(self):
        self.color = (255, 255, 255)
        self.bgcolor = (0, 0, 0)
        
        #pygame.init()
        pygame.display.init()
        pygame.font.init()
        
        
        self.scale = [5*4,  8*4]    # 16x2 zeichen, 4 als skalierung
        self.size =  [16 ,  2  ]       # 5x8 je pixel
        self.screenSize = [a*b for a,b in zip(self.scale,self.size)]   #elementweise multipl
        self.screen = pygame.display.set_mode(self.screenSize)
        self.font = pygame.font.SysFont("monospace", self.scale[1])
        
        self.col = 0
        self.row = 0
        
        self.c1 = list("                ")
        self.c2 = list("                ")

    def write(self, value, char_mode=False):
        """ Send command/data to LCD """
        
    def begin(self, cols, lines):
        self.clear()

    def getBackgroundColor(self):
        return self.bgcolor
        
    def stop(self):
        print("Virtual LCD get shut down...")
        self.clear()
        pygame.quit()
        
    def hasError(self):
        return False
 
    def clear(self):
        self.col = 0
        self.row = 0
        self.screen.fill(self.bgcolor)

    def home(self):
        print("home")
        
    def setCursor(self, col, row):
        self.col = col
        self.row = row
        
    def display(self):
        """ Turn the display on (quickly) """
    def noDisplay(self):
        """ Turn the display off (quickly) """
    def cursor(self):
        """ Underline cursor on """
    def noCursor(self):
        """ Underline cursor off """
    def blink(self):
        """ Turn on the blinking cursor """
    def noBlink(self):
        """ Turn off the blinking cursor """
    def ToggleBlink(self):
        """ Toggles the blinking cursor """
    def scrollDisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
    def scrollDisplayRight(self):
        """ These commands scroll the display without changing the RAM """
    def leftToRight(self):
        """ This is for text that flows left to right """
    def rightToLeft(self):
        """ This is for text that flows right to left """
    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
    def noAutoscroll(self):
        """ This will 'left justify' text from the cursor """

    def createChar(self, location, bitmap):
        return
        #print("char create!?...")

    def message(self, text, truncate=NO_TRUNCATE):
        """ Send string to LCD. Newline wraps to second line"""
        i=0
        while(i<len(text)):
            if text[i] == '\n':
                self.row += 1
                self.row = self.row % 2
                self.col = 0
                i += 1
                continue
            if self.col >= len(self.c1):
                i += 1
                continue
            if self.row == 0:
                self.c1[self.col] = text[i]
            if self.row == 1:
                self.c2[self.col] = text[i]
                
            self.col += 1
            i += 1
        self.update()
        
    def processText(self,  text):
        
        # 00 : Grad-Symbol          \x00    \xdf   (mehr eckig)
        # 01 : heizen               \x01
        # 02 : kuehlen              \x02
        # 03 : Wahlmglk. oben/unten \x03
        # 04 : ok (pfeil rechts)    \x04    \x7e
        # 05 : setting              \x05
        # 06 : wenig heizen         \x06    \x5e
        # 07 : s-z Umlaut           \x07    
        #if len(text) == 0:
        #    return ' '
        if ord(text) == 0:
            return chr(176)
        if ord(text) == 1:
            return chr(8593)
        if ord(text) == 2:
            return b'\xe2\x86\x92'.decode("utf-8", "strict") 
            #return chr(8594)
        if ord(text) == 3:
            return b'\xe2\x86\x95'.decode("utf-8", "strict") 
            #return chr(8597)
        if ord(text) == 4: # pfeil rechts
            return chr(187)     # evtl 707 (>)
        if ord(text) == 5:
            return chr(1421)
        if ord(text) == 6:
            return chr(8599)
        if ord(text) == 7:
            return chr(223)
            
        if ord(text) == 225:
            return chr(228) # ae
        if ord(text) == 239:
            return chr(246) # oe
        if ord(text) == 245:
            return chr(252) # ue
            
        return text
                
    def update(self):
        #self.screen.get_rect(self.screenSize).fill(self.bgcolor)
        pygame.draw.rect(self.screen, self.bgcolor, (0,0,self.screenSize[0],self.screenSize[1]))
        
        text = list(self.c1) # vs. text = ''.join(text)
        text2 = list(self.c2) # vs. text = ''.join(text)
        
        i = 0
        while(i<len(text)):
                
            if len(text[i]) != 0:
                text[i] = self.processText(text[i])
                line = self.font.render(text[i],  2,  self.color)
                self.screen.blit(line,  (i * 5*4, 0))    #c1
                
            i += 1
                
        i = 0
        while(i<len(text2)):
                
            if len(text2[i]) != 0:
                text2[i] = self.processText(text2[i])
                line2 = self.font.render(text2[i],  2,  self.color)
                self.screen.blit(line2,  (i * 5*4, 8*4))  #c2
                
            i += 1
        pygame.display.update()
        #pygame.display.flip()

    def backlight(self, color):
        self.bgcolor = color
        print("backlight", color)

    # Read state of single button
    def buttonPressed(self, b):
            
        pygame.event.pump()
        if( b == self.UP and pygame.key.get_pressed()[pygame.K_UP] != 0 ):
            #print("up pressed")
            return True
        if(b == self.DOWN and pygame.key.get_pressed()[pygame.K_DOWN] != 0 ):
            #print("dwn pressed")
            return True              
        if( b == self.LEFT and pygame.key.get_pressed()[pygame.K_LEFT] != 0 ):
            return True
        if( b == self.RIGHT and pygame.key.get_pressed()[pygame.K_RIGHT] != 0 ):
            return True
        if( b == self.SELECT and pygame.key.get_pressed()[pygame.K_SPACE] != 0 ):
            return True
            
        return False
        #return (self.i2c.readU8(self.MCP23017_GPIOA) >> b) & 1

    # Read and return bitmask of combined button state
    def buttons(self):
            
        return False
        #return self.i2c.readU8(self.MCP23017_GPIOA) & 0b11111
