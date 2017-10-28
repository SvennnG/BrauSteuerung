from http.client import HTTPSConnection
from base64 import b64encode
import ssl

import urllib.parse

def SendToDB(temp, zieltemp, time, first):
    #This sets up the https connection
    c = HTTPSConnection("brau.gesper-web.de")
    #we need to base 64 encode it 
    #and then decode it to acsii as python 3 stores it as a byte string
    userAndPass = b64encode(b"brauer:Seelze!Bier").decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass }
    #then connect


    temp = urllib.parse.quote_plus(temp)
    time = urllib.parse.quote_plus(time)
    zieltemp = urllib.parse.quote_plus(zieltemp)
    first = urllib.parse.quote_plus(first)

    print("Send to Web, First: %s." % first, end='\n', flush=True)
    url = '/admin/addToDB.php?temp='+temp+'&time='+time+'&zieltemp='+zieltemp+'&first='+first

    #print(url)

    c.request('GET', url, headers=headers)

    #get the response back
    res = c.getresponse()
    # at this point you could check the status etc
    # this gets the page text
    status = res.status

    if status != 200:
        print("Error sending to DB!: %s" % status, flush=True)
        #return print("Error sending to DB!:", status);
    else:
        print(" Success! ", end='', flush=True)
        
    #data = res.read() 
    #print(data)

if __name__ == "__main__":

    temp = "%.2f" % 64.4
    time = "2017-10-11 04:20:20"
    zieltemp = "%.2f" % 60
    first = "0"
    
    SendToDB(temp, zieltemp, time, first);
