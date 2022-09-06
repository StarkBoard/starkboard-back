import os
import json
from starkboard.utils import StarkboardDatabase


def update_core_ecosystem(db):
    list_applications = []
    with open('starkboard/ecosystem/ecosystem.json', 'r') as f:
        list_applications = json.load(f)

    for app in list_applications:
        final_app = {}
        final_app['application'] = app.get('name')
        final_app['application_short'] = app.get('short_name')
        final_app['tags'] = app.get('tags')
        final_app['discord'] = app.get('network').get('discord')
        final_app['website'] = app.get('network').get('website')
        final_app['twitter'] = app.get('network').get('twitter')
        final_app['medium'] = app.get('network').get('medium')
        final_app['github'] = app.get('network').get('github')
        final_app['isLive'] = app.get('isLive')
        final_app['isTestnetLive'] = app.get('isTestnetLive')
        #final_app['isLive'] = app.get('isLive')

    print(list_applications[0])
    return None
