from flask import Flask, request
import json
import requests
# get the urllib2 library, to fetch the web page
import urllib3
app = Flask(__name__)

PAT = 'EAADNnJuZBxKEBAIZC5Inwjxr8UX7Iu2uE3kmythbsRHeFkOCJSgaynpYpBpNPmrnzngaeZC59ENMEQ7MuxYJuYiwpiPp2QxbMcxMnVMYbKV3PwZAfRkk66QooJRmb4Ohab2Sx4YBQGuyP9jmgxyCaMLYqNV37awokpZBYUa51XAZDZD'

http = urllib3.PoolManager()
r = http.request('GET', 'http://www.tastespotting.com/browse/1')
# import beautifulsoup to parse data
from bs4 import BeautifulSoup

response = requests.post(
    "https://graph.facebook.com/v2.6/me/thread_settings?access_token"+PAT,
    json={
          "setting_type":"call_to_actions",
          "thread_state":"new_thread",
          "call_to_actions": {
            "payload": "USER_DEFINED_PAYLOAD"
        }
    })
response = requests.post(
    "https://graph.facebook.com/v2.6/me/messenger_profile?access_token="+PAT,
    json={
          "persistent_menu":[
                            {
                               "locale":"default",
                               "composer_input_disabled": False,
                               "call_to_actions":[
                                                  {
                                                    "type":"web_url",
                                                    "title":"Latest News",
                                                    "url":"https://www.messenger.com/",
                                                    "webview_height_ratio":"full"
                                                   }
												  ]
                            },
                            {
                               "locale": "zh_CN",
                               "composer_input_disabled": False
                            }
                            ]
                             })
          

@app.route('/', methods=['GET'])
def handle_verification():
  print("Handling Verification.")
  payload = request.get_data()
  print(payload)
  if request.args.get('hub.verify_token', '') == 'recipe-token':
    print("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print("Verification failed!")    
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print("Handling Messages")
  payload = request.get_data()
  print(payload)
  for sender, message in messaging_events(payload):
    print("Incoming from %s: %s" % (sender, message))
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"

def retrieving_data():
    """Send the recipe and increment the counter to send different each time"""
    req = http.request('GET', 'http://www.tastespotting.com/browse/2')
    data = BeautifulSoup(req.data,'html.parser')
    for each_div in data.find_all("div", { "class": "trendspotted-item"}):
        for each_recipe in each_div.find_all('a', href=True):
            print("recipe link :",each_recipe['href'])
            print(each_recipe['href'].startswith('/click'))
            if each_recipe['href'].startswith('/click'):
                retrieving_data.msg=each_recipe['href'][16:-13]
                print("the msg is ----------",retrieving_data.msg[:-13])
            for each_img in each_recipe.find_all('img', alt=True):
                retrieving_data.msg2=each_img['src']
        for each_caption in each_div.find("p", { "class": "photo_caption"}):
            retrieving_data.msg3=each_caption
			
			
def send_message(token, recipient, text):
      """Send the message text to recipient with id recipient.
      """
      print("calling retrieving_data func")
      retrieving_data()
      print("printing msg3 there",retrieving_data.msg3)
      r = requests.post("https://graph.facebook.com/v2.6/me/messages",
      params={"access_token": token},
      data=json.dumps({
        "recipient": {"id": recipient},
        "message":{
                    "attachment":{
                              "type":"template",
                              "payload":{
                              "template_type":"generic",
                              "elements":[
                                         {
                                          "title":retrieving_data.msg3,
                                          "image_url":retrieving_data.msg2,
                                          "buttons":[
                                                    {
                                                      "type": "web_url",
                                                      "title": "Read more!",
                                                      "url": retrieving_data.msg,
                                                    },
                                                    {
                                                      "type":"element_share"
                                                    }              
                                                    ]
                                         }
                                         ]
                                        }
                             }
                           }
                       }),
      headers={'Content-type': 'application/json'})
      if r.status_code != requests.codes.ok:
         print(r.text)

if __name__ == '__main__':
  app.run()