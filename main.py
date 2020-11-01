import twitter
import configparser
from time import sleep
from video_controller import VideoPlayer 
from secret_sanitizer import sanitize_url
import requests
import traceback
'''
Useful props:

status.id_str : unique ID (track duplicates)
status.text : raw text of tweet
status.favorite_count : number of likes (sort by most popular)
status.user.screen_name : text of username
'''


class TwitterAPI:

    class Credentials:
        def __init__(self):
            config = configparser.RawConfigParser()   
            config.read(r'twitter_auth.txt')
            self.api_key = config.get('twitter', 'API_KEY')
            self.api_secret = config.get('twitter', 'SECRET_KEY')
            self.access_token = config.get('twitter', 'ACCESS_TOKEN')
            self.access_secret = config.get('twitter', 'ACCESS_TOKEN_SECRET')

    def __init__(self):
        creds = TwitterAPI.Credentials()
        self.api = self.setup_api(creds)
        try:
            with open('latest.tweet') as f:
                line = f.readline()
                if len(line) > 0:
                    self.latest_mention = line
                else: raise Exception
        except:
            self.latest_mention = None

    def setup_api(self, creds):
        return twitter.Api(
            consumer_key=creds.api_key,
            consumer_secret=creds.api_secret,
            access_token_key=creds.access_token,
            access_token_secret=creds.access_secret
        )

    def update_latest_mention(self, tweet_id):
        self.latest_mention = tweet_id
        with open("latest.tweet", "w+") as f:
            f.write(tweet_id)
            f.close()

    def get_new_mentions(self):
        results = self.api.GetMentions(since_id=self.latest_mention)
        if len(results) > 0:
            id = results[0].id_str
            self.update_latest_mention(id)
        return results

def main():
    api = TwitterAPI()
    video = VideoPlayer()
    print("Bot is ready. Searching for tweets...")
    while True:
        try:
            results = api.get_new_mentions()
        except:
            traceback.print_exc()
            print("API Request failed. Trying again...")
            print("If this keeps happening, login may be failing.")
        if results:
            for status in results:
                try:
                    text = status.text
                    url = None
                    print(text)
                    for good_url in ['youtube.com', 'youtu.be', 't.co']:
                        if good_url in text:
                            print("got good url")
                            try:
                                # Clean tweet with secret sauce
                                url = sanitize_url(text, good_url)
                                # Video must meet certain content criteria
                                if video.is_valid(url):
                                    print("video is valid")
                                    video.playlist.add_to_queue(url)
                                    if not video.is_playing():
                                        video.play_next_if_ready()
                            except:
                                print("Failed to load to queue (or play first video). Skipping video...")
                                continue
                except:
                    print("Loop iteration failed somewhere.")
                    print("Skipping result...")
        try:
            sleep(1)
            video.play_next_if_ready()
            sleep(8)
        except KeyboardInterrupt:
            return
        except:
            print("Failed to play video, skipping...")
            continue

if __name__ == "__main__":
    main()