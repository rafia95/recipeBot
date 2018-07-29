from flask import Flask, request
import json
import requests
import random
# get the urllib2 library, to fetch the web page
import urllib3
app = Flask(__name__)

PAT = 'EAADJQYB3nKABAK2F9MCFRG86MOEcNlQ2Nbm7TSPmWvZA9ZAx4xQ4nrLIiVzVY9Qf9FYKeEuE5NkNOWmk64bd2EYVCixlqbdBLKOELZANtfZARcG2NXLrQD9lawAkDAXZBTLnd2yM3Ux9rTYrv95W0KAuNFciYvL1ZCie3DeTipswZDZD'
http = urllib3.PoolManager()
# import beautifulsoup to parse data
from bs4 import BeautifulSoup
response = requests.post("https://graph.facebook.com/v2.6/me/thread_settings?access_token="+PAT,
   json={ 
          "setting_type":"call_to_actions",
		  "thread_state":"new_thread",
		  "call_to_actions":[
                             {"payload":"GET_STARTED_PAYLOAD"
                             }
							]
        })

response = requests.post(
    "https://graph.facebook.com/v2.6/me/messenger_profile?access_token="+PAT,
    json={
          "persistent_menu":[
                            {
                               "locale":"default",
                               "composer_input_disabled": True,
                               "call_to_actions":[
                                                  {
                                                    "type":"postback",
                                                    "title":"More Recipes",
                                                    "payload":"send_recipe_payload",
                                                    "webview_height_ratio":"full"
                                                   }
												  ]
                            },
                            {
                               "locale": "zh_CN",
                               "composer_input_disabled": True
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
    send_message( sender)
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
     elif "postback" in event and "payload" in event["postback"]:
        yield event["sender"]["id"], event["postback"]["payload"].encode('unicode_escape')
     else:
       yield event["sender"]["id"], "I can't echo this"

def retrieving_data():
    """Send the recipe and increment the counter to send different each time"""
    for x in range(1):
       page_number=random.randint(1,500)
    print("page_num is ",page_number)
    page_num=str(page_number)
    print("str version is ",page_num)
    url = 'http://www.tastespotting.com/browse/'+page_num
    print("url ",url)
    req = http.request('GET', url)
    data = BeautifulSoup(req.data,'html.parser')
    for each_div in data.find_all("div", { "class": "trendspotted-item"}):
        for each_recipe in each_div.find_all('a', href=True):
            """links starting with /clicks are the links of recipe to their original sites, so just retrieve those links"""
            if each_recipe['href'].startswith('/click'):
                retrieving_data.recipe_link=each_recipe['href'][16:-12]
               # print("the recipe_link is ----------",retrieving_data.recipe_link,each_recipe['href'])
            for each_img in each_recipe.find_all('img', alt=True):
                retrieving_data.msg2=each_img['src']
        for each_caption in each_div.find("p", { "class": "photo_caption"}):
            retrieving_data.msg3=each_caption
 
			
def send_message( recipient):
      """Send the message text to recipient with id recipient.
      """
      print("calling retrieving_data func")
      retrieving_data()
      r = requests.post("https://graph.facebook.com/v2.6/me/messages",
      params={"access_token": PAT},
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
                                                      "url": retrieving_data.recipe_link,
                                                    }              
                                                    ]
                                         }
                                         ]
                                        }
                             }
                           }
                       }),
      headers={'Content-type': 'application/json'})
     # if r.status_code != requests.codes.ok:
     #    print(r.text)

if __name__ == '__main__':
  app.run()