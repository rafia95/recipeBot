from flask import Flask, request
import json
import requests
import random
# get the urllib2 library, to fetch the web page
import urllib3
import hashlib
import hmac
app = Flask(__name__)

PAT = 'EAADJQYB3nKABAK2F9MCFRG86MOEcNlQ2Nbm7TSPmWvZA9ZAx4xQ4nrLIiVzVY9Qf9FYKeEuE5NkNOWmk64bd2EYVCixlqbdBLKOELZANtfZARcG2NXLrQD9lawAkDAXZBTLnd2yM3Ux9rTYrv95W0KAuNFciYvL1ZCie3DeTipswZDZD'
http = urllib3.PoolManager()
# import beautifulsoup to parse data
from bs4 import BeautifulSoup
""" post call to display the GET STARTED button in the messenger"""
response = requests.post("https://graph.facebook.com/v2.6/me/thread_settings?access_token="+PAT,
   json={ 
          "setting_type":"call_to_actions",
		  "thread_state":"new_thread",
		  "call_to_actions":[
                             {"payload":"GET_STARTED_PAYLOAD"
                             }
							] 
        })
""" post call for displaying the greeting text"""
response = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile?access_token="+PAT,
   json={ 
          "setting_type":"greeting",
		  "greeting":[
                             {"locale":"default",
                              "text":"A Recipe a Day offers recipes taken from food site TasteSpotting.com and makes it easier for you to cook different meals"
                             }
							]
        })
""" post call to set up the menu,
    and to disable the user input for now, since its not needed"""
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
                                                    "title":"Get a Recipe",
                                                    "payload":"send_recipe_payload",
                                                    "webview_height_ratio":"full"
                                                   }
												  ]
                            },
                            {
                               "locale": "zh_CN",
                            }
                            ]
                             })
          
""" get request to verify the messenger application token """
@app.route('/', methods=['GET'])
def handle_verification():
  print("Handling Verification.")
  if request.args.get('hub.verify_token', '') == 'recipe-token':
    print("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print("Verification failed!")    
    return 'Error, wrong validation token'
""" This method verifies that the request is coming from facebook,
    calls another method to send a response to user """
@app.route('/', methods=['POST'])
def handle_messages():
  print("Handling Messages")
  payload = request.get_data()
  appkey = b'bca6c5f1a8d5d5eb0ca744fe04528b84'
  digester = hmac.new(appkey,payload,hashlib.sha1)
  generated_signature = "sha1="+digester.hexdigest()
  signature = request.headers.get("X-Hub-Signature")
  if signature == generated_signature:
     #Request is coming from facebook
     for sender, message in message_events(payload):
        send_message( sender,message)
     return "ok"
  else: 
     #Request not from facebook as signatures dont match
     return "Bad Request"
""" This method returns the user id and the received message """
def message_events(payload):
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
     if "message" in event and "text" in event["message"]:
        yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
     elif "postback" in event and "payload" in event["postback"]:
        yield event["sender"]["id"], event["postback"]["payload"].encode('unicode_escape')
     else:
       yield event["sender"]["id"], "I can't echo this"   
""" This method sends the recipe response to the user """
def send_message( recipient,payload):
      """Send the message text to recipient with id recipient.
      responds with a custom text message to get started payload
      """
      if payload.decode("utf-8") == "GET_STARTED_PAYLOAD":
       r = requests.post("https://graph.facebook.com/v2.6/me/messages",
       params={"access_token": PAT},
       data=json.dumps({
         "recipient": {"id": recipient},
         "message":{
                     "text":"Welcome to Recipes page. You can get different recipes here to make ur cooking more fun"
                            }
                        }),
       headers={'Content-type': 'application/json'})
      else:
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
                                           "title":retrieving_data.recipe_title,
                                           "image_url":retrieving_data.recipe_image,
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


""" this method retrieves the recipe data from the tastespotting.com website"""
def retrieving_data():
    """Send the recipe and increment the counter to send different each time"""
    for x in range(1):
       page_number=random.randint(1,500)
    page_num=str(page_number)
    url = 'http://www.tastespotting.com/browse/'+page_num
    req = http.request('GET', url)
    data = BeautifulSoup(req.data,'html.parser')
    for each_div in data.find_all("div", { "class": "trendspotted-item"}):
        for each_recipe in each_div.find_all('a', href=True):
            """links starting with /clicks are the links of recipe to their original sites, so just retrieve those links"""
            if each_recipe['href'].startswith('/click'):
                retrieving_data.recipe_link=each_recipe['href'][16:-12]
            for each_img in each_recipe.find_all('img', alt=True):
                retrieving_data.recipe_image=each_img['src']
        for each_caption in each_div.find("p", { "class": "photo_caption"}):
            retrieving_data.recipe_title=each_caption
 
			


if __name__ == '__main__':
  app.run()