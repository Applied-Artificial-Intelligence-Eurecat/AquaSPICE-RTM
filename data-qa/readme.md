# Data QA Module

## Usage

### Streaming

Run with docker

### Batch mode
````python
python -u ./src/batch_analysis.py "config/base_config_antwerp_remote.json;config/data_qa_params.json;config/data_qa_config.json"
````

Requires setting in batch_analysis.py:
- stations_to_analyze
- offset_global
- limit
- or configure if last_n wish to be used

# Changelog
---

## 07/02/24:
- The scripts have been changed, algorithm-related code are now in separated .py files
- Added waterCPS method with its proper Upsert ({EntityType}Flagged)
- Added logger

## 13/23/23:
- Added WaterCPS error flagging threshold analysis to the dataQA
- Upgraded pandas to 2.1.2
- General bug fixing
- Adding script for batch analysis

## 27/10/23:
- Adjustments in produce_corrected
- Upgrade to pandas 2.1.2, some functions (such as pandas append) were changed.

## 20/10/23:

- Corrected function produce_corrected_readings

## 17/05/23:

- Historic data doesn't trigger at function start, instead it triggers when new data from a new entityId is received.
- EntityId specification at data_qa_config.json isn't mandatory anymore.
- Hampel filter and Z-score parameters adjusted.
- Problem that caused hampel filter to not detect outliers: corrected
- Deal with shortages of data. e.g. when there is a period when data is not received. (A function calculates the date distance of every new sample and last succesfully received sample). When that happens, a reset in in-memory data is done to prevent algorithms confusion.
- Monitoring of cadency of data: Function cadency_monitoring() executes every 25 minutes to check when the last data was received, if it was > than 24 hours (parameter data_cadency_anomaly_threshold at data_qa_params.json) it generates an Anomaly (its implemented but this part is currently commented).
- In-memory data: Changed from simple arrays to dataframes with date index to better control the gaps in data.
- Z-score starts outlier detection when n_samples > 250 and hampel filter starts when sliding_window > 100.


### 16/02/23:
---

- Produce corrected reading function changes:
    - location parameter is not hardcoded into the body anymore
    - Creation of parameter **{{notCorrectedProperties}}** which indicates which parameters should only be copied from the original reading, to the creation of the body of the "corrected reading"
    - Overall, the function is more generalizable and should adapt to different types of entities

### 13/02/23:
---

- create_subscription function corrected 
    - Included entityIds/entityTypes/Properties in the subscription
    - More generalizable

- Callback function
    - Now it also passes the subscription id to the process reading function

- process reading function
    - It identifies the analysis based on the subscription id of incoming package, and process data as defined

- produce corrected reading
    - More generalizable, now the body format of the json does not represent only measurement stations

- Variable measurement_stations_data renamed to entities_data

### 30/01/23:
---

- The json file data_qa_config now holds a list of different analysis

- When launched, the application:
    - Create subscriptions defined in json file
    - Update, for each defined analysis, the in-memory dictionaries with data

- On each incoming package, it looks at which of the analysis it belongs and then execute all defined analysis.
    - New data arrives
    - The incoming packet is inspected to see which of the defined analysis it is part of
    - The corresponding outlier detection analysis is executed (with defined entities, ids and properties)
    - If an anomaly is detected, it creates an anomaly with the supplied Id
    - Publish the corrected version of the reading


### 17/01/23
---

- New file data_qa_config added which contains the things and properties to be included in the analysis. Also includes the subscription ID and more
- General code refactored to reflect changes (more generalizable)

When the process starts:

- In-data memory objects are updated depending on the algorithm chosen (once)
- During the process reading, only the supplied things and properties will be analyzed (as indicated in the data_qa_config file), after each data sample is analyzed, they are included in the in-memory objects

- Tests made in the testing environment

## Z-score outlier detection

Z-Score outlier detection method is implemented.


## Hampel Filter outlier detection

Hampel Filter outlier detection implemented.

## WaterCPS Error Flagging on Sensors

Implemented.