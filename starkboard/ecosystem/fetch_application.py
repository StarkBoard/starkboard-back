import os
import json


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

