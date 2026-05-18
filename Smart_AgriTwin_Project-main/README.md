# Smart AgriTwin

Distributed Computing Project
CENG 465
Version 1.0.0

Smart AgriTwin is a distributed REST-based digital twin system developed for modern agriculture.
The system simulates IoT sensor telemetry, processes environmental data, evaluates rule-based
conditions, generates alerts, and provides real-time visualization through a lightweight web interface.

The project focuses on modeling digital twins of vertical farming zones using a modular backend
architecture with extensible APIs, rule automation, authentication, and data visualization.

---

## Project Structure

smart-agritwin/

* backend/

  * app/

    * **init**.py        Application factory and blueprint registration
    * config.py          System configuration (PostgreSQL, JWT)
    * models.py          SQLAlchemy models
    * rule_engine.py     Rule evaluation and automation logic
    * auth.py            Authentication and authorization
    * api/

      * farms.py
      * zones.py
      * devices.py       Device management and status endpoint
      * telemetry.py     Telemetry ingest and query endpoints
      * rules.py
      * alerts.py        Alert generation and acknowledgment
      * commands.py      Actuator command logging
      * reports.py       Resource usage reports
      * dashboard.py     System-level statistics
  * migrations/          Database migrations
  * run.py               Application entry point

* frontend/

  * zone_detail.html     Zone-level visualization
  * assets/

* mock_clients/

  * simulate_telemetry.py

* docker-compose.yml

* Dockerfile

* schema.sql

* README.md

---

## Database Schema

The database schema for the Smart AgriTwin system is provided in `schema.sql`.
This file contains all table definitions, relationships, and indexes required to initialize
the PostgreSQL database.

### Initialize the Database

Ensure PostgreSQL is running and a target database has been created, then execute:

```bash
psql -U postgres -d agritwin -f schema.sql
```

This will create all required tables including users, farms, zones, devices, telemetry,
alerts, and commands.

---

## Telemetry Ingestion

Simulated IoT devices send telemetry data including temperature, humidity, and soil moisture
to the system using the telemetry ingestion endpoint.

POST /api/telemetry/ingest

---

## Digital Twin Representation

Each zone maintains a digital twin state consisting of:

* Latest telemetry data
* Last seen timestamp
* Device connectivity status
* Environmental condition snapshot

---

## Rule Engine

Rules are evaluated automatically whenever telemetry data is received.
The rule engine supports:

* Comparison operators
* Logical operators
* Nested conditions
* Payload-based expressions

When a rule condition is satisfied, an alert is generated and stored.

---

## Alerts

The alert system allows:

* Retrieving active (unacknowledged) alerts
* Acknowledging alerts

Endpoints:

* GET /api/alerts/active
* POST /api/alerts/ack/<id>

---

## Device Status Monitoring

Device connectivity is determined based on the last telemetry timestamp.
Devices are considered online if they have sent telemetry within the last 30 seconds.

GET /api/devices/status

---

## Zone Visualization

The zone detail page provides:

* Real-time telemetry visualization
* Latest sensor values
* Historical telemetry data

Data is retrieved via the telemetry history endpoint.

---

## Resource Usage Reports

The system provides analytical reports including:

* Estimated water usage
* Estimated energy consumption
* Environmental averages
* Device and zone statistics

GET /api/reports/resource-usage

---

## System Dashboard

A system-wide dashboard endpoint provides:

* Counts of farms, zones, and devices
* Alert statistics
* Online and offline device counts
* Global telemetry summaries

GET /api/dashboard/stats

---

## Authentication

JWT-based authentication is used to protect sensitive endpoints.

Endpoints:

* POST /api/auth/register
* POST /api/auth/login

---

## Authors

Fatıma Zehra Özyürek
Database design, telemetry simulation, alert visualization, deployment, testing

Hirad Khademian
Core API development, rule engine, authentication, digital twin logic
