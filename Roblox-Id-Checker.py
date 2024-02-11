import requests
import pandas as pd
import threading
import time
import sys
import json

# Configuration Settings
TIME_SET = 1  # The set value of the check time
WEBHOOK_URL = ''  # Insert the webhook link from Discord
OUT_PATH = ''  # Specify your path to the out.csv file

exit_flag = False

class AssetClass():
    classes = {
        'Image': 1,
        'TShirt':2,
        'Audio': 3,
        'Mesh': 4,
        'Lua': 5,
        'Hat': 8,
        'Place': 9,
        'Model': 10,
        'Shirt': 11,
        'Pants': 12,
        'Decal': 13,
        'Head': 17,
        'Face': 18,
        'Gear': 19,
        'Badge': 21,
        'Animation': 24,
        'Torso': 27,
        'RightArm':	28,
        'LeftArm': 29,
        'LeftLeg': 30,
        'RightLeg':	31,
        'Package': 32,
        'GamePass':	34,
        'Plugin': 38,
        'MeshPart': 40,
        'HairAccessory': 41,
        'FaceAccessory': 42,
        'NeckAccessory': 43,
        'ShoulderAccessory': 44,
        'FrontAccessory': 45,
        'BackAccessory': 46,
        'WaistAccessory': 47,
        'ClimbAnimation': 48,
        'DeathAnimation': 49,
        'FallAnimation': 50,
        'IdleAnimation': 51,
        'JumpAnimation': 52,
        'RunAnimation': 53,
        'SwimAnimation': 54,
        'WalkAnimation': 55,
        'PoseAnimation': 56,
        'EarAccessory': 57,
        'EyeAccessory':	58,
        'EmoteAnimation': 61,
        'Video': 62,
        'TShirtAccessory': 64,
        'ShirtAccessory': 65,
        'PantsAccessory': 66,
        'JacketAccessory': 67,
        'SweaterAccessory': 68,
        'ShortsAccessory': 69,
        'LeftShoeAccessory': 70,
        'RightShoeAccessory': 71,	
        'DressSkirtAccessory': 72,	                     
        'FontFamily': 73,
        'EyebrowAccessory':	76,
        'EyelashAccessory':	77,
        'MoodAnimation': 78,
        'DynamicHead': 79
    }

def send_discord_message(ad_df, webhook_url, asset_id, message, data):

    decal_value = ad_df.loc[ad_df['ImageId'] == asset_id, 'DecalId'].iloc[0]
    img_value = ad_df.loc[ad_df['ImageId'] == asset_id, 'ImageId'].iloc[0]
    Name_value = ad_df.loc[ad_df['ImageId'] == asset_id, 'FileName'].iloc[0]
    image_url = data['data'][0].get('imageUrl')
    
    decal_value = int(decal_value)
    img_value = int(img_value)
    library_url = f'https://www.roblox.com/library/{img_value}/'
    Asset_url = f'https://assetdelivery.roblox.com/v2/assetId/{asset_id}'

    response = requests.get(Asset_url)

    if response.status_code == 200:
        data = response.json()
        if 'assetTypeId' in data:
            Asset_type = data['assetTypeId']

            # Check if Asset_type is in the classes dictionary
            asset_type_name = next(key for key, value in AssetClass.classes.items() if value == Asset_type)

    embed_data = {
        'title': f'{asset_type_name} confirmed',
        'url': library_url,
        'image': {'url': image_url},
        'fields': [
            {'name': 'File Name', 'value': f'||{Name_value}||'},
            {'name': 'Decal Id', 'value': f'||{decal_value}||'},
            {'name': 'Image ID', 'value': f'||{img_value}||'}
        ],
        'color': '16777215'
    }

    payload = {'embeds': [embed_data]}

    response = requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

    if response.status_code == 204:
        print(message)
    else:
        print(f'Cant send message to Discord. Status code: {response.status_code}')

def get_asset_state(asset_id, ad_df, blocked_assets):
    url = f'https://thumbnails.roblox.com/v1/assets?assetIds={asset_id}&returnPolicy=PlaceHolder&size=420x420&format=Png&isCircular=false'
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            state = data['data'][0].get('state')
            message = f'The AssetId {asset_id} is {state}.'
            
            if state == 'Blocked':
                blocked_assets.add(asset_id)
                print(message)

            elif state == 'InReview':
                print(message)

            elif state == 'Completed':
                blocked_assets.add(asset_id)
                send_discord_message(ad_df, WEBHOOK_URL, asset_id, message, data)
                global exit_flag
                exit_flag = True

def check_assets():
    assets = {}
    blocked_assets = set()

    while True:
        ad = pd.read_csv(OUT_PATH, delimiter=',', quoting=3)
        ad.columns = ['FileName', 'DecalId', 'ImageId']

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

        if exit_flag:
            sys.exit()

if __name__ == '__main__':
    exit_flag = check_assets()
    
