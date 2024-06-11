# AquaSPICE

The aim of AquaSPICE (Advancing Sustainability of Process Industries through Digital and Circular Water Use Innovations) is the adoption of circular water use practices in the industrial sector, the integration, and the demonstration of innovative solutions concerning the process, the resource-efficiency, and the digital tools. It aims at materializing circular water use in European Process Industries, fostering awareness in resource-efficiency and delivering compact solutions for industrial applications.

## RTM platform

The RTM platform focuses on real-time monitoring and operational modelling. It is integrated within the AquaSPICE ecosystem and it is based on the [FIWARE initiative](https://www.fiware.org/).

To guarantee that data ingested by the RTM platform is valid and can be confidently used by end users through dashboards, as well as by intelligent services to reason over it, the context broker [Orion](https://github.com/FIWARE/context.Orion-LD) has in its core the Data Quality Assurance module (DataQA). This module evaluates the input data (coming from on-site sensors) in real time and produces transformed time series with quality metrics associated to the original readings (e.g., flag invalid readings). This evaluation is implemented using a bag of algorithms and techniques offered by the DataQA module including feature engineering and outliers’ detection and correction.

## Fiware

FIWARE Foundation drives the definition – and the Open Source implementation – of key open standards that enable the development of portable and interoperable smart solutions in a faster, easier and affordable way, avoiding vendor lock-in scenarios, whilst also nurturing FIWARE as a sustainable and innovation-driven business ecosystem. The FIWARE platform provides a rather simple yet powerful set of APIs (Application Programming Interfaces) that ease the development of Smart Applications in multiple vertical sectors. It includes Core Context Broker components, Core Data Connectors, Context Processing, Analysis and Visualization, IoT agent interfaces and more.

## Orion

The Orion Context Broker currently provides the FIWARE NGSI v2 API which is a simple yet powerful Restful API enabling to perform updates, queries, or subscribe to changes on context information. The context broker (Orion-LD) is responsible for managing the lifecycle of context information: entities and their attributes. Using the APIs provided by the context broker it allows to create context elements, manage them through updates, update their attributes, perform queries to retrieve their status, and subscribe to context changes.

A Context Broker component is the core and mandatory component of any “Powered by FIWARE” platform or solution. It enables to manage context information in a highly decentralized and large-scale manner.

# Proxy

NGINX is open-source web server software used for reverse proxy, load balancing, and caching. It provides HTTPS server capabilities and is mainly designed for maximum performance and stability. It also functions as a proxy server for email communications protocols, such as IMAP, POP3, and SMTP. In this build its used a reverse proxy to provide HTTPS with the help of Certbot.

# Configuration
Change in files rtm.conf, grafana.conf, all the data-qa/config and src files, and .env the {domain_name} value for the selected domain of the platform.

Also, make all the D3.5 guide changes so that all the components are correctly configured.

**BEWARE**, this build uses the antwerp example, so it doesn't use rtm as a prefix; it uses antwerp. All the commands and container references containing rtm, for example, (docker-compose up -d rtm-timescale) are instead (docker-compose up -d antwerp-timescale). 

# Volumes
In the .env file, there are two types of volumes: data volumes, which are by default configured at media/aqua/... and can be modified anywhere the admin wants to store the data, and the config volumes, which are mapped at ./confs/... and point to specific configuration. If these need to be changed, please move the corresponding configuration files as well; otherwise, the containers won't fetch the configuration correctly.

## Usage
Build the images:
```
docker-compose build
```
Run the containers:
```
docker-compose up
```
Run the nginx proxy:
```
docker compose -f .\docker-compose-proxy.yml  up -d
```
# Dependencies
Ports 80 and 443 open in the machine and network.

Docker engine and compose installed in the machine
https://docs.docker.com/engine/
https://docs.docker.com/compose/

# Contributors
The current mantainers of the project are:

- [Pol Escolà](pol.escola@eurecat.org)
- [Didac Colominas](didac.colominas@eurecat.org)
- [Robert Sanfeliu](robert.sanfeliu@eurecat.org)

Copyright 2024 Eurecat
