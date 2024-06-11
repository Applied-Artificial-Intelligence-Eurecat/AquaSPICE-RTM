import datetime
import requests
import time
import json
import random
import streaming_analysis
import aquaspice_context_broker_client_utils


"""
To call this file use: python streaming_analysis_test.py ../config/base_config_testing_remote.json;../config/data_qa_params.json
v2: python streaming_analysis_test.py ../config/base_config_testing_remote.json;../config/data_qa_params.json;../config/data_qa_config.json
"""

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
'''
incorrect/old/testing_environment
        ,"@context": [           
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ,{ "MeasurementStation": aquaspice_context_broker_client_utils.config["rtm_platform_public_url"] + "/schemas/AquaSPICE/MeasurementStation/schema.json" }
        ]
''' 
'''
correct
"@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"                
            ]
'''
#python39 streaming_analysis_test.py 'config/base_config_testing_remote.json;config/test_stations.json'  


def dumy_produce_corrected_reading(id, date, coordinates, temperatureRaw, temperatureCorrected, conductivityRaw,conductivityCorrected, depthRaw, depthCorrected):
    print("corrected")
def dumy_produce_anomaly(id, anomaly_start_date, last_anomaly_date, subject): 
    print("anomaly")

if __name__ == '__main__':
    aquaspice_context_broker_client_utils.init()
    stations = [
        { "name": "MS1_test", "coordinates": [37.337937901015444, -5.995446988486934] },
        { "name": "MS2_test", "coordinates": [37.319196710566146, -5.992914302017941] },
        { "name": "MS3_test", "coordinates": [36.319196710566146, -5.992914302017941] }
    ]

    '''
    while(True):
        streaming_analysis.produce_anomaly(stations[0]["name"],
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Error")
        time.sleep(random.randrange(2,10,1))
    exit()
    '''
    
    # Cycle through defined analysis in json file
    for analysis in aquaspice_context_broker_client_utils.config["analysis"]:
        # Create subscription at given ID (get from config file) for each analysis
        streaming_analysis.create_subscription(analysis)
    '''
    for analysis in aquaspice_context_broker_client_utils.config["analysis"]:    
        # Depending on the algorithm used, perform the initial load of data
        if analysis["algorithm"] == "hampel_filter":
            streaming_analysis.hampel_filter_module(analysis)
        elif analysis["algorithm"] == "z_score":
            streaming_analysis.z_score_module(analysis)
    '''        
    
    # Get list of subscriptions to debug, it will send a random subscription along as the fake payload
    subcription_id_list = [x["subscription_id"] for x in aquaspice_context_broker_client_utils.config["analysis"]]
    
    i = 0    
    multiplier = 1
    while True:
        # Iterate over the 2 stations
        for station in stations:
            
            random_subscription = subcription_id_list[random.randrange(0, len(subcription_id_list))]
            
            # Generate a fake payload with random values
            
            p = fake_payload(id = station["name"], 
                             date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                             coordinates = station["coordinates"],
                             temperature = random.randrange(10, 25) * multiplier,
                             conductivity = random.randrange(30, 60) * multiplier,
                             depth = random.randrange(30, 40) * multiplier)

            
            streaming_analysis.process_reading(p, random_subscription, streaming_analysis._produce_anomaly, streaming_analysis._produce_corrected_reading)
            aquaspice_context_broker_client_utils.upsert_context_broker([p])
        
        # Sleep    
        time.sleep(random.randrange(4, 12 ,1))
        i += 1        
        anomaly_end_i = None
        
        # Random to force an outlier period every 20 readings with a random duration (num readings)
        if i ==5:
            anomaly_end_i = random.randrange(2, 10)+i
            multiplier = random.randrange(2, 5)

        if anomaly_end_i is not None and i > anomaly_end_i:
            anomaly_end_i = None
            multiplier = 1
           
        # Restart counter    
        if i == 20: 
            i = 0