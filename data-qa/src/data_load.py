import datetime
import requests
import time
import json
import random
import streaming_analysis
import aquaspice_context_broker_client_utils
import csv
def fake_payload(id, date,coordinates,temperature,conductivity,depth): 
    return {
        "id": "urn:ngsi-ld:AquaSpice:measurementStation:" + id,
        "type": "MeasurementStation",        
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": coordinates
            }
        },
        "temperature": {
        "type": "Property",
        "value": temperature,
        "observedAt":date        
        },
        "conductivity":{
        "type": "Property",
        "value": conductivity,
        "observedAt":date
        },
        "depth": {
        "type": "Property",
        "value": depth,
        "observedAt":date
        }        
        ,"@context": [           
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ,{ "MeasurementStation": aquaspice_context_broker_client_utils.config["rtm_platform_public_url"] + "/schemas/AquaSPICE/MeasurementStation/schema.json" }
        ]
    }
#python39 streaming_analysis_test.py 'config/base_config_testing_remote.json;config/test_stations.json'  

if __name__ == '__main__':
    exit()
    aquaspice_context_broker_client_utils.init()

   
    with open('etmeasurementstation.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in spamreader:
            print(', '.join(row))
            try:
                id = row[0].replace('urn:ngsi-ld:AquaSpice:measurementStation:','')
                #entity_id, time_index, temperature, conductivity, depth, ST_X(location) AS latitude,  ST_Y(location) AS longitude

                p = fake_payload(id = id,
                                date =datetime.datetime.strptime(row[1].split("+")[0]+"Z", "%Y-%m-%d %H:%M:%S.%fZ").strftime("%Y-%m-%dT%H:%M:%SZ"),
                                coordinates = [float(row[5]),float(row[6])],
                                temperature = float(row[2]),
                                conductivity = float(row[3]),
                                depth =float(row[4]))
                #print(p)
                
                aquaspice_context_broker_client_utils.upsert_context_broker([p])

                #exit()
                i += 1
                if(i == 100):
                    time.sleep(2)
                    i = 0
            except Exception as e:
                print(e)
            '''
            p = fake_payload(id = station["name"], 
                             date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                             coordinates = station["coordinates"],
                             temperature = random.randrange(20, 35) * multiplier,
                             conductivity = random.randrange(20, 30) * multiplier,
                             depth = random.randrange(30, 40) * multiplier)
            print(p)
            streaming_analysis.process_reading(p)
            aquaspice_context_broker_client_utils.upsert_context_broker([p])
            '''
