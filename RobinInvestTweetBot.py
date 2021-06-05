import tweepy
import robin_stocks.robinhood as r
import pyotp
import time

totp = pyotp.TOTP('').now()
login = r.login('', '', mfa_code = totp)
print("Current OTP:", totp)

consumer_key = ''
consumer_secret = ''

access_key = ''
access_secret = ''

def quote(SYBL):
    sInfo = r.get_latest_price(SYBL)
    return ('$' + SYBL.upper() + ": $" + str(sInfo[0]))

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)

filename = 'LastSeenMentions.txt'

#copied from CS DOJO (twitter bot python video)
def retreive_last_seen_id(file):
    file_read = open(file, 'r')
    last_seen_id = int(file_read.read().strip())
    file_read.close()
    return last_seen_id
#Work on Tweet Retreival

#copied from CS DOJO (twitter bot python video)
def store_last_seen_id(last_seen_id, file):
    file_write = open(file, 'w')
    file_write.write(str(last_seen_id))
    file_write.close()
    return

def reply_quote():
    last_seen_id = retreive_last_seen_id(filename)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode = 'extended')

    print('retrieving and replying...')

    mentions = api.mentions_timeline()
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + str(mention.text))

        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, filename)

        men_txtlst = str(mention.text).split(' ')
        if len(men_txtlst) == 2:
            try:
                status = quote(str(mention.text).split(' ')[1])
                print('found ticker and price...')
                print('posting quote...')
                api.update_status('@' + mention.user.screen_name + ' ' + status, str(mention.id))
            except:
                api.update_status('@' + mention.user.screen_name + ' requested stock ticker does not exist', str(mention.id))

while True:
    reply_quote()
    time.sleep(15)    
#print(r.get_latest_price('SQ'))

#api.update_status(str(status))
