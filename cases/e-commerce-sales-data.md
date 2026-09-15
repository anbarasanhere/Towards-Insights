---
case_id: e-commerce-sales-data
title: E commerce sales data
created: 2026-09-15T08:09:44.683540+00:00
updated: 2026-09-15T08:09:44.683540+00:00
domain: Retail E-commerce
status: reviewed
columns:
  - OrderID
  - CustomerID
  - OrderDate
  - ProductID
  - Quantity
  - Discount
  - PaymentMethod
  - Status
  - Age
  - City
  - SignupDate
  - CustomerSegment
  - ProductName
  - Category
  - UnitPrice
  - Sales
  - OrderValue
---

# E commerce sales data

**Business domain:** Retail E-commerce

## Data Overview

This dataset is a retail e-commerce order log capturing completed transactions, customer demographics, and product attributes. Each row represents a single order line linked to individual customer profiles and items across various product categories. Key quantitative fields track quantities, discounts, sales, and order values. Customer attributes include demographics such as age and city, while categorical fields encompass payment methods and order statuses. Initial quality checks reveal potential issues such as inconsistent date formats and the presence of redundant or unclear fields like 'Sales' and 'OrderValue', which may lead to confusion in analysis.

The dataset provides insights into customer purchasing behavior and product performance in an e-commerce environment.

**Likely grain:** Order line level

### Field Roles
- Identifier
- Dimension
- Measure
- Categorical

### Quality Checks
- Inconsistent date formats (DD/MM/YY vs. MM/DD/YY)
- Redundant fields (Sales and OrderValue)
- Potential for missing customer demographic data

### Measures
- Quantity
- Discount
- Sales
- OrderValue

### Dimensions
- OrderID
- CustomerID
- OrderDate
- ProductID
- PaymentMethod
- Status
- Age
- City
- SignupDate
- CustomerSegment
- ProductName
- Category
- UnitPrice

### Time Fields
- OrderDate
- SignupDate

### Analytical Opportunities
- Customer lifetime value analysis based on order history
- Product performance tracking across different categories
- Segmentation of customers based on demographics and purchasing behavior

### Limitations
- Limited historical data for trend analysis
- Potential biases in customer segmentation
- Inconsistent data entry for categorical fields

## Core Entities
- Order
- Customer
- Product

## Relationships
- An Order is linked to a Customer through CustomerID.
- An Order contains one or more Products identified by ProductID.

## Assumptions
- All orders are completed or returned, with no pending statuses.
- Customer demographics are accurately captured at the time of signup.

## Key Metrics & KPIs

### 1. What is the average order value per customer?

**WHY it matters:** To assess customer spending behavior.

**HOW to compute:** Calculate the average of OrderValue grouped by CustomerID.

**WHAT to visualize:** Average OrderValue

### 2. What percentage of orders are returned?

**WHY it matters:** To evaluate product satisfaction and return rates.

**HOW to compute:** Calculate the ratio of returned orders to total orders.

**WHAT to visualize:** Return Rate

## Customer & Behavioral Segmentation

### 1. How does purchasing behavior vary by customer age?

**WHY it matters:** To tailor marketing strategies to different age groups.

**HOW to compute:** Analyze OrderValue and Quantity by age brackets.

**WHAT to visualize:** Purchasing behavior by age

### 2. What are the most common payment methods used by different customer segments?

**WHY it matters:** To optimize payment options and enhance customer experience.

**HOW to compute:** Count occurrences of PaymentMethod grouped by CustomerSegment.

**WHAT to visualize:** Payment method distribution by segment

## Operational Efficiency

### 1. What is the average time taken from order placement to delivery?

**WHY it matters:** To improve logistics and customer satisfaction.

**HOW to compute:** Calculate the time difference between OrderDate and a hypothetical delivery date.

**WHAT to visualize:** Average delivery time

### 2. How does discounting affect sales volume?

**WHY it matters:** To understand the impact of promotions on sales.

**HOW to compute:** Analyze the correlation between Discount and Quantity sold.

**WHAT to visualize:** Sales volume impact by discount
