# -*- coding: utf-8 -*-

import os
import gc
import sys
import json
import re
import zipfile
import threading
import webbrowser

from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl


def delete_tweets(tweets: list, oauth: OAuth1Session):
    url = "https://api.twitter.com/1.1/statuses/destroy/"

    for tweet in tweets:
        try:
            res = oauth.post(url + tweet + ".json")

            if res.status_code == 200:
                print(f"ID: {tweet} deleted")
            else:
                print(f"ID: {tweet} | failed")

        except IndexError:
            pass


def exit_procedure(error_msg):
    print(error_msg)
    print('To exit, please press enter.')
    input()
    sys.exit()


if __name__ == "__main__":
    try:
        zipFile = sys.argv[1]
    except IndexError:
        exit_procedure("Please drag & drop the zip file downloaded from Twitter.")

    targetFiles = []
    targetFileRegex = re.compile(r'tweet[s]?\..*js.*')

    if not zipfile.is_zipfile(zipFile):
        exit_procedure('Provided file is probably not a zip file.')

    try:
        zipFile = zipfile.ZipFile(zipFile)
    except FileExistsError:
        exit_procedure('Zip file does not exist.')

    try:
        if not zipFile.getinfo('data/').is_dir():
            raise RuntimeError('Provided zip file does not contain data/ folder.')
    except (RuntimeError, KeyError):
        exit_procedure('The zip file does not have path data/.')

    zipPath = zipfile.Path(zipFile, 'data/')

    for item in zipPath.iterdir():
        if targetFileRegex.fullmatch(item.name):
            targetFiles.append(item)

    CLIENT_KEY = "CLIENT_KEY"
    CLIENT_SECRET = "CLIENT_SECRET"
    WORKER_COUNT = 32

    tweet_ids = []

    for file in targetFiles:   
        archive = file.open(mode = 'r', encoding = 'utf-8')
        archive.seek(re.compile(r'.*= ').search(archive.readline()).end())
        tweets = json.loads(archive.read())
        archive.close()

        for i in range(len(tweets)):
            tweet_ids.append(tweets[i]["tweet"]["id_str"])

    zipFile.close()

    del archive
    del tweets

    gc.collect()

    token_request = OAuth1Session(
        client_key=CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri="oob"
    )
    res = token_request.post("https://api.twitter.com/oauth/request_token")
    tokens = dict(parse_qsl(res.text))

    webbrowser.open(f"https://api.twitter.com/oauth/authorize?oauth_token={tokens['oauth_token']}")

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
    print("How many workers do you want to use? Defaults to 32 workers. (Recommended)")
    
    try:
        temp_val = int(input())
    except ValueError:
        temp_val = 32
    
    WORKER_COUNT = temp_val if temp_val > 0 else 32

    if not tweet_ids:
        exit_procedure("No tweets were found inside the provided archive.")

    workload = []
    worker_target = min(WORKER_COUNT, len(tweet_ids))
    worker_target = max(1, worker_target)
    base_chunk = len(tweet_ids) // worker_target
    remainder = len(tweet_ids) % worker_target
    start = 0

    for worker_index in range(worker_target):
        size = base_chunk + (1 if worker_index < remainder else 0)
        workload.append(tweet_ids[start : start + size])
        start += size

    print(
        f"You have {len(tweet_ids)} tweets. Delete now? (enter y / yes to go ahead, n / other to exit.)"
    )

    answer = input()

    if not (answer.lower() == "y" or answer.lower() == "yes"):
        sys.exit()

    print("\nDeleting now.")

    threads = []

    for chunk in workload:
        threads.append(threading.Thread(
            target=delete_tweets,
            args=(
                (
                    chunk,
                    account_session,
                )
            ),
            daemon=True
        ))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
