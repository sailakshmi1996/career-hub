// data.js - Structured Knowledge Base Data for SynapseArchitect Website

const SYNAPSE_DATA = {
  architectures: [
    {
      id: "mdw",
      name: "Modern Data Warehouse (MDW)",
      description: "The classic architectural pattern for Enterprise BI and structured reporting. It decouples storage from compute, moving data sequentially from raw ingest to a structured relational serving layer.",
      diagram: [
        { id: "sources", label: "Data Sources", type: "source", desc: "On-premises databases, APIs, SaaS applications, and logs." },
        { id: "pipelines", label: "Synapse Pipelines", type: "process", desc: "Data orchestration engine (ADF tech) copy activities and data flows." },
        { id: "datalake", label: "ADLS Gen2 Storage", type: "storage", desc: "Organized into raw, cleaned, and curated storage zones." },
        { id: "sqlpool", label: "Dedicated SQL Pool", type: "compute", desc: "Enterprise relational data warehouse utilizing MPP (Massive Parallel Processing)." },
        { id: "powerbi", label: "Power BI", type: "client", desc: "Interactive executive dashboards and analytical reports." }
      ],
      flow: [
        "1. Ingest: Synapse Pipelines ingest structured and unstructured data from source systems.",
        "2. Store: Ingested files land in Azure Data Lake Storage Gen2 (organized by raw, clean, curated folders).",
        "3. Prep & Clean: Mapping data flows transform and clean raw data, writing conformed Parquet files back to curated folders.",
        "4. Load: Data is loaded into tables inside a Dedicated SQL Pool using high-performance T-SQL COPY commands.",
        "5. Visualize: Analysts query the Dedicated SQL Pool using Power BI with high concurrency."
      ]
    },
    {
      id: "medallion",
      name: "Medallion (Delta Lakehouse)",
      description: "An open architecture pattern that logically organizes data lake storage into three progressive quality tiers, introducing ACID transaction safety, versioning, and schema enforcement to files.",
      diagram: [
        { id: "bronze", label: "Bronze (Raw)", type: "storage", desc: "Immutable, append-only raw data directly from source systems." },
        { id: "spark", label: "Synapse Spark Pools", type: "process", desc: "Applies validation, cleaning, and business transformations via notebooks." },
        { id: "silver", label: "Silver (Cleaned)", type: "storage", desc: "Standardized, conformed Delta tables for enterprise-wide analysis." },
        { id: "gold", label: "Gold (Curated)", type: "storage", desc: "Aggregated star schema models optimized for reporting and business logic." },
        { id: "serverless", label: "Serverless SQL Pool", type: "compute", desc: "Pay-per-query engine providing instant SQL views of Gold files without data replication." }
      ],
      flow: [
        "1. Bronze Layer: Raw data lands in its original format, acting as the system of record.",
        "2. Silver Transformation: Spark jobs clean, de-duplicate, and standardize data, writing to Delta format.",
        "3. Gold Aggregations: Advanced business transformations apply aggregation logic and save files as star schemas.",
        "4. Logical DW: Serverless SQL pools expose Gold files as SQL views, avoiding the cost of a dedicated SQL pool."
      ]
    },
    {
      id: "lambda",
      name: "Real-Time / Streaming (Lambda)",
      description: "Processes both high-velocity real-time event streaming streams (hot path) and massive batch historical datasets (cold path) concurrently for real-time dashboard visibility.",
      diagram: [
        { id: "telemetry", label: "IoT / App Events", type: "source", desc: "Real-time telemetry, clickstreams, and application event feeds." },
        { id: "eventhub", label: "Azure Event Hubs", type: "ingest", desc: "High-throughput real-time ingestion queue." },
        { id: "hotpath", label: "Azure Stream Analytics", type: "process", desc: "Hot Path: Low-latency query engine evaluating sliding time-windows." },
        { id: "coldpath", label: "Event Hubs Capture", type: "storage", desc: "Cold Path: Automatically archives raw streams to ADLS Gen2 files." },
        { id: "serving", label: "Dedicated SQL Pool", type: "compute", desc: "Serves conformed batch data alongside low-latency streaming aggregations." },
        { id: "dash", label: "Real-Time Power BI", type: "client", desc: "Dynamic dashboards displaying instant alerts and historical trends." }
      ],
      flow: [
        "1. Capture: Event Hubs acts as the ingestion broker, splitting data into real-time streams and static files.",
        "2. Hot Path: Stream Analytics reads streams, executes aggregations, and dumps to SQL Pools within 30 seconds.",
        "3. Cold Path: Raw events are saved to ADLS Gen2 and processed weekly via Synapse Spark for historical deep-dives.",
        "4. Serve: Query views combine the stream tables and batch tables for a complete analytical dataset."
      ]
    },
    {
      id: "hubspoke",
      name: "Enterprise Hub-and-Spoke",
      description: "Maintains federated governance across multiple business departments. A centralized IT hub controls network, security, and cataloging, while autonomous spokes host Synapse workspaces.",
      diagram: [
        { id: "hubvnet", label: "Central Hub VNet", type: "network", desc: "Contains Firewall, VPN gateways, DNS, and Microsoft Purview for centralized governance." },
        { id: "peering", label: "VNet Peering", type: "network", desc: "Secure private peering connecting networks without public exposure." },
        { id: "spoke1", label: "Finance Spoke", type: "compute", desc: "Isolated workspace running Dedicated SQL Pools with domain-specific pipelines." },
        { id: "spoke2", label: "Retail Spoke", type: "compute", desc: "Isolated workspace running Spark pools for customer analytics." },
        { id: "purview", label: "Microsoft Purview", type: "governance", desc: "Scans all workspaces to compile global data catalogs and security policy enforcement." }
      ],
      flow: [
        "1. Central Governance: Central IT establishes the Hub, containing the global security rules and Purview catalogs.",
        "2. Spoke Provisioning: Departments receive independent subscriptions and Synapse workspaces connected via VNet peering.",
        "3. Autonomous Delivery: Teams build their own data products using their dedicated Spark or SQL pools.",
        "4. Federated Cataloging: Purview automatically crawls the spokes to map cross-workspace data lineage."
      ]
    }
  ],
  components: [
    {
      name: "Dedicated SQL Pools",
      icon: "database",
      details: "High-performance data warehouse employing MPP (Massive Parallel Processing). Detaches compute from storage and splits tables into 60 distinct distributions to optimize parallel queries.",
      bestPractices: [
        "Rebuild Clustered Columnstore Indexes (CCI) regularly to eliminate fragmented rowgroups.",
        "Use Replicated distribution for small dimension tables under 2GB to eliminate DMS data movement.",
        "Update statistics manually after major ETL runs to ensure the query optimizer builds efficient plans."
      ]
    },
    {
      name: "Serverless SQL Pools",
      icon: "cloud",
      details: "Pay-per-query schema-on-read engine. Charges based on data scanned ($5.00/TB). Instantly reads Parquet, CSV, JSON, and Delta Lake files directly from storage.",
      bestPractices: [
        "Select Parquet format over CSV to reduce file sizes, speed up query rates, and cut data scan costs by up to 80%.",
        "Utilize folder-based partitioning and query using filepath() to prune directories and avoid scanning unrelated files.",
        "Avoid using SELECT *; explicitly define target columns to scan only what is needed."
      ]
    },
    {
      name: "Apache Spark Pools",
      icon: "terminal",
      details: "Managed Apache Spark engine with rapid startup, auto-scaling nodes, and auto-pause capabilities. Built-in support for Delta Lake, Spark SQL, and SynapseML library.",
      bestPractices: [
        "Set auto-pause timeout to 10 minutes to avoid paying for idle clusters.",
        "Configure executor nodes to auto-scale dynamically rather than hardcoding a fixed node count.",
        "Use Delta tables to leverage transaction logging, Z-ordering, and time-travel querying."
      ]
    },
    {
      name: "Synapse Pipelines",
      icon: "shuffle",
      details: "Built-in data integration engine derived from Azure Data Factory. Orchestrates complex data pipelines across 90+ connectors and hosts Mapping Data Flows.",
      bestPractices: [
        "Utilize Self-Hosted Integration Runtime (SHIR) to securely bridge on-premises databases with the cloud.",
        "Parameterize linked services and store connection strings inside Azure Key Vault.",
        "Separate orchestration control flows from computational data transformations."
      ]
    }
  ],
  useCases: [
    {
      category: "Retail",
      title: "Customer 360 Profile",
      challenge: "POS, web e-commerce, and loyalty card datasets resided in isolated storage silos, preventing targeted marketing.",
      solution: "Synapse Pipelines copy records from all platforms into ADLS Gen2. Spark pools cleanse and join profiles into unified gold Delta tables, queried by Power BI.",
      impact: "Reduced query latencies for unified profile analysis from 6 hours to 4 seconds, increasing marketing conversion rates by 18%."
    },
    {
      category: "Manufacturing",
      title: "OEE & Predictive Maintenance",
      challenge: "Cell factory machine sensors produced millions of real-time events that overloaded operational databases.",
      solution: "IoT sensor streams route through Event Hubs. Stream Analytics executes anomalies hot path, while Spark batch processes historical logs for health prediction.",
      impact: "Detected machine bearing faults 5 days prior to failure, saving an estimated $80k in unplanned factory downtime per incident."
    },
    {
      category: "Financial Services",
      title: "AML & Fraud Detection",
      challenge: "Legacy databases struggled to execute real-time anti-money laundering (AML) detection patterns at transaction times.",
      solution: "Synapse Link replicates operational database transactions in near real-time without impact. SparkML evaluates fraud models on the operational analytical store.",
      impact: "Suspicious pattern detection latency dropped from 24 hours to under 30 seconds, satisfying regulatory requirements."
    }
  ],
  successStories: [
    {
      company: "ABN AMRO Bank",
      logoText: "AA",
      challenge: "ABN AMRO suffered from massive data latency, requiring weeks to generate regulatory risk reports during financial close.",
      solution: "Unified risk tables inside Synapse Dedicated SQL Pools, loading data via high-performance pipelines from core bank mainframe clusters.",
      result: "Reduced risk calculation runtimes from weeks to under 4 hours, managing datasets exceeding 10 billion rows."
    },
    {
      company: "T-Mobile",
      logoText: "TM",
      challenge: "Struggled to analyze petabytes of real-time 5G network telemetry to isolate cell tower connectivity issues.",
      solution: "Implemented a streaming medallion lakehouse pattern using Event Hubs Capture, ADLS Gen2, and Spark-engineered Delta tables.",
      result: "Enabled network technicians to perform ad-hoc diagnostic queries via Serverless SQL, reducing tower outage diagnostics by 40%."
    }
  ],
  fabricChecklist: [
    { id: 1, title: "Audit SQL Schemas", desc: "Identify Dedicated SQL pool tables and generate DDL scripts. Prepare schema updates matching Fabric Warehouse compatibility rules." },
    { id: 2, title: "Convert Data to Parquet/Delta", desc: "Ensure historical lake data is converted to open-format Delta tables, which can be referenced in Fabric OneLake without data copies." },
    { id: 3, title: "Export Notebooks & Scripts", desc: "Export Spark notebooks (.ipynb) and SQL scripts from Synapse Studio. They can be imported directly into Fabric Workspace environments." },
    { id: 4, title: "Re-point Pipelines", desc: "Map Synapse Pipelines to Fabric Data Factory pipelines, adjusting linked services to point to Fabric endpoints." },
    { id: 5, title: "Migrate BI serving", desc: "Set up Power BI Direct Lake mode to query OneLake Delta files directly, replacing slow DirectQuery import models." }
  ],
  pricingTiers: [
    { tier: "DW100c", computeNodes: 1, distributions: 60, costPerHour: 1.20, costPerMonth: 864.00, fit: "Dev, Sandbox, and Proof of Concept" },
    { tier: "DW500c", computeNodes: 1, distributions: 60, costPerHour: 6.04, costPerMonth: 4348.80, fit: "Small teams and lightweight analytical models" },
    { tier: "DW1000c", computeNodes: 2, distributions: 30, costPerHour: 12.08, costPerMonth: 8697.60, fit: "Mid-sized data warehouses and operational reporting" },
    { tier: "DW5000c", computeNodes: 10, distributions: 6, costPerHour: 60.38, costPerMonth: 43473.60, fit: "Enterprise scales with high concurrency and data size" },
    { tier: "DW30000c", computeNodes: 60, distributions: 1, costPerHour: 362.28, costPerMonth: 260841.60, fit: "Maximum physical hardware capability limits" }
  ]
};

// Export data for browser use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SYNAPSE_DATA;
} else {
  window.SYNAPSE_DATA = SYNAPSE_DATA;
}
