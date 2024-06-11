################################################################################### Imports
import datetime
import os
import requests
import time
import argparse
import json
import random

config = None
token = None

def load_config():
    global config
    # Load config
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('config_file', metavar='config_file', help='the config file path')
    args = parser.parse_args()
    config = {}
    
    print(f'Using config file[s] {args.config_file}')
    
    for file_path in args.config_file.split(';'):
        print(f'Reading {file_path}')
        with open(file_path, "r") as f:
            content = json.load(f)
            print(content)   
            config = {**config, **content}
            
    print("Final config:")
    print(config) 
    
def query_quantumleap(path):
    global config

    url = config["rtm_platform_services_urls"]["historical"] + f'/v2/{path}'
    print(url)
    response = requests.get(url = url,
                            headers={'Authorization': 'Bearer ' + access_token})
        
    return response

def request_create_subscription(subscription_id, body):
    '''
    Creates a subscription to recieve updates uppon context changes.
    Uses a predefined `subscription_id`. This grants that only one subscription will exists. If not proivded, the ID gets generated by the context-broker
    and this can lead to multiple subscriptions
    For more info, read: https://documenter.getpostman.com/view/513743/fiware-subscriptions/RW1dHeTR#intro  and specialy
    https://documenter.getpostman.com/view/513743/fiware-subscriptions/RW1dHeTR#89da7ed6-4c05-4360-810b-a80e7ee213aa
    '''
    global config

    #Delete subscription (if exists)
    print("------ Delete sub ------")
    response = requests.delete(url = config["rtm_platform_services_urls"]['broker']+'/ngsi-ld/v1/subscriptions/' + subscription_id,
    headers = { 'Authorization': 'Bearer ' + access_token})
    print(response)
    print("------ Create sub ------")
    #Create new subscription
    print(json.dumps(body, indent=4),flush=True)

    response = requests.post(url=config["rtm_platform_services_urls"]["broker"] + '/ngsi-ld/v1/subscriptions',
                             headers = {"content-type": "application/ld+json",  'Authorization': 'Bearer ' + access_token}, data=json.dumps(body))
    print(response)
    print(response.text)
    print('--> Subscription created', flush = True)

def create_subscription(analysis):
    '''
    Function responsible of creating the subscription, based on the defined analysis (entitytype, ids, properties...)
    '''
    global config

    # Create json list to specify which Ids/entities are part of this subscription
    entity_json_list = []

    if "entityIds" in analysis:
        for entity in analysis["entityIds"].split(";"):
            entity_json_list.append({"type": analysis["entityType"], "id": entity})
    else:
        entity_json_list.append({"type": analysis["entityType"]})

    # Create new subscription
    body = {
        "id": analysis["subscription_id"],
        "description": "anomaly-detection",
        "type": "Subscription",
        "entities": entity_json_list,
        "notification": {
            "attributes": analysis["analyzedProperties"],
            "format": "normalized",
            "endpoint": {
                "uri": config["callback_url"],
                "accept": "application/json",
            },
        },
        # "throttling": 1,
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            {
                analysis["entityType"]: config[
                                            "rtm_platform_public_url"
                                        ]
                                        + "/schemas/AquaSPICE/" + analysis["entityType"] + "/schema.json"
            },
        ],
    }
    request_create_subscription(analysis["subscription_id"], body)

    del entity_json_list

    #print("--> Subscription created")


def upsert_context_broker(body):   
    #print(body)
    #We can do an insert and an update but an exception will be raised if we do an insert and the entity already exists or an update and if the entity
    # does not exists, with an upsert we do not need to check the existance of that entity
    #"Fiware-Service": "AquaSpice"
    global config
    
    url = config["rtm_platform_services_urls"]["broker"] + '/ngsi-ld/v1/entityOperations/upsert'
    print(f"--> Started upsert_context_broker (url: {url})", flush = True)
    
    #print(json.dumps(body))
    response = requests.post(url = url, headers = {
     'Authorization': 'Bearer ' + access_token,
    "content-type": "application/ld+json"            
    }, data=json.dumps(body))

    # Refresh token in case of need
    if response.status_code == 401:
        get_token()
        
        response = requests.post(url = url, headers = {
        'Authorization': 'Bearer ' + access_token,
        "content-type": "application/ld+json"            
        }, data=json.dumps(body))
        
    if(response.ok == False):
        print(f"---X Error while executing upsert_context_broker. Response code: {response.status_code}, Response text: {response.text}", flush = True)
    else:
        print(f"---> Success on upsert_context_broker. Response code: {response.status_code}, Response text: {response.text}", flush = True)
        
    #print(response)
    #print(response.ok, response.text)
    #print("", flush=True)

def get_token():
    global access_token, config

    if config["external"] == False:
        access_token = ""
        return
    #
    # Exchange config["iot_user"] and config["iot_pwd"] for an acces token
    #
    payload='grant_type=password&username='+config["iot_user"]+'&password='+config["iot_pwd"]
    
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'     
    }
    
    url = config["rtm_platform_services_urls"]["secure"] + "/oauth2/token"
    
    response = requests.request("POST", url, headers=headers,auth=(config["app_id"],config["app_secret"]), data=payload)

    if(response.ok == True):
        print(f"--> Response from token: {response}", flush = True)
        print(f'--> Access token acquired = {response.json()["access_token"]}', flush = True)

        access_token = response.json()["access_token"]
    else:
        print(f"---X Error while accepting token: {response.text}", flush = True)

def query_historical_data_lastN(urn, lastN):
    '''
    Query historical data. Based on the last N samples.
    '''
    global config

    type = (
            config["rtm_platform_public_url"]
            + "/schemas/AquaSPICE/MeasurementStation/schema.json"
    )
    print(f"--> Query historical data with n = {lastN} for urn = {urn}", flush = True)
    response = query_quantumleap(
        f"entities/{urn}?lastN={lastN}&type={type}"
    )
    if response.ok == False:
        print(f"---X Failed to get historical data for {urn}: {response.reason}", flush = True)
        return None
    else:
        print(f"---> Query historical data at {urn} successful ({lastN} samples retrieved).", flush = True)
        return response.json()


def query_historical_all_data(urn, offset, limit):
    '''
    Query historical data. Possible to include offset and limit.
    '''

    response = query_quantumleap(
        f'entities/{urn}?&type=https://{domain_name}/schemas/AquaSPICE/MeasurementStation/schema.json&offset={offset}&limit={limit}')

    if response.ok == False:
        print(f"---X Failed to get historical data for {urn}: {response.reason}", flush = True)
        return None
    else:
        print(f"---> Query historical data at {urn} successful ({limit} samples retrieved).", flush = True)
        return response.json()


def init():    
    load_config()
    get_token()