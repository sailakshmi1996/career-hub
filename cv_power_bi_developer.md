# SAI LAKSHMI ELUSURI
**SENIOR POWER BI DEVELOPER | SEMANTIC MODELING, DAX, SQL & MICROSOFT FABRIC**

**Location:** Utrecht region, Netherlands  
**Email:** sailakshmi.elusuri@gmail.com | **WhatsApp / Mobile:** +91 8142674401  
**LinkedIn:** [linkedin.com/in/sailakshmielusuri-data-analyst](https://www.linkedin.com/in/sailakshmielusuri-data-analyst/) | **Portfolio:** [sailakshmi1996.github.io/career-hub](https://sailakshmi1996.github.io/career-hub/) | **Code:** [github.com/sailakshmi1996/career-hub](https://github.com/sailakshmi1996/career-hub/tree/main/technical-showcase)  

> **Dutch Work Authorization:** Utrecht region, Netherlands. Full unrestricted Dutch labor market access under official IND endorsement: *"Arbeid vrij toegestaan, TWV niet vereist"* (no employer sponsorship or TWV work permit required; immediate Dutch contract start).

---

## PROFESSIONAL SUMMARY
**PL-300 & DP-600 certified Senior Power BI Developer** with **8+ years of enterprise experience** across sustainability, financial risk, and operations. Specializes in Kimball star-schema modeling, DAX & VertiPaq optimization, Oracle/SQL Server incremental pipelines, and Microsoft Fabric (OneLake, Direct Lake, PySpark). Documented impact: **up to 40% faster report loads**, **35% model memory shrink**, **45% lower refresh latency**, and **€350K+ in annual BI license savings**.

---

## TECHNICAL & ANALYTICAL COMPETENCIES
- **Microsoft Certifications:** Fabric Analytics Engineer (DP-600) · Power BI Data Analyst (PL-300) · Azure Data (DP-900) · Azure Fundamentals (AZ-900) · Azure AI (AI-900)
- **Power BI & Semantic Modeling:** Power BI Desktop & Service, DAX (Calculation Groups, Time Intelligence, Semi-Additive Patterns), Power Query (M), Kimball Star Schema, Composite Models, Paginated Reports (RDL), Dynamic RLS (`USERPRINCIPALNAME()`), Field Parameters
- **Tuning, DevOps & Governance:** Tabular Editor 3, DAX Studio, VertiPaq Analyzer, XMLA Endpoint, ALM Toolkit, Power BI Deployment Pipelines (Dev/Test/Prod), Azure DevOps & Git CI/CD, Microsoft Purview Lineage, Power BI REST API
- **Microsoft Fabric & Cloud Data:** Microsoft Fabric (OneLake, Lakehouse, Direct Lake Mode, Dataflows Gen2, Fabric Copilot), Python & PySpark Notebooks, Delta Parquet (V-Order), Medallion Architecture (Bronze/Silver/Gold), Azure Data Factory (ADF), ADLS Gen2, dbt Core (awareness)
- **Databases & Query Engineering:** Oracle SQL DB, Microsoft SQL Server (T-SQL), Sargable CTEs, Analytical Window Functions (`ROW_NUMBER`, `DENSE_RANK`, `RANK`), Incremental Refresh Folding, Partitioned Views, Indexing
- **Migration & Process Analytics:** Qlik Sense to Power BI Migration (Set Analysis to DAX), Celonis Process Mining, Jira, Confluence, ServiceNow, Agile / Scrum

---

## PROFESSIONAL EXPERIENCE

### **Senior Data Analyst | Apexon**
*Apr 2026–Present | Enterprise Analytics Division (Remote)*
- **Automated Oracle-to-Power BI Pipelines:** Engineered automated ingestion connecting Oracle SQL DB into Power BI Service using DirectQuery and incremental refresh partitions, eliminating 30+ hours/month of manual exports and reducing refresh latency by 45%.
- **Sargable Oracle Query Tuning:** Refactored nested database subqueries into sargable CTEs, window functions (`ROW_NUMBER`, `DENSE_RANK`), and partitioned views to preserve query folding, cutting staging query runtimes by 35%.
- **PL-300 Semantic Layer & Fabric Readiness:** Architected Kimball star-schema semantic models with DAX Calculation Groups and VertiPaq tuning across 30+ operational reports, alongside OneLake / Direct Lake evaluation patterns for high-volume datasets.
- **Stakeholder KPI Adoption:** Partnered with product, finance, and operations leadership to standardize KPI definitions and run enablement workshops, driving a 40% increase in weekly active report usage.

### **Power BI Developer | Accenture**
*February 2022 – April 2026 | Hyderabad, India*
- **Enterprise Sustainability Analytics:** Delivered 15+ governed Power BI scorecards for 200+ stakeholders across 5 international business units, translating sustainability and ESG metrics into certified star-schema semantic models.
- **VertiPaq & DAX Performance Engineering:** Replaced flat tables and bi-directional filters with 1:* star schemas, integer surrogate keys, and `KEEPFILTERS` DAX patterns via DAX Studio and Tabular Editor — cutting dashboard load times by up to 40% and memory footprint by up to 35%.
- **Qlik Sense-to-Power BI Consolidation:** Coordinated migration of 50+ legacy Qlik Sense reporting assets into standardized Power BI semantic models, converting Qlik set analysis to DAX and eliminating €350K+ in annual licensing spend.
- **Azure Medallion & Governance:** Built Azure Data Factory (ADF) pipelines loading Bronze/Silver/Gold ADLS Gen2 assets and enforced dynamic Row-Level Security (RLS) across multi-country organizational units.
- **Process Intelligence & Agile Delivery:** Integrated Celonis process-mining telemetry into Power BI bottleneck dashboards and owned sprint execution, risk logs, and UAT handoffs in Jira, Confluence, and ServiceNow.

### **Data Risk Analyst | Genpact**
*April 2021 – January 2022 | Noida, India*
- **Mortgage Portfolio Risk Reporting:** Built 8 SQL Server-backed Power BI dashboards monitoring underwriting compliance and loss metrics across a €2B+ mortgage insurance portfolio, replacing 20+ hours/week of manual reporting.
- **Automated T-SQL Reconciliation:** Authored stored procedures and validation tie-out checks across transactional source tables, guaranteeing 100% reconciliation between core ledgers and executive risk scorecards.
- **Credit Concentration Insights:** Partnered with underwriting committees to implement drill-through exposure views supporting credit risk reviews and regulatory audit defense.

### **Data Analyst | Conduent**
*June 2018 – April 2021 | Visakhapatnam, India*
- **Operational Reporting Automation:** Replaced manual spreadsheet packs with automated Power BI suites, saving 60+ person-hours monthly and eliminating cross-team reporting discrepancies.
- **SQL Staging Optimization:** Authored 40+ T-SQL views, CTEs, and stored procedures across enterprise databases, increasing staging throughput by 35% for monthly financial close reporting.
- **SLA Performance Visibility:** Modeled operational queue bottlenecks and billing accuracy scorecards that helped management raise SLA compliance from 91% to 98%.

---

## SELECTED ARCHITECTURE & ENGINEERING DEEP-DIVES

### **1. VertiPaq Storage Engine & Calculation Group Refactor | Accenture**
*Stack: Power BI, Tabular Editor 3, DAX Studio, VertiPaq Analyzer, Dynamic RLS*
- Split high-cardinality timestamps into integer `DateKey` / `TimeKey` fields and removed unused GUID columns to reclaim 35% RAM.
- Consolidated redundant YTD/PY/YoY and multi-currency measures into reusable DAX Calculation Groups with `KEEPFILTERS`.

### **2. Partition-Folded Oracle Ingestion & OneLake Gold Pipeline | Apexon & Showcase**
*Stack: Oracle SQL DB, Power BI Incremental Refresh, Deployment Pipelines, Microsoft Fabric PySpark (V-Order)*
- Kept `transaction_timestamp` predicates sargable against `RangeStart`/`RangeEnd` parameters with `ROW_NUMBER()` deduplication so Power BI folds partitions cleanly without OLTP locks.
- Designed Medallion Gold Delta Parquet tables using PySpark with write-time V-Order sorting and Z-Ordering (`DateKey`, `CustomerKey`) for Direct Lake memory paging with graceful DirectQuery fallback.

### **3. Celonis Process Mining & End-to-End SLA Telemetry | Accenture**
*Stack: Celonis Event Logs, Power BI Service, SQL Server, Jira / ServiceNow*
- Integrated Celonis activity-event telemetry into operational Power BI scorecards, exposing rework loops and approval bottlenecks across multi-region enterprise workflows.

---

## EDUCATION & LANGUAGES
- **Bachelor of Technology (B.Tech.) in Computer Science & Engineering** — Raghu Engineering College, India | 2017
- **English:** Professional working proficiency (C1) | **Dutch:** Elementary (A1 — actively learning toward B1 integration) | **Telugu:** Native | **Hindi:** Conversational
