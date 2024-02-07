import requests
import pandas as pd
import threading
import time
import sys
import json

# Configuration Settings
TIME_SET = 1  # The set value of the check time
WEBHOOK_URL = ""  # Insert the webhook link from Discord
OUT_PATH = ""  # Specify your path to the out.csv file

def send_discord_message(ad_df, webhook_url, asset_id, message, data):
    decal_value = ad_df.loc[ad_df['ImageId'] == asset_id, 'DecalId'].iloc[0]
    img_value = ad_df.loc[ad_df['ImageId'] == asset_id, 'ImageId'].iloc[0]
    name_value = ad_df.loc[ad_df['ImageId'] == asset_id, 'FileName'].iloc[0]
    image_url = data['data'][0].get('imageUrl')

    decal_value = int(decal_value)
    img_value = int(img_value)

    embed_data = {
        "title": "Image Bypassed.",
        "url": image_url,
        "image": {"url": image_url},
        "fields": [
            {"name": "File Name", "value": f"||{name_value}||"},
            {"name": "Decal Id", "value": f"||{decal_value}||"},
            {"name": "Image ID", "value": f"||{img_value}||"}
        ],
        "color": "16777215"
    }

    payload = {"embeds": [embed_data]}

    response = requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

    if response.status_code == 204:
        print(message)
    else:
        print(f"Cant send message to Discord. Status code: {response.status_code}")

def get_asset_state(asset_id, ad_df, blocked_assets):
    url = f"https://thumbnails.roblox.com/v1/assets?assetIds={asset_id}&returnPolicy=PlaceHolder&size=420x420&format=Png&isCircular=false"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            state = data['data'][0].get('state')
            message = f"The AssetId {asset_id} is {state}."
            
            if state == "Blocked":
                blocked_assets.add(asset_id)
                print(message)

            elif state == "InReview":
                print(message)

            elif state == "Completed":
                blocked_assets.add(asset_id)
                send_discord_message(ad_df, WEBHOOK_URL, asset_id, message, data)
                return True  # Exit flag set to True

    return False  # Exit flag remains False

def check_assets():
    assets = {}
    blocked_assets = set()

    while True:
        ad = pd.read_csv(OUT_PATH, delimiter=",", quoting=3)
        ad.columns = ["FileName", "DecalId", "ImageId"]

        threads = []
        for index, row in ad.iterrows():
            asset_id = row['ImageId']
            if asset_id not in blocked_assets:
                time.sleep(TIME_SET)
                assets[asset_id] = True
                thread = threading.Thread(target=get_asset_state, args=(asset_id, ad, blocked_assets))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        if any(threads):
            sys.exit()  # Exit if any thread sets the exit flag

if __name__ == "__main__":
    exit_flag = check_assets()
    if exit_flag:
        sys.exit()
