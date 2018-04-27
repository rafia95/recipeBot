from flask import Flask, request
import json
import requests
# get the urllib2 library, to fetch the web page
import urllib3
app = Flask(__name__)

PAT = 'EAAFDVWHFI8gBAO66TFhEEzhO3hgCeJcR4Mbl6uFZAAGED2asUFUDlSoDYQliguJQHzQQ1bUPKNB1KP9ZCbZCDbNc6ouUfTzaYJqJk7ne5XSohgxnjT6zV31MFYtyBnJIpcbl3jqAUQbZAcOzZB2XIJgl5ySRatxiPwZAjZADLmHNAZDZD'

http = urllib3.PoolManager()
r = http.request('GET', 'http://www.tastespotting.com/browse/2')
# import beautifulsoup to parse data
from bs4 import BeautifulSoup



@app.route('/', methods=['GET'])
def handle_verification():
  print("Handling Verification.")
  payload = request.get_data()
  print(payload)
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
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


def send_message(token, recipient, text):
    """Send the message text to recipient with id recipient.
    """
    r = http.request('GET', 'http://www.tastespotting.com/browse/2')
    msg=""
    data = BeautifulSoup(r.data,'html.parser')
    for each_div in data.find_all("div", { "class": "trendspotted-item"}):
        for each_recipe in each_div.find_all('a', href=True):
            print("recipe link :",each_recipe['href'])
            reclink="",each_recipe['href']
            if reclink.startswith("/clicks")
                msg=each_recipe['href']
                print("the msg is ----------",msg)
            for each_img in each_recipe.find_all('img', alt=True):
                print(each_img['src'])
        for each_caption in each_div.find("p", { "class": "photo_caption"}):
            print("......", each_caption)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
      params={"access_token": token},
      data=json.dumps({
        "recipient": {"id": recipient},
        "message": {"text": msg}
      }),
      headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
      print(r.text)

if __name__ == '__main__':
  app.run()