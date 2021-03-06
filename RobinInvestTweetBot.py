from robin_stocks import robinhood as r
import pyotp
import time
import tweepy

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

def stored_ids(file):
    file_read = open(file, 'r')
    ids = (file_read.readlines())[0].split(',')
    file_read.close()
    
    print('returning ids')
    return ids
#Work on Tweet Retreival

def store_new_id(latest_id, file):
    file_write = open(file, 'a')
    file_write.write(',' + str(latest_id))
    file_write.close()
    print('adding id')
    return

def reply_quote():
    stored = stored_ids(filename)
    #mentions = api.mentions_timeline(last_seen_id, tweet_mode = 'extended')

    print('retrieving and replying...')

    mentions = api.mentions_timeline()
    for mention in reversed(mentions):
        mention_id = str(mention.id)
        #print('mention_id: ' + str(mention_id))
        #print('stored ids: ' + str(stored))
        if mention_id not in stored:
            print('mention_id not in stored')
            print(str(mention.id) + ' - ' + str(mention.text))

            last_seen_id = mention.id
            store_new_id(last_seen_id, filename)

            men_txtlst = str(mention.text).split(' ')
            if len(men_txtlst) == 2:
                SYBL = str(mention.text).split(' ')[1]
                image_today(SYBL)
                status = quote(SYBL)
                if status != None:
                    print('found ticker and price...')
                    print('posting quote...')
                    
                    print('uploading...')
                    api.update_with_media('C:\\Users\\kkama\\OneDrive\\Documents\\RobinInvestImages\\image.png', 
                        '@' + mention.user.screen_name + ' ' + status, 
                        in_reply_to_status_id = str(mention.id))
                    print('finished uploading.')
                else:
                    api.update_status('@' + mention.user.screen_name + ' requested stock ticker does not exist', str(mention.id))
            if len(men_txtlst) == 3 and (str(mention.text).split(' ')[2] == '3m'):
                SYBL = str(mention.text).split(' ')[1]
                image_3m(SYBL)
                status = quote(SYBL)
                if status != None:
                    print('found ticker and price...')
                    print('posting quote...')
                    
                    print('uploading...')
                    api.update_with_media('C:\\Users\\kkama\\OneDrive\\Documents\\RobinInvestImages\\image.png', 
                        '@' + mention.user.screen_name + ' ' + status, 
                        in_reply_to_status_id = str(mention.id))
                    print('finished uploading.')
                else:
                    api.update_status('@' + mention.user.screen_name + ' requested stock ticker does not exist', str(mention.id))

def tweet_quote_image(SYBL):
    image_today(SYBL)
    status = quote(str(SYBL).split(' ')[0])
    media = api.update_with_media('C:\\Users\\kkama\\OneDrive\\Documents\\RobinInvestImages\\image.png', status)

#while True:
#    reply_quote()
#    time.sleep(15)

tweet_quote_image('COIN')
#print(r.get_latest_price('SQ'))

##Find earnings call date for some companies and post price day after
                    
while True:
    reply_quote()
    time.sleep(10) #shouldn't exceed 5 or else runs out of requests

#api.update_status(str(status))
