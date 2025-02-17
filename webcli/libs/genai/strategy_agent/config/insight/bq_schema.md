# BigQuery Table Annotations for text2SQL

## Overview
This document provides structured annotations for the `mart` dataset in BigQuery, which is used for text2SQL tasks. The dataset `mart` is located in the project `velvety-outcome-448307-f0` and contains various tables related to BOM structures, companies, customers, finished goods, items, production lines, materials, forecasts, routings, storages, transactions, and versions.

## Table Descriptions and Schema
- descriptions of version code
  - V001: ordinal scenario, which is a basic scneario compared by the other scenarios
  - V002: disaster, which is a result of the disaster.
  - V003: prediction of kansai, which is a inferenced scenario comparing to ordinal one.
  - V003: prediction of kyushu, which is a inferenced scenario comparing to ordinal one.

### 1. `mart.bom_trees`
- **Description**: Represents Bill of Materials (BOM) hierarchy with parent-child relationships.
- **Schema**:
  - `parent_item_code` (STRING): Code for the parent item.
  - `child_item_code` (STRING): Code for the child item.
  - `quantity` (INTEGER): Quantity of child item required.
  - `is_active` (BOOLEAN): Whether the relationship is active.
  - `version` (STRING): BOM version identifier.

### 2. `mart.companies`
- **Description**: Stores information about companies.
- **Schema**:
  - `company_code` (STRING): Unique code for the company.
  - `company_name` (STRING): Name of the company.

### 3. `mart.customers`
- **Description**: Stores information about customers.
- **Schema**:
  - `customer_code` (STRING): Unique code for the customer.
  - `customer_name` (STRING): Name of the customer.

### 4. `mart.finished_goods`
- **Description**: Represents finished goods and their details.
- **Schema**:
  - `finished_goods_code` (STRING): Unique code for the finished good.
  - `finished_goods_name` (STRING): Name of the finished good.
  - `item_code` (STRING): Associated item code.
  - `item_type` (STRING): Type of item.
  - `finished_goods_volume` (FLOAT): Volume of the finished good.

### 5. `mart.items`
- **Description**: Stores item information.
- **Schema**:
  - `item_id` (INTEGER): Unique identifier for the item.
  - `item_type` (STRING): Type of the item.
  - `resource_code` (STRING): Resource associated with the item.

### 6. `mart.lines`
- **Description**: Represents production lines with capacity and cost information.
- **Schema**:
  - `time_id` (STRING): Time identifier.
  - `version` (STRING): Version identifier.
  - `location_code` (STRING): Code for the location.
  - `location_name` (STRING): Name of the location.
  - `plant_code` (STRING): Code for the plant.
  - `plant_name` (STRING): Name of the plant.
  - `line_code` (STRING): Unique identifier for the production line.
  - `line_name` (STRING): Name of the production line.
  - `capacity` (INTEGER): Production capacity.
  - `production_cost` (INTEGER): Cost of production.

### 7. `mart.materials`
- **Description**: Stores material-related data.
- **Schema**:
  - `material_code` (STRING): Unique identifier for the material.
  - `material_name` (STRING): Name of the material.
  - `item_code` (STRING): Associated item code.
  - `item_type` (STRING): Type of item.
  - `material_volume` (FLOAT): Volume of the material.

### 8. `mart.production_forecasts`
- **Description**: Forecasted production quantities for items.
- **Schema**:
  - `version` (STRING): Forecast version.
  - `time_id` (STRING): Time identifier.
  - `line_code` (STRING): Code for the production line.
  - `item_code` (STRING): Code for the item.
  - `quantity` (INTEGER): Forecasted quantity.

### 9. `mart.resource_forecasts`
- **Description**: Forecasted resource demand by customers.
- **Schema**:
  - `version` (STRING): Forecast version.
  - `time_id` (STRING): Time identifier.
  - `customer_code` (STRING): Code for the customer.
  - `item_code` (STRING): Code for the item.
  - `quantity` (INTEGER): Forecasted quantity.

### 10. `mart.sales_forecasts`
- **Description**: Forecasted sales data.
- **Schema**:
  - `version` (STRING): Forecast version.
  - `time_id` (STRING): Time identifier.
  - `company_code` (STRING): Company code.
  - `customer_code` (STRING): Customer code.
  - `item_code` (STRING): Item code.
  - `quantity` (INTEGER): Forecasted quantity.

### 11. `mart.transactions`
- **Description**: Logs various transactions.
- **Schema**:
  - `time_id` (STRING): Time identifier.
  - `company_code` (STRING): Company code.
  - `customer_code` (STRING): Customer code.
  - `item_code` (STRING): Item code.
  - `transaction_type` (STRING): Type of transaction.
  - `storage_code` (STRING): Storage code.
  - `price` (INTEGER): Price per unit.
  - `quantity` (INTEGER): Quantity of the transaction.
  - `version` (STRING): Transaction version.

### 12. `mart.versions`
- **Description**: Stores versioning information.
- **Schema**:
  - `version_code` (STRING): Unique version identifier.
  - `version_name` (STRING): Name of the version.
  - `is_active` (BOOLEAN): Whether the version is active.

### 13. `mart.routings`
- **Description**: Stores routing information between plants.
- **Schema**:
  - `routings_code` (STRING): Unique routing identifier.
  - `from_plants_code` (STRING): Code for the origin plant.
  - `to_plants_code` (STRING): Code for the destination plant.
  - `routings_name` (STRING): Name of the routing.
  - `from_plants_name` (STRING): Name of the origin plant.
  - `to_plants_name` (STRING): Name of the destination plant.
  - `routing_leadtime` (INTEGER): Lead time for the routing.
  - `routing_unit_cost` (INTEGER): Cost per unit.
  - `is_active` (BOOLEAN): Whether the routing is active.
  - `version` (STRING): Routing version.

### 14. `mart.routing_forecasts`
- **Description**: Forecasted routing information for items.
- **Schema**:
  - `version` (STRING): Forecast version.
  - `time_id` (STRING): Time identifier.
  - `routings_code` (STRING): Code for the routing.
  - `routings_name` (STRING): Name of the routing.
  - `from_plants_code` (STRING): Origin plant code.
  - `to_plants_code` (STRING): Destination plant code.
  - `item_code` (STRING): Code for the item.
  - `quantity` (FLOAT): Quantity routed.
  - `cost` (FLOAT): Routing cost.
  - `unit_cost` (INTEGER): Cost per unit.

### 15. `mart.storages`
- **Description**: Storage data for different locations.
- **Schema**:
  - `time_id` (STRING): Time identifier.
  - `version` (STRING): Storage version.
  - `location_code` (STRING): Location code.
  - `location_name` (STRING): Location name.
  - `plant_code` (STRING): Plant code.
  - `plant_name` (STRING): Plant name.
  - `storage_code` (STRING): Storage identifier.
  - `storage_name` (STRING): Storage name.
  - `item_code` (STRING): Item code.
  - `target_quantity` (INTEGER): Target quantity.
  - `storage_unit_cost` (INTEGER): Storage cost per unit.
  - `longitude` (FLOAT): Longitude.
  - `latitude` (FLOAT): Latitude.

### 16. `mart.times`
- **Description**: Stores time-related metadata.
- **Schema**:
  - `time_id` (STRING): Unique time identifier.
  - `year` (INTEGER): Year value.
  - `year_name` (INTEGER): Name of the year.
  - `month` (INTEGER): Month value.
  - `month_name` (STRING): Name of the month.
  - `date` (INTEGER): Date value.
  - `date_name` (STRING): Name of the date.

