import os
import json
from starkboard.utils import Requester


def update_core_ecosystem(db):
    list_applications = []
    print("Inserting Ecosystem Data...")
    with open('starkboard/ecosystem/ecosystem.json', 'r') as f:
        list_applications = json.load(f)
    for app in list_applications:
        final_app = {}
        final_app['application'] = app.get('name')
        final_app['application_short'] = app.get('short_name')
        final_app['tags'] = json.dumps(app.get('tags'))
        final_app['discord'] = app.get('network').get('discord')
        final_app['website'] = app.get('network').get('website')
        final_app['twitter'] = app.get('network').get('twitter')
        final_app['medium'] = app.get('network').get('medium')
        final_app['github'] = app.get('network').get('github')
        final_app['isLive'] = app.get('isLive')
        final_app['isTestnetLive'] = app.get('isTestnetLive')
        final_app['description'] = app.get('description')
        final_app['countFollowers'] = 0
        print(f'Inserted {final_app["application"]} !')
        db.insert_ecosystem_offchain(final_app)
    print("Success !")
    return None

def get_core_ecosystem(db):
    res = db.get_ecosystem_offchain()
    return res

def get_starknet_db_ecosystem():
    headers = {'Content-Type': 'application/json'}
    page = 0
    starknet_db_res = Requester(os.environ.get('STARKNET_ECOSYSTEM_DB_URL')).get(url=f"projects?page={page}&size=100", headers=headers).json()
    list_applications = starknet_db_res.get('content')
    while not starknet_db_res.get('last'):
        page += 1
        starknet_db_res = Requester(os.environ.get('STARKNET_ECOSYSTEM_DB_URL')).get(url=f"projects?page={page}&size=100", headers=headers).json()
        list_applications += starknet_db_res.get('content')
    count_projects = len(list_applications)
    return list_applications, count_projects

   
def normalize_list_applications(list_applications):
    final_apps = []
    for app in list_applications:
        final_app = {}
        final_app['id'] = app.get('id')
        final_app['application'] = app.get('name')
        final_app['application_short'] = app.get('short_name')
        final_app['tags'] = json.dumps(app.get('tags'))
        final_app['discord'] = app.get('network').get('discord')
        final_app['website'] = app.get('network').get('website')
        final_app['twitter'] = app.get('network').get('twitter')
        final_app['medium'] = app.get('network').get('medium')
        final_app['github'] = app.get('network').get('github')
        final_app['isLive'] = app.get('isLive')
        final_app['isTestnetLive'] = app.get('isTestnetLive')
        final_app['description'] = app.get('description')
        final_app['profile_picture_url'] = app.get('network').get('twitterImage')
        final_app['banner_picture_url'] = app.get('network').get('twitterBanner')
        final_app['countFollowers'] = app.get('countFollowers')
        final_apps.append(final_app)
    return final_apps
