import traceback, random
import requests, json, time
from datetime import datetime
from datetime import timedelta

import aquaspice_context_broker_client_utils as aquaspice_utils
import auxiliar_functions as aux_func
import streaming_analysis_batch
import streaming_analysis

import warnings, os

warnings.filterwarnings(action='ignore')
import pandas as pd

working_dir = os.path.dirname(os.path.realpath(__file__))

# ====================== Variables to set before running batch analysis ================================
#stations_to_analyze = ["AK_04", "AK_06", "AK_08", "AK_12", "AK_14", "AK_16", "AK_18", "AK_20", "AK_22", "AK_25",
#                       "KD_01", "KD_03", "KD_07", "KD_08", "KD_14", "KD_16", "KD_17", "KD_18"]
#stations_to_analyze = ["AK_04", "AK_06", "AK_08", "AK_12", "AK_14", "AK_16", "AK_18", "AK_20", "AK_22", "AK_25"]
stations_to_analyze = ["AK_04", "AK_06", "AK_08", "AK_12", "AK_14", "AK_16", "AK_18", "AK_20", "AK_22", "AK_25",
                       "KD_01", "KD_03", "KD_08", "KD_14", "KD_16", "KD_17", "KD_18"]

'''
last_n_dict = {"AK_04" : 5979,
               "AK_06": 6287,
               "AK_08" : 6205,
               "AK_12" : 7845,
               "AK_14" : 5617,
               "AK_16" : 6095,
               "AK_18" : 6008,
               "AK_20" : 6243,
               "AK_22" : 8738,
               "AK_25" : 1277,
               "KD_01" : 5715,
               "KD_03" : 6151,
               "KD_07" : 490,
               "KD_08" : 5719,
               "KD_14" : 6106,
               "KD_16" : 5874,
               "KD_17" : 4924,
               "KD_18" : 572}
'''

last_n_dict = {'KD_01': 214,
 'KD_02': 213,
 'KD_03': 224,
 'KD_04': 218,
 'KD_08': 225,
 'KD_09': 217,
 'KD_13': 219,
 'KD_14': 213,
 'KD_16': 343,
 'KD_17': 225}

offset_global = 13521
limit_global = 5000
# 1 day of data = around 205 samples
last_n_global = 3160
# ======================================================================================================

def query_historical_all_data(urn, offset, limit):
    '''
    Get data starting from the beginning
    '''
    return aquaspice_utils.query_quantumleap(
        f'entities/{urn}?&type=https://{domain_name}/schemas/AquaSPICE/MeasurementStation/schema.json&offset={offset}&limit={limit}')


def query_historical_lastN(urn, lastN):
    '''
    Get data (last n data samples)
    '''
    response = aquaspice_utils.query_quantumleap(
        f'entities/{urn}?lastN={lastN}&type=https://{domain_name}/schemas/AquaSPICE/MeasurementStation/schema.json')

    if response.ok == False:
        print(f"---X Failed to get historical data for {urn}: {response.reason}")
        return None
    else:
        print(f"---> Query historical data at {urn} successful ({lastN} samples retrieved).")
        return response

#lastN = 100

# Usage:
# python39 -u ./src/batch_analysis.py "config/base_config_antwerp_remote.json;config/data_qa_params.json;config/data_qa_config.json"
# python -u ./src/batch_analysis.py "config/base_config_antwerp_remote.json;config/data_qa_params.json;config/data_qa_config.json"

def generate_fake_payload(id, counter):

    # entity_id, time_index, temperature, conductivity, depth, ST_X(location) AS latitude,  ST_Y(location) AS longitude
    new_fake_date = (datetime.now() + timedelta(minutes=15 * counter)).strftime("%Y-%m-%dT%H:%M:%SZ")

    p = fake_payload(id=id,
                     date= new_fake_date,
                     coordinates=[22312, 48734],
                     temperature=random.randrange(0, 10),
                     conductivity=random.randrange(10, 22),
                     depth=float(random.randrange(40, 50)))
    return p

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
        "observedAt": date
        },
        "conductivity":{
        "type": "Property",
        "value": conductivity,
        "observedAt": date
        },
        "depth": {
        "type": "Property",
        "value": depth,
        "observedAt": date
        }
        ,"@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
    }

def analyze_station_batch_fake(station, subcription_id_list):
    for i in range(0, 1000):
        fake_payload = generate_fake_payload(station, i + 1)

        aux_func.logMessage(f"Sending fake payload: {fake_payload}")
        #for subscriptionID in ["urn:ngsi-ld:Subscription:watercps_detection_1", "urn:ngsi-ld:Subscription:hampel_anomaly_detection_1", "urn:ngsi-ld:Subscription:z_score_detection_1"]:
        for subscriptionID in ["urn:ngsi-ld:Subscription:watercps_detection_1"]:
        #for subscriptionID in ["urn:ngsi-ld:Subscription:hampel_anomaly_detection_1"]:
            streaming_analysis.process_reading(fake_payload,
                                               subscriptionID,
                                               aux_func._produce_anomaly,
                                               streaming_analysis._produce_corrected_reading)

        time.sleep(2)

def analyze_station_batch(station, subcription_id_list):

    global offset_global, limit, stations_to_analyze, last_n_dict

    counter = 0
    # offset 20k = 18/02/23
    # offset 20k (KD_18) = 27/10/23
    # offset 30k = 27/04/23
    # offset 25k = 29/03/23
    # offset 26k = 05/04/23
    # offset 26600 = 08/04/23 === most used
    # offset 50k = 01/08/23
    # offset 57k = 29/08/23
    # offset 62k = 18/09/23
    # offset 62500 = 20/09/23 / 13/11/23 (KD_08)
    # offset 64k = 24/09/23
    # offset 68k = 29/09/23 (KD_01)
    # offset 72k =
    # offset 82k = 22/11/23 (KD_01)
    # offset 84k = 15/12/223 (KD_01)

    #if station == "KD_01":
    #    offset = offset_global
    #else:
    #    offset = 0

    #offset = offset_global
    limit = limit_global

    #limit = offset + 870
    #resp = query_historical_all_data(f'urn:ngsi-ld:AquaSpice:measurementStation:{station}', offset=offset, limit=limit)
    #last_n  = last_n_dict[station] + 400
    last_n = 350
    resp = query_historical_lastN(f'urn:ngsi-ld:AquaSpice:measurementStation:{station}', last_n)

    #print(resp)
    # Uncomment if using not last-n
    #while (resp.ok):
    resp = resp.json()
    conductivity = next(e for e in resp['attributes'] if e["attrName"] == "conductivity")['values']
    depth = next(e for e in resp['attributes'] if e["attrName"] == "depth")['values']
    temperature = next(e for e in resp['attributes'] if e["attrName"] == "temperature")['values']
    location = next(e for e in resp['attributes'] if e["attrName"] == "location")['values']
    t = resp['index']
    num_readings = len(conductivity)

    for i in range(num_readings):
        # random_subscription = subcription_id_list[random.randrange(0, len(subcription_id_list))]
        print(f"Counter: {counter}, Date: {t[i]}, Station: {station}")

        # print(f'{station} - {t[i]}')
        reading = {
            "id": f'urn:ngsi-ld:AquaSpice:measurementStation:{station}',
            "type": "MeasurementStation",
            "location": {"value": location[i]},
            "temperature": {"observedAt": t[i], "value": temperature[i]},
            "depth": {"observedAt": t[i], "value": depth[i]},
            "conductivity": {"observedAt": t[i], "value": conductivity[i]}
        }

        #random_subscription = subcription_id_list[random.randrange(0, len(subcription_id_list))]
        # streaming_analysis.process_reading(reading,dumy_produce_anomaly,dumy_produce_corrected_reading)
        # streaming_analysis.process_reading(reading,"urn:ngsi-ld:Subscription:measurement_station_hampel_filter",streaming_analysis._produce_anomaly,streaming_analysis._produce_corrected_reading)
        streaming_analysis_batch.process_reading(reading,
                                                 aux_func._produce_anomaly,
                                                 streaming_analysis_batch._produce_corrected_reading)

        time.sleep(0.1)

        # Change to incremental if necessary
        counter = i

    #offset = offset + limit + 1
    #resp = query_historical_all_data(f'urn:ngsi-ld:AquaSpice:measurementStation:{station}', offset=offset, limit=limit)


# offset=3&limit=3
def dumy_produce_corrected_reading(id, date, coordinates, temperatureRaw, temperatureCorrected, conductivityRaw,
                                   conductivityCorrected, depthRaw, depthCorrected):
    print("corrected")


def dumy_produce_anomaly(id, anomaly_start_date, last_anomaly_date, subject):
    print("anomaly")


if __name__ == "__main__":
    '''
    Main function
    '''
    aquaspice_utils.init()

    subscription_id_list = [x["subscription_id"] for x in aquaspice_utils.config["analysis"]]

    try:
        # KD_02, 04, 09, 13 gives error
        for st in stations_to_analyze:
            #analyze_station_batch(st, subscription_id_list)
            analyze_station_batch(st, subscription_id_list)
            #analyze_station_batch_fake(st, subscription_id_list)

    except Exception as e:
        print(e)
        print(traceback.format_exc())
