import os
import gc
import sys
import argparse
import json

from requests_oauthlib import OAuth1Session, oauth1_session
from urllib.parse import parse_qsl
from multiprocessing import Process


def delete_tweets(tweets: list, oauth: OAuth1Session):
    url = "https://api.twitter.com/1.1/statuses/destroy/"

    for i in range(len(tweets)):
        try:
            res = oauth.post(url + tweets[i] + ".json")

            if res.status_code == 200:
                print(f"ID: {tweets[i]} deleted")
            else:
                print(f"ID: {tweets[i]} | failed")

        except IndexError:
            pass


CLIENT_KEY = "CLIENT_KEY"
CLIENT_SECRET = "CLIENT_SECRET"

parser = argparse.ArgumentParser(description="Twitter archive eraser")

parser.add_argument(
    "--file",
    type=str,
    default="./tweet.js",
    help="Input file. Look for the tweet.js file under the archive's data folder.",
)
parser.add_argument(
    "--threads",
    type=int,
    default=32,
    help="How many threads to run. 32 is default, max to 64.",
)

args = parser.parse_args()

if args.threads > 64:
    args.threads = 64

archive = open(args.file, "rt", encoding="utf-8")
archive.seek(25)
tweets = json.loads(archive.read())
archive.close()

tweet_ids = []

for i in range(len(tweets)):
    tweet_ids.append(tweets[i]["tweet"]["id_str"])

del archive
del tweets

gc.collect()

if __name__ == "__main__":

    workload = []
    workload_size = len(tweet_ids) // args.threads

    for i in range(args.threads):
        workload.append(tweet_ids[i * workload_size : (i + 1) * workload_size])

    token_request = OAuth1Session(
        client_key=CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri="oob"
    )
    res = token_request.post("https://api.twitter.com/oauth/request_token")
    tokens = dict(parse_qsl(res.text))

    os.system(
        f"start \"\" https://api.twitter.com/oauth/authorize?oauth_token={tokens['oauth_token']}"
    )

    sys.stdout.write("Enter the PIN code: ")
    pin_code = str(input())

    res = token_request.post(
        f"https://api.twitter.com/oauth/access_token",
        params={"oauth_token": tokens["oauth_token"], "oauth_verifier": pin_code},
    )

    credentials = dict(parse_qsl(res.text))

    account_session = OAuth1Session(
        client_key=CLIENT_KEY,
        client_secret=CLIENT_SECRET,
        resource_owner_key=credentials["oauth_token"],
        resource_owner_secret=credentials["oauth_token_secret"],
    )

    print(f"\nHello {credentials['screen_name']}.")
    print(
        f"You have {len(tweet_ids)} tweets. Delete now? (enter y / yes to go ahead, n / other to exit.)\n"
    )

    answer = input()

    if answer.lower() == "y" or answer.lower() == "yes":
        pass
    else:
        sys.exit()

    print("\n\nDeleting now.")

    for i in range(args.threads):
        Process(
            target=delete_tweets,
            args=(
                (
                    workload[i],
                    account_session,
                )
            ),
        ).start()

    Process(
        target=delete_tweets,
        args=(
            (
                tweet_ids[args.threads * workload_size :],
                account_session,
            )
        ),
    ).start()
