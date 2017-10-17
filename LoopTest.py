import time
import urllib2
import json
import create2api

bot = create2api.Create2()
bot.start()
bot.safe()
lastCommand = "Stop"

parsedResponse = json.loads(response.read())
print parsedResponse
#html = response.read()
print(parsedResponse['Message'])
print(parsedResponse['Command'])

while (1):
    response = urllib2.urlopen("http://natebotapi.azurewebsites.net/api/botmessage")
    parsedResponse = json.loads(response.read())
    print lastCommand
    time.sleep(1)
    
