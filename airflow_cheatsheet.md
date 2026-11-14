# Apache Airflow Complete Cheatsheet
### Beginner → Advanced → Architect Level | Version-Agnostic Core + 2.x vs 3.x Notes

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Concepts & Terminology](#2-core-concepts--terminology)
3. [DAG Authoring — Classic vs TaskFlow API](#3-dag-authoring--classic-vs-taskflow-api)
4. [Scheduling — Cron, Intervals & Timetables](#4-scheduling--cron-intervals--timetables)
5. [Operators Reference](#5-operators-reference)
6. [Sensors & Deferrable Operators](#6-sensors--deferrable-operators)
7. [XComs & Task Communication](#7-xcoms--task-communication)
8. [Connections & Hooks](#8-connections--hooks)
9. [Dynamic Task Mapping](#9-dynamic-task-mapping)
10. [DAG Dependencies & Dataset-Driven Scheduling](#10-dag-dependencies--dataset-driven-scheduling)
11. [Executors](#11-executors)
12. [Pools, Queues & Priorities](#12-pools-queues--priorities)
13. [Custom Operators, Hooks & Sensors](#13-custom-operators-hooks--sensors)
14. [Testing DAGs](#14-testing-dags)
15. [Deployment & Configuration](#15-deployment--configuration)
16. [Security — RBAC, Fernet, Secrets](#16-security--rbac-fernet--secrets)
17. [Logging, Monitoring & Alerting](#17-logging-monitoring--alerting)
18. [Kubernetes Executor & KubernetesPodOperator](#18-kubernetes-executor--kubernetespodoperator)
19. [CLI Reference](#19-cli-reference)
20. [REST API Reference](#20-rest-api-reference)
21. [Performance Tuning](#21-performance-tuning)
22. [Best Practices & Anti-Patterns](#22-best-practices--anti-patterns)
23. [Airflow 2.x vs 3.x — Key Differences & Migration](#23-airflow-2x-vs-3x--key-differences--migration)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Airflow Platform                     │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │Webserver │  │Scheduler │  │ Triggerer│  │  Workers  │  │
│  │(Flask +  │  │(DAG parse│  │(Deferred │  │(Executors)│  │
│  │ FAB RBAC)│  │ +schedule│  │ tasks)   │  │           │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬─────┘  │
│       │              │              │               │        │
│       └──────────────┴──────────────┴───────────────┘        │
│                              │                               │
│                    ┌─────────▼─────────┐                     │
│                    │  Metadata Database │                     │
│                    │  (PostgreSQL/MySQL)│                     │
│                    └───────────────────┘                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DAGs Folder │  │ Logs Storage │  │  Plugins Dir │      │
│  │  (py files)  │  │  (local/S3)  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Role | Scales? |
|-----------|------|---------|
| **Webserver** | UI + REST API | Horizontally (stateless) |
| **Scheduler** | Parse DAGs, create DagRuns, schedule TaskInstances | 1 active (HA via DB locking) |
| **Triggerer** | Monitor deferred tasks (asyncio event loop) | Horizontally |
| **Workers** | Execute tasks | Horizontally (Celery/K8s) |
| **Metadata DB** | Source of truth (DAGs, runs, task states) | Scale the DB |
| **DAGs Folder** | Python files defining pipelines | Shared FS or Git-sync |

### Scheduler Loop (Simplified)
```
1. Parse DAG files → populate DagBag
2. For each DAG: check if a new DagRun is due
3. For each DagRun: find tasks whose upstream are done
4. Send eligible TaskInstances to Executor queue
5. Executor reports back state → Scheduler updates DB
```

---

## 2. Core Concepts & Terminology

| Term | Definition |
|------|-----------|
| **DAG** | Directed Acyclic Graph — a workflow definition in Python |
| **DagRun** | A single execution instance of a DAG for a logical date |
| **TaskInstance (TI)** | A single execution of a task within a DagRun |
| **logical_date** | The logical time the DagRun represents (formerly `execution_date`) |
| **data_interval_start** | Start of the data window the run processes |
| **data_interval_end** | End of the data window (= when the run is triggered for fixed intervals) |
| **Operator** | Template for a unit of work |
| **Task** | An instantiated Operator placed in a DAG |
| **Hook** | Interface to an external system (wraps connection logic) |
| **Sensor** | Operator that waits for a condition |
| **XCom** | Cross-task communication mechanism (key-value store in metadata DB) |
| **Connection** | Stored credentials + config for external systems |
| **Variable** | Global key-value store in metadata DB |
| **Pool** | Limit concurrency of a group of tasks |
| **Queue** | Route tasks to specific worker groups (Celery) |
| **SLA** | Service Level Agreement — alert if task takes too long |
| **Timetable** | Custom schedule logic (replaces schedule_interval in 2.2+) |
| **Dataset** | Named logical data asset used for data-aware scheduling (2.4+) |

### Task States (lifecycle)
```
none → scheduled → queued → running → success
                                    ↘ failed → up_for_retry → running...
                                    ↘ up_for_reschedule (sensors)
                                    ↘ skipped
                                    ↘ deferred (async sensors, 2.2+)
                                    ↘ removed
```

---

## 3. DAG Authoring — Classic vs TaskFlow API

### Minimal DAG (both styles)

#### Classic Style
```python
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract():
    return {"rows": 100}

def transform(ti):
    data = ti.xcom_pull(task_ids="extract")
    return {k: v * 2 for k, v in data.items()}

with DAG(
    dag_id="classic_etl",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["example"],
) as dag:

    t_extract = PythonOperator(task_id="extract", python_callable=extract)
    t_transform = PythonOperator(task_id="transform", python_callable=transform)
    t_extract >> t_transform
```

#### TaskFlow API Style
```python
from datetime import datetime
from airflow.decorators import dag, task

@dag(
    dag_id="taskflow_etl",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["example"],
)
def etl_pipeline():

    @task
    def extract() -> dict:
        return {"rows": 100}

    @task
    def transform(data: dict) -> dict:
        return {k: v * 2 for k, v in data.items()}

    @task
    def load(data: dict):
        print(f"Loading: {data}")

    raw = extract()
    transformed = transform(raw)
    load(transformed)

etl_pipeline()
```

### DAG Parameters — Full Reference

```python
with DAG(
    dag_id="full_example",                    # Unique DAG identifier
    description="My pipeline",                # Human-readable description
    schedule="0 6 * * *",                     # Cron / timedelta / None / "@daily" / Dataset
    start_date=datetime(2024, 1, 1),          # First logical date to schedule
    end_date=datetime(2024, 12, 31),          # Stop scheduling after this date
    catchup=False,                            # Don't backfill missed runs
    max_active_runs=1,                        # Max concurrent DagRuns
    max_active_tasks=16,                      # Max concurrent tasks across all runs
    default_args={                            # Default kwargs for all operators
        "owner": "data-team",
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(hours=1),
        "email": ["alert@company.com"],
        "email_on_failure": True,
        "email_on_retry": False,
        "depends_on_past": False,
        "execution_timeout": timedelta(hours=2),
        "on_failure_callback": my_failure_callback,
        "on_success_callback": my_success_callback,
        "on_retry_callback": my_retry_callback,
        "sla": timedelta(hours=1),
    },
    tags=["etl", "finance"],                  # UI filtering tags
    params={                                  # Runtime-configurable params (Params API)
        "env": Param("prod", type="string", enum=["dev","staging","prod"]),
        "batch_size": Param(1000, type="integer", minimum=1, maximum=10000),
    },
    render_template_as_native_obj=True,       # Return Python objects from Jinja templates
    template_searchpath=["/opt/sql"],         # Extra dirs for template files
    on_failure_callback=dag_failure_handler,  # Callback for DAG-level failure
    access_control={"data_team": {"can_read", "can_edit"}},  # RBAC
    is_paused_upon_creation=False,            # Start active (2.2+)
    doc_md="""# My DAG\nThis DAG does XYZ.""", # Markdown docs shown in UI
) as dag:
    ...
```

### Dependency Syntax

```python
# Bitshift operators
t1 >> t2 >> t3          # t1 → t2 → t3
t1 >> [t2, t3]          # t1 → t2 AND t1 → t3 (fan-out)
[t1, t2] >> t3          # t1 → t3 AND t2 → t3 (fan-in)

# Explicit methods
t1.set_downstream(t2)
t2.set_upstream(t1)

# Cross-DAG dependency (not real dependency — just trigger)
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
```

### Jinja Templating — Built-in Variables

```python
# Available in templated fields of operators
"{{ ds }}"                    # logical_date as YYYY-MM-DD
"{{ ds_nodash }}"             # YYYYMMDD
"{{ ts }}"                    # ISO 8601 timestamp
"{{ ts_nodash }}"             # YYYYMMDDTHHmmss
"{{ logical_date }}"          # datetime object
"{{ data_interval_start }}"   # Pendulum datetime
"{{ data_interval_end }}"     # Pendulum datetime
"{{ prev_ds }}"               # Previous run's ds
"{{ next_ds }}"               # Next run's ds
"{{ dag.dag_id }}"            # DAG id string
"{{ task.task_id }}"          # Task id string
"{{ run_id }}"                # DagRun run_id
"{{ var.value.my_var }}"      # Airflow Variable
"{{ var.json.my_var.key }}"   # JSON Variable key
"{{ conn.my_conn.host }}"     # Connection attribute
"{{ macros.ds_add(ds, 7) }}"  # Date macro helpers
"{{ params.env }}"            # DAG Params
"{{ task_instance.xcom_pull(task_ids='t1') }}"  # XCom in template
```

---

## 4. Scheduling — Cron, Intervals & Timetables

### Schedule Presets

| Preset | Equivalent Cron | Description |
|--------|----------------|-------------|
| `"@once"` | — | Run once only |
| `"@continuous"` | — | Run immediately after previous finishes |
| `"@hourly"` | `0 * * * *` | Every hour |
| `"@daily"` | `0 0 * * *` | Midnight daily |
| `"@weekly"` | `0 0 * * 0` | Sunday midnight |
| `"@monthly"` | `0 0 1 * *` | 1st of month |
| `"@yearly"` | `0 0 1 1 *` | Jan 1st |
| `None` | — | No automatic scheduling (manual only) |

### Cron Expression Quick Reference

```
┌─────────── minute (0-59)
│ ┌───────── hour (0-23)
│ │ ┌─────── day of month (1-31)
│ │ │ ┌───── month (1-12)
│ │ │ │ ┌─── day of week (0-7, 0=Sun)
│ │ │ │ │
* * * * *

Examples:
"0 6 * * *"        → 6:00 AM every day
"0 6 * * 1-5"      → 6:00 AM Mon-Fri
"0 */4 * * *"      → Every 4 hours
"30 2 1,15 * *"    → 2:30 AM on 1st and 15th
"0 0 * * 0"        → Midnight every Sunday
```

### timedelta Schedules

```python
from datetime import timedelta

schedule=timedelta(hours=6)     # Every 6 hours
schedule=timedelta(days=1)      # Daily (same as @daily but relative)
schedule=timedelta(weeks=1)     # Weekly
```

### Custom Timetables (2.2+)

```python
from airflow.plugins_manager import AirflowPlugin
from airflow.timetables.base import DagRunInfo, DataInterval, TimeRestriction, Timetable
import pendulum

class WeekdayTimetable(Timetable):
    """Run Mon–Fri at 08:00 UTC only."""

    description = "Weekdays at 08:00 UTC"

    def infer_manual_data_interval(self, run_after: pendulum.DateTime) -> DataInterval:
        start = run_after.start_of("day")
        return DataInterval(start=start, end=run_after)

    def next_dagrun_info(
        self,
        *,
        last_automated_data_interval: DataInterval | None,
        restriction: TimeRestriction,
    ) -> DagRunInfo | None:
        if last_automated_data_interval:
            last_start = last_automated_data_interval.start
            delta = pendulum.duration(days=1)
            next_start = last_start + delta
        else:
            next_start = restriction.earliest
            if next_start is None:
                return None

        # Skip weekends
        while next_start.day_of_week in (pendulum.SATURDAY, pendulum.SUNDAY):
            next_start = next_start.add(days=1)

        next_start = next_start.set(hour=8, minute=0, second=0)
        if restriction.latest and next_start > restriction.latest:
            return None

        return DagRunInfo.interval(
            start=next_start,
            end=next_start + pendulum.duration(days=1),
        )

class WeekdayPlugin(AirflowPlugin):
    name = "weekday_plugin"
    timetables = [WeekdayTimetable]

# Usage in DAG:
with DAG(dag_id="weekday_dag", timetable=WeekdayTimetable(), ...):
    ...
```

### Catchup & Backfill

```bash
# Catchup=True: Airflow auto-creates DagRuns for all missed intervals
# Catchup=False: Only runs from "now" forward

# Manual backfill via CLI
airflow dags backfill \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  my_dag_id

# Backfill with parallelism
airflow dags backfill --start-date 2024-01-01 --end-date 2024-12-31 \
  --max-jobs 4 my_dag_id
```

---

## 5. Operators Reference

### Built-in Operators

#### PythonOperator
```python
from airflow.operators.python import PythonOperator

def my_func(ds, **kwargs):
    print(f"Running for {ds}")
    return "result_value"

task = PythonOperator(
    task_id="my_python_task",
    python_callable=my_func,
    op_kwargs={"extra_param": "value"},   # passed to function
    op_args=[],                            # positional args
    templates_dict={"date": "{{ ds }}"},  # templated dict injected into kwargs
    provide_context=True,                  # deprecated in 2.x (always True now)
)
```

#### BashOperator
```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id="run_script",
    bash_command="python /opt/scripts/process.py --date {{ ds }}",
    env={"MY_VAR": "{{ var.value.my_variable }}"},  # env vars (templated)
    cwd="/opt/scripts",                              # working directory
    append_env=False,                                # if True, merge with system env
    output_encoding="utf-8",
    skip_exit_code=99,                               # exit code that means "skip"
)
```

#### BranchPythonOperator
```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(ds, **kwargs):
    if ds < "2024-06-01":
        return "task_a"          # return task_id or list of task_ids
    return ["task_b", "task_c"] # fan-out branch

branch = BranchPythonOperator(
    task_id="branch",
    python_callable=choose_branch,
)

branch >> [task_a, task_b, task_c]
# non-chosen branches are automatically SKIPPED
```

#### ShortCircuitOperator
```python
from airflow.operators.python import ShortCircuitOperator

def check_condition(ds, **kwargs):
    return True  # False → skip all downstream tasks

short = ShortCircuitOperator(
    task_id="check",
    python_callable=check_condition,
    ignore_downstream_trigger_rules=True,  # True=skip all downstream, False=only direct
)
```

#### EmptyOperator / DummyOperator
```python
from airflow.operators.empty import EmptyOperator  # 2.x
# from airflow.operators.dummy import DummyOperator  # legacy

start = EmptyOperator(task_id="start")
end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")
```

#### EmailOperator
```python
from airflow.operators.email import EmailOperator

send_email = EmailOperator(
    task_id="send_email",
    to=["team@company.com"],
    subject="Pipeline {{ ds }} complete",
    html_content="<h1>Done!</h1><p>Rows processed: {{ ti.xcom_pull('load') }}</p>",
    cc=["manager@company.com"],
    bcc=[],
    files=["/path/to/report.csv"],
    mime_subtype="mixed",
)
```

#### TriggerDagRunOperator
```python
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

trigger = TriggerDagRunOperator(
    task_id="trigger_downstream",
    trigger_dag_id="downstream_dag",
    conf={"source": "upstream_dag", "date": "{{ ds }}"},
    wait_for_completion=True,       # block until triggered DAG finishes
    poke_interval=30,               # seconds between status checks
    reset_dag_run=True,             # re-trigger if DagRun already exists
    allowed_states=["success"],     # states considered OK when waiting
    failed_states=["failed"],
    execution_date="{{ ds }}",      # logical_date for triggered run
)
```

### Trigger Rules

Controls when a task runs relative to its upstream tasks:

| Rule | Trigger Condition |
|------|------------------|
| `all_success` | All upstream tasks succeeded **(default)** |
| `all_failed` | All upstream tasks failed |
| `all_done` | All upstream tasks are done (any state) |
| `all_skipped` | All upstream tasks are skipped |
| `one_success` | At least one upstream succeeded |
| `one_failed` | At least one upstream failed |
| `none_failed` | No upstream failed (success or skipped) |
| `none_failed_min_one_success` | No failed, at least one succeeded |
| `none_skipped` | No upstream was skipped |
| `always` | Always run regardless of upstream |

```python
cleanup = EmptyOperator(
    task_id="cleanup",
    trigger_rule="all_done",  # always runs even if upstream fails
)
```

---

## 6. Sensors & Deferrable Operators

### Classic Sensors

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.time_delta import TimeDeltaSensor
from airflow.sensors.time_sensor import TimeSensor
from airflow.sensors.python import PythonSensor
from airflow.sensors.external_task import ExternalTaskSensor

# FileSensor — wait for a file to appear
wait_file = FileSensor(
    task_id="wait_for_file",
    filepath="/data/input/{{ ds_nodash }}/data.csv",
    poke_interval=60,    # check every 60 seconds
    timeout=3600,        # fail after 1 hour
    mode="poke",         # "poke" or "reschedule"
    soft_fail=False,     # True = skip instead of fail on timeout
    fs_conn_id="fs_default",
)

# ExternalTaskSensor — wait for a task in another DAG
wait_upstream = ExternalTaskSensor(
    task_id="wait_for_upstream",
    external_dag_id="upstream_dag",
    external_task_id="final_task",          # None = wait for whole DAG
    allowed_states=["success"],
    failed_states=["failed", "skipped"],
    execution_date_fn=lambda dt: dt,        # map logical dates
    poke_interval=30,
    timeout=7200,
    mode="reschedule",
)

# PythonSensor — custom condition
def check_api():
    import requests
    r = requests.get("http://api/health")
    return r.status_code == 200

wait_api = PythonSensor(
    task_id="wait_for_api",
    python_callable=check_api,
    poke_interval=30,
    timeout=600,
    mode="reschedule",
)
```

### Sensor Modes Comparison

| Mode | Behavior | Use When |
|------|----------|----------|
| `poke` | Worker slot held during wait | Short waits (< 5 min) |
| `reschedule` | Slot released between checks | Long waits (hours) |
| `deferrable` | Asyncio-based, no worker slot | Many sensors, best efficiency |

### Deferrable Operators (2.2+)

```python
from airflow.sensors.time_delta import TimeDeltaSensorAsync

# Drop-in async replacement — uses Triggerer, releases worker slot
wait = TimeDeltaSensorAsync(
    task_id="wait_5min",
    delta=timedelta(minutes=5),
)

# Building a custom deferrable operator
from airflow.models import BaseOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.exceptions import TaskDeferred
import asyncio

class MyTrigger(BaseTrigger):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def serialize(self):
        return ("my_module.MyTrigger", {"url": self.url})

    async def run(self):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(self.url) as r:
                    if r.status == 200:
                        yield TriggerEvent({"status": "ready"})
                        return
                await asyncio.sleep(30)

class MyDeferrableOperator(BaseOperator):
    def execute(self, context):
        raise TaskDeferred(
            trigger=MyTrigger(url="http://api/ready"),
            method_name="execute_complete",
        )

    def execute_complete(self, context, event):
        return event["status"]
```

---

## 7. XComs & Task Communication

### Basic XCom Push/Pull

```python
# PUSH — via return value (TaskFlow)
@task
def extract() -> dict:
    return {"key": "value"}  # auto-pushed to XCom

# PUSH — explicit (Classic)
def push_fn(ti, **kwargs):
    ti.xcom_push(key="my_key", value={"data": 42})

# PULL — in downstream task
def pull_fn(ti, **kwargs):
    val = ti.xcom_pull(task_ids="extract")          # gets default/return xcom
    val2 = ti.xcom_pull(task_ids="push_task", key="my_key")
    val3 = ti.xcom_pull(task_ids=["t1", "t2"])      # list of values

# PULL — in Jinja template
"{{ ti.xcom_pull(task_ids='extract') }}"
"{{ ti.xcom_pull(task_ids='extract', key='my_key') }}"
```

### XCom Backends

| Backend | Storage | Use Case |
|---------|---------|----------|
| Default (DB) | Metadata DB | Small values (< 48KB recommended) |
| Custom XCom Backend | Any (S3, GCS, etc.) | Large payloads (dataframes, files) |

```python
# Custom XCom backend — store large values in S3
# Set in airflow.cfg or env var:
# AIRFLOW__CORE__XCOM_BACKEND=my_module.S3XComBackend

from airflow.models.xcom import BaseXCom
import json, boto3

class S3XComBackend(BaseXCom):
    PREFIX = "s3://"

    @staticmethod
    def serialize_value(value, **kwargs):
        if isinstance(value, bytes) or len(str(value)) > 10_000:
            key = f"xcom/{kwargs['run_id']}/{kwargs['task_id']}.json"
            boto3.client("s3").put_object(
                Bucket="my-airflow-xcom",
                Key=key,
                Body=json.dumps(value),
            )
            return BaseXCom.serialize_value(f"{S3XComBackend.PREFIX}{key}")
        return BaseXCom.serialize_value(value)

    @staticmethod
    def deserialize_value(result):
        value = BaseXCom.deserialize_value(result)
        if isinstance(value, str) and value.startswith(S3XComBackend.PREFIX):
            s3_key = value[len(S3XComBackend.PREFIX):]
            obj = boto3.client("s3").get_object(Bucket="my-airflow-xcom", Key=s3_key)
            return json.loads(obj["Body"].read())
        return value
```

### TaskFlow Automatic XCom Chaining

```python
@dag(...)
def pipeline():
    @task
    def step1() -> list:
        return [1, 2, 3]

    @task
    def step2(items: list) -> int:
        return sum(items)

    @task
    def step3(total: int):
        print(total)

    step3(step2(step1()))   # XComs wired automatically
```

---

## 8. Connections & Hooks

### Connection Object Fields

| Field | Description |
|-------|-------------|
| `conn_id` | Unique identifier (referenced in operators/hooks) |
| `conn_type` | Type (http, postgres, s3, ssh, etc.) |
| `host` | Hostname or URL |
| `port` | Port number |
| `schema` | Database name / path / schema |
| `login` | Username |
| `password` | Password (encrypted at rest) |
| `extra` | JSON for additional config (e.g., SSL, region) |

### Managing Connections

```bash
# CLI
airflow connections add my_postgres \
  --conn-type postgres \
  --conn-host localhost \
  --conn-port 5432 \
  --conn-login airflow \
  --conn-password secret \
  --conn-schema mydb

airflow connections list
airflow connections get my_postgres
airflow connections delete my_postgres
airflow connections export connections.json

# Environment Variable (override UI)
# Format: AIRFLOW_CONN_<CONN_ID_UPPERCASE>=<URI>
export AIRFLOW_CONN_MY_POSTGRES="postgresql://airflow:secret@localhost:5432/mydb"

# JSON format
export AIRFLOW_CONN_MY_POSTGRES='{
  "conn_type": "postgres",
  "host": "localhost",
  "login": "airflow",
  "password": "secret",
  "port": 5432,
  "schema": "mydb",
  "extra": {"sslmode": "require"}
}'
```

### Using Hooks Directly

```python
from airflow.hooks.base import BaseHook

# Generic connection retrieval
conn = BaseHook.get_connection("my_postgres")
print(conn.host, conn.port, conn.login)

# PostgreSQL Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook

pg_hook = PostgresHook(postgres_conn_id="my_postgres")

# Execute SQL
records = pg_hook.get_records("SELECT id, name FROM users WHERE active = true")
df = pg_hook.get_pandas_df("SELECT * FROM orders WHERE date = %s", parameters=[ds])
pg_hook.run("INSERT INTO logs VALUES (%s, %s)", parameters=["job_a", "success"])

# Bulk load
pg_hook.bulk_load("staging_table", "/path/to/data.csv")

# HTTP Hook
from airflow.providers.http.hooks.http import HttpHook

http_hook = HttpHook(method="GET", http_conn_id="my_api")
response = http_hook.run(endpoint="/api/v1/data", headers={"Authorization": "Bearer token"})
```

### Variables

```python
from airflow.models import Variable

# Get
val = Variable.get("my_var")
json_val = Variable.get("my_json_var", deserialize_json=True)
val_default = Variable.get("missing", default_var="fallback")

# Set
Variable.set("my_var", "new_value")
Variable.set("my_json_var", {"key": "val"}, serialize_json=True)

# Delete
Variable.delete("my_var")

# In templates
"{{ var.value.my_var }}"
"{{ var.json.my_json_var.nested_key }}"

# CLI
airflow variables set my_var "my_value"
airflow variables get my_var
airflow variables list
airflow variables import vars.json
airflow variables export vars.json
```

---

## 9. Dynamic Task Mapping (2.3+)

Dynamically generate tasks at runtime based on data.

### expand() — Basic Fan-Out

```python
from airflow.decorators import dag, task

@dag(schedule="@daily", start_date=datetime(2024, 1, 1), catchup=False)
def dynamic_mapping():

    @task
    def get_files() -> list:
        return ["file_a.csv", "file_b.csv", "file_c.csv"]

    @task
    def process_file(filename: str) -> str:
        # Called once per item in the list
        return f"processed_{filename}"

    files = get_files()
    process_file.expand(filename=files)  # creates 3 mapped task instances

dynamic_mapping()
```

### expand() with Multiple Args

```python
@task
def process(region: str, date: str):
    print(f"Processing {region} for {date}")

# Cartesian product: 2 x 3 = 6 tasks
process.expand(region=["us", "eu"], date=["2024-01", "2024-02", "2024-03"])
```

### partial() + expand() — Fixed + Dynamic Args

```python
@task
def upload(data: dict, bucket: str, prefix: str):
    ...

upload.partial(bucket="my-bucket", prefix="data/").expand(data=get_data())
```

### expand_kwargs() — Dictionary Fan-Out

```python
@task
def process(**kwargs):
    ...

process.expand_kwargs([
    {"region": "us", "env": "prod"},
    {"region": "eu", "env": "staging"},
])
```

### Mapped Task Limits

```python
# airflow.cfg
# [core]
# max_map_length = 1024  # default; max tasks per mapped operator

# Override per-task
process.expand(filename=big_list).override(task_concurrency=5)
```

---

## 10. DAG Dependencies & Dataset-Driven Scheduling

### Dataset Scheduling (2.4+)

```python
from airflow import Dataset

# Producer DAG — declare outputs
raw_data = Dataset("s3://my-bucket/raw/data.csv")
processed = Dataset("postgres://mydb/processed_table")

with DAG("producer", schedule="@daily", ...):
    @task(outlets=[raw_data])          # marks this dataset as updated
    def produce():
        # write to s3://my-bucket/raw/data.csv
        pass

# Consumer DAG — triggered when dataset is updated
with DAG("consumer", schedule=[raw_data, processed], ...):  # waits for BOTH
    @task
    def consume():
        pass

# Multiple datasets (AND logic — all must be updated)
with DAG("multi_consumer", schedule=[dataset_a, dataset_b]):
    ...
```

### ExternalTaskSensor Patterns

```python
# Wait for a specific task in another DAG's run
wait = ExternalTaskSensor(
    task_id="wait_upstream",
    external_dag_id="upstream_dag",
    external_task_id="final_task",
    execution_date_fn=lambda dt: dt.subtract(days=1),  # look at yesterday's run
    mode="reschedule",
    timeout=7200,
    check_existence=True,           # fail fast if DAG/task doesn't exist
)

# Wait for entire DAG (not a specific task)
wait_dag = ExternalTaskSensor(
    task_id="wait_for_dag",
    external_dag_id="upstream_dag",
    external_task_id=None,          # None = whole DAG
)
```

### TriggerDagRunOperator (Fire & Forget vs Wait)

```python
# Fire-and-forget
trigger = TriggerDagRunOperator(
    task_id="trigger",
    trigger_dag_id="child_dag",
    wait_for_completion=False,
)

# Fire and wait
trigger_wait = TriggerDagRunOperator(
    task_id="trigger_and_wait",
    trigger_dag_id="child_dag",
    conf={"parent_run_id": "{{ run_id }}"},
    wait_for_completion=True,
    deferrable=True,               # uses Triggerer instead of polling worker
    poke_interval=30,
)
```

---

## 11. Executors

### Executor Comparison

| Executor | Workers | Best For | Requires |
|----------|---------|----------|---------|
| `SequentialExecutor` | 1 (in-process) | Development / testing | Nothing extra |
| `LocalExecutor` | N processes (same host) | Small teams, single node | PostgreSQL/MySQL |
| `CeleryExecutor` | N separate workers | Multi-node, horizontal scale | Celery + Redis/RabbitMQ |
| `KubernetesExecutor` | 1 pod per task | Isolation, cloud-native | Kubernetes cluster |
| `CeleryKubernetesExecutor` | Mixed | Hybrid (fast + isolated tasks) | Both above |
| `LocalKubernetesExecutor` | Mixed | Dev + prod in same cluster | K8s |

### LocalExecutor Config

```ini
# airflow.cfg
[core]
executor = LocalExecutor
parallelism = 32          # max total concurrent tasks
max_active_tasks_per_dag = 16

[database]
sql_alchemy_conn = postgresql+psycopg2://airflow:pass@localhost/airflow
```

### CeleryExecutor Config

```ini
[core]
executor = CeleryExecutor

[celery]
broker_url = redis://localhost:6379/0
result_backend = db+postgresql://airflow:pass@localhost/airflow
worker_concurrency = 16       # tasks per worker process
worker_prefetch_multiplier = 1
task_acks_late = True         # re-queue if worker dies mid-task
task_track_started = True

[celery_broker_transport_options]
visibility_timeout = 21600    # 6 hours — must be > longest task
```

```bash
# Start Celery worker
airflow celery worker --queues default,high_priority -c 8 -l info

# Start Flower monitoring UI
airflow celery flower --port 5555

# Inspect workers
celery -A airflow.executors.celery_executor inspect active
celery -A airflow.executors.celery_executor inspect stats
```

### KubernetesExecutor Config

```ini
[core]
executor = KubernetesExecutor

[kubernetes]
namespace = airflow
worker_container_repository = my-registry/airflow
worker_container_tag = 2.9.0
kube_config_file = /home/airflow/.kube/config
pod_template_file = /opt/airflow/pod_template.yaml
logs_volume_claim = airflow-logs-pvc
git_sync_container_repository = k8s.gcr.io/git-sync/git-sync
in_cluster = True             # when running inside K8s
delete_worker_pods = True
delete_worker_pods_on_failure = False
worker_pod_pending_fatal_timeout = 300
```

---

## 12. Pools, Queues & Priorities

### Pools — Concurrency Limiting

```python
# Create pool via UI, CLI, or code
# airflow pools set my_pool 5 "Limits DB-heavy tasks"

task = PythonOperator(
    task_id="db_heavy_task",
    python_callable=run_query,
    pool="my_pool",           # assign to pool
    pool_slots=1,             # slots consumed by this task (default=1)
)

# Task using 2 slots (counts as "heavy")
heavy_task = PythonOperator(
    task_id="heavy_task",
    python_callable=heavy_fn,
    pool="my_pool",
    pool_slots=2,
)
```

```bash
# CLI pool management
airflow pools set etl_pool 10 "ETL concurrency limit"
airflow pools list
airflow pools get etl_pool
airflow pools delete etl_pool
airflow pools import pools.json
airflow pools export pools.json
```

### Queues (CeleryExecutor only)

```python
task = BashOperator(
    task_id="gpu_task",
    bash_command="python train.py",
    queue="gpu_queue",        # route to specific worker group
)
```

```bash
# Start worker listening on specific queue
airflow celery worker --queues gpu_queue
airflow celery worker --queues default,etl_queue
```

### Priority & Weight

```python
task = PythonOperator(
    task_id="high_priority",
    python_callable=fn,
    priority_weight=100,          # higher = scheduled first (default=1)
    weight_rule="downstream",     # "downstream" | "upstream" | "absolute"
    # downstream: priority = sum of all downstream task weights
    # upstream:   priority = sum of all upstream task weights
    # absolute:   priority = priority_weight only
)
```

---

## 13. Custom Operators, Hooks & Sensors

### Custom Operator

```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults  # optional in 2.x+

class MyApiOperator(BaseOperator):
    """Calls an HTTP API and stores response in XCom."""

    # Specify which __init__ params support Jinja templating
    template_fields = ("endpoint", "payload")
    template_fields_renderers = {"payload": "json"}  # UI renderer hint
    template_ext = ()
    ui_color = "#e8f7e4"       # task box color in UI
    ui_fgcolor = "#000"

    def __init__(
        self,
        endpoint: str,
        payload: dict,
        http_conn_id: str = "http_default",
        method: str = "POST",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.endpoint = endpoint
        self.payload = payload
        self.http_conn_id = http_conn_id
        self.method = method

    def execute(self, context):
        from airflow.providers.http.hooks.http import HttpHook
        hook = HttpHook(method=self.method, http_conn_id=self.http_conn_id)
        response = hook.run(endpoint=self.endpoint, data=self.payload)
        self.log.info("Response: %s", response.json())
        return response.json()   # auto-pushed to XCom

    def on_kill(self):
        """Called when task is externally killed — cleanup here."""
        self.log.info("Task killed — cleaning up resources")
```

### Custom Hook

```python
from airflow.hooks.base import BaseHook

class MyServiceHook(BaseHook):
    """Hook for MyService API."""

    conn_name_attr = "my_service_conn_id"
    default_conn_name = "my_service_default"
    conn_type = "my_service"
    hook_name = "My Service"

    def __init__(self, my_service_conn_id: str = default_conn_name):
        super().__init__()
        self.my_service_conn_id = my_service_conn_id
        self._client = None

    def get_conn(self):
        if self._client:
            return self._client
        conn = self.get_connection(self.my_service_conn_id)
        import my_service_sdk
        self._client = my_service_sdk.Client(
            host=conn.host,
            port=conn.port,
            token=conn.password,
        )
        return self._client

    def get_data(self, table: str, date: str) -> list:
        client = self.get_conn()
        return client.query(table=table, date=date)
```

### Custom Sensor

```python
from airflow.sensors.base import BaseSensorOperator

class MyJobSensor(BaseSensorOperator):
    """Waits until a job reaches 'completed' state."""

    template_fields = ("job_id",)

    def __init__(self, job_id: str, api_conn_id: str = "my_api", **kwargs):
        super().__init__(**kwargs)
        self.job_id = job_id
        self.api_conn_id = api_conn_id

    def poke(self, context) -> bool:
        from airflow.providers.http.hooks.http import HttpHook
        hook = HttpHook(http_conn_id=self.api_conn_id)
        response = hook.run(f"/jobs/{self.job_id}/status")
        status = response.json()["status"]
        self.log.info("Job %s status: %s", self.job_id, status)
        if status == "failed":
            raise Exception(f"Job {self.job_id} failed!")
        return status == "completed"
```

---

## 14. Testing DAGs

### DAG Integrity Tests

```python
# tests/test_dag_integrity.py
import pytest
from airflow.models import DagBag

@pytest.fixture(scope="module")
def dagbag():
    return DagBag(dag_folder="dags/", include_examples=False)

def test_no_import_errors(dagbag):
    assert not dagbag.import_errors, f"DAG import errors: {dagbag.import_errors}"

def test_dag_count(dagbag):
    assert len(dagbag.dags) > 0

def test_required_tags(dagbag):
    for dag_id, dag in dagbag.dags.items():
        assert dag.tags, f"DAG {dag_id} has no tags"
        assert "owner" in dag.default_args, f"DAG {dag_id} has no owner"

def test_dag_has_retries(dagbag):
    for dag_id, dag in dagbag.dags.items():
        for task in dag.tasks:
            assert task.retries >= 1, f"Task {dag_id}.{task.task_id} has 0 retries"

def test_dag_load_time(dagbag):
    stats = dagbag.dagbag_stats
    for stat in stats:
        assert stat.duration.seconds < 2, f"DAG {stat.file} loads too slowly"
```

### Unit Testing Tasks

```python
# tests/test_my_dag.py
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
from airflow.utils.types import DagRunType

from dags.my_dag import etl_pipeline

@pytest.fixture
def dag():
    return etl_pipeline()

def test_extract_task(dag):
    task = dag.get_task("extract")
    assert task is not None
    assert task.task_type == "PythonOperator"

def test_task_execution(dag):
    dag.clear()
    dag_run = dag.create_dagrun(
        run_type=DagRunType.MANUAL,
        logical_date=datetime(2024, 1, 1),
        state=State.RUNNING,
    )
    task = dag.get_task("extract")
    ti = TaskInstance(task=task, run_id=dag_run.run_id)
    ti.run(ignore_ti_state=True)
    assert ti.state == State.SUCCESS

@patch("dags.my_dag.my_api_call")
def test_extract_with_mock(mock_api, dag):
    mock_api.return_value = {"rows": 42}
    task = dag.get_task("extract")
    result = task.python_callable()
    assert result["rows"] == 42
```

### Pytest Config

```ini
# pytest.ini or pyproject.toml [tool.pytest.ini_options]
[pytest]
env =
    AIRFLOW__CORE__UNIT_TEST_MODE=True
    AIRFLOW__CORE__DAGS_FOLDER=tests/dags
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////tmp/test_airflow.db
filterwarnings =
    ignore::DeprecationWarning
```

```python
# conftest.py — auto-initialize test DB
import pytest
from airflow.utils.db import resetdb, initdb

@pytest.fixture(scope="session", autouse=True)
def initialize_airflow_db():
    resetdb()
    initdb()
```

---

## 15. Deployment & Configuration

### airflow.cfg — Critical Settings

```ini
[core]
dags_folder = /opt/airflow/dags
executor = LocalExecutor
parallelism = 32                  # total concurrent tasks across all DAGs
max_active_tasks_per_dag = 16
max_active_runs_per_dag = 16
load_examples = False
fernet_key = <generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
default_timezone = UTC

[database]
sql_alchemy_conn = postgresql+psycopg2://user:pass@host:5432/airflow
sql_alchemy_pool_size = 5
sql_alchemy_max_overflow = 10
sql_alchemy_pool_recycle = 1800   # recycle connections every 30 min
sql_alchemy_pool_timeout = 30

[scheduler]
dag_dir_list_interval = 30        # seconds between re-scanning DAGs folder
min_file_process_interval = 30    # seconds between re-parsing same file
parsing_processes = 2             # parallel DAG file parsers
catchup_by_default = False
max_dagruns_to_create_per_loop = 10
max_tis_per_query = 512

[webserver]
expose_config = False             # never expose in prod
secret_key = <random string>
base_url = https://airflow.company.com
default_ui_timezone = America/New_York
rbac = True

[logging]
base_log_folder = /opt/airflow/logs
remote_logging = True
remote_log_conn_id = my_s3_conn
remote_base_log_folder = s3://my-logs/airflow
encrypt_s3_logs = True
logging_level = INFO
fab_logging_level = WARN

[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = alert@company.com
smtp_password = <app_password>
smtp_port = 587
smtp_mail_from = airflow@company.com

[api]
auth_backends = airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session
```

### Environment Variables (override airflow.cfg)

```bash
# Pattern: AIRFLOW__{SECTION}__{KEY} (double underscores)
export AIRFLOW__CORE__EXECUTOR=CeleryExecutor
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://..."
export AIRFLOW__CORE__FERNET_KEY="..."
export AIRFLOW__CELERY__BROKER_URL="redis://redis:6379/0"
export AIRFLOW__WEBSERVER__SECRET_KEY="my-secret"
export AIRFLOW__LOGGING__REMOTE_LOGGING=True
export AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER="s3://my-bucket/logs"
```

### Secrets Backends

```bash
# 1. HashiCorp Vault
export AIRFLOW__SECRETS__BACKEND="airflow.providers.hashicorp.secrets.vault.VaultBackend"
export AIRFLOW__SECRETS__BACKEND_KWARGS='{"connections_path":"airflow/connections","variables_path":"airflow/variables","mount_point":"secret","url":"http://vault:8200","token":"my-vault-token"}'

# 2. AWS Secrets Manager
export AIRFLOW__SECRETS__BACKEND="airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
export AIRFLOW__SECRETS__BACKEND_KWARGS='{"connections_prefix":"airflow/connections","variables_prefix":"airflow/variables"}'

# 3. GCP Secret Manager
export AIRFLOW__SECRETS__BACKEND="airflow.providers.google.cloud.secrets.secret_manager.CloudSecretManagerBackend"
export AIRFLOW__SECRETS__BACKEND_KWARGS='{"connections_prefix":"airflow-connections","variables_prefix":"airflow-variables","project_id":"my-gcp-project"}'
```

### Docker Compose (Minimal Production)

```yaml
# docker-compose.yml
version: '3.8'
x-airflow-common: &airflow-common
  image: apache/airflow:2.9.0
  environment:
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: ${FERNET_KEY}
    AIRFLOW__WEBSERVER__SECRET_KEY: ${SECRET_KEY}
  volumes:
    - ./dags:/opt/airflow/dags
    - ./plugins:/opt/airflow/plugins
    - ./logs:/opt/airflow/logs
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy

services:
  postgres:
    image: postgres:15
    environment: {POSTGRES_USER: airflow, POSTGRES_PASSWORD: airflow, POSTGRES_DB: airflow}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      retries: 5

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports: ["8080:8080"]
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler

  airflow-triggerer:
    <<: *airflow-common
    command: triggerer

  airflow-worker:
    <<: *airflow-common
    command: celery worker
    environment:
      <<: *airflow-common.environment
      DUMB_INIT_SETSID: "0"

  airflow-init:
    <<: *airflow-common
    command: >
      bash -c "airflow db migrate && airflow users create
        --username admin --firstname Admin --lastname User
        --role Admin --email admin@example.com --password admin"
```

---

## 16. Security — RBAC, Fernet & Secrets

### RBAC Roles

| Role | Permissions |
|------|-------------|
| `Admin` | Full access including user management |
| `Viewer` | Read-only access to DAGs, runs, logs |
| `User` | Trigger/clear runs, but no config changes |
| `Op` | Manage connections, variables, pools |
| `Public` | No access (used for unauthenticated requests) |

```bash
# User management
airflow users create \
  --username john \
  --firstname John \
  --lastname Doe \
  --role Viewer \
  --email john@company.com \
  --password secret

airflow users list
airflow users add-role --username john --role Op
airflow users remove-role --username john --role Viewer
airflow users delete --username john

# Role management
airflow roles create my_custom_role
airflow roles list
airflow roles add-perms --role my_custom_role --action can_read --resource DAGs
airflow roles export roles.json
```

### DAG-Level Access Control

```python
with DAG(
    dag_id="finance_dag",
    access_control={
        "finance_team": {"can_read", "can_edit"},
        "auditors":     {"can_read"},
    },
):
    ...
```

### Fernet Encryption

```python
# Generate Fernet key
from cryptography.fernet import Fernet
key = Fernet.generate_key().decode()
print(key)
# Store as: AIRFLOW__CORE__FERNET_KEY=<key>

# Rotate Fernet key
# 1. Set new key first, keep old key
# AIRFLOW__CORE__FERNET_KEY="new_key"
# Run: airflow db rotate-fernet-key
# 2. Then remove old key reference
```

### Authentication Backends

```ini
# airflow.cfg
[api]
auth_backends = airflow.api.auth.backend.basic_auth

# Multiple backends (tried in order)
auth_backends = airflow.api.auth.backend.kerberos_auth,airflow.api.auth.backend.basic_auth

# LDAP (via fab config in webserver_config.py)
# OAuth (Google, GitHub, Okta via fab)
```

```python
# webserver_config.py — LDAP
from airflow.www.security import AirflowSecurityManager
from flask_appbuilder.security.manager import AUTH_LDAP

AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://ldap.company.com"
AUTH_LDAP_USE_TLS = True
AUTH_LDAP_BIND_USER = "cn=svc-airflow,ou=service,dc=company,dc=com"
AUTH_LDAP_BIND_PASSWORD = "ldap_service_password"
AUTH_LDAP_SEARCH = "ou=users,dc=company,dc=com"
AUTH_LDAP_UID_FIELD = "sAMAccountName"
AUTH_LDAP_GROUP_FIELD = "memberOf"
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Viewer"
AUTH_ROLES_MAPPING = {
    "cn=data-engineers,ou=groups,dc=company,dc=com": ["User"],
    "cn=data-leads,ou=groups,dc=company,dc=com":     ["Op"],
    "cn=airflow-admins,ou=groups,dc=company,dc=com": ["Admin"],
}
```

---

## 17. Logging, Monitoring & Alerting

### Logging Configuration

```python
# Custom logging config — $AIRFLOW_HOME/config/log_config.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "airflow": {"format": "%(asctime)s %(levelname)s %(name)s - %(message)s"},
        "json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"},
    },
    "handlers": {
        "console":    {"class": "logging.StreamHandler", "formatter": "airflow"},
        "task":       {
            "class": "airflow.utils.log.file_task_handler.FileTaskHandler",
            "formatter": "airflow",
            "base_log_folder": "/opt/airflow/logs",
            "filename_template": "{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log",
        },
        "s3_task":    {
            "class": "airflow.providers.amazon.aws.log.s3_task_handler.S3TaskHandler",
            "formatter": "airflow",
            "base_log_folder": "/opt/airflow/logs",
            "s3_log_folder": "s3://my-logs/airflow",
            "filename_template": "{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log",
        },
    },
    "loggers": {
        "airflow.task": {"handlers": ["s3_task"], "level": "INFO", "propagate": False},
        "airflow":      {"handlers": ["console"], "level": "INFO"},
    },
}
```

### Callbacks & Alerts

```python
from airflow.utils.email import send_email
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def on_failure_callback(context):
    """Called when a task fails."""
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    logical_date = context["logical_date"]
    log_url = context["task_instance"].log_url
    exception = context.get("exception")

    # Email alert
    send_email(
        to=["oncall@company.com"],
        subject=f"Airflow FAILED: {dag_id}.{task_id}",
        html_content=f"""
            <b>DAG:</b> {dag_id}<br>
            <b>Task:</b> {task_id}<br>
            <b>Date:</b> {logical_date}<br>
            <b>Logs:</b> <a href="{log_url}">{log_url}</a><br>
            <b>Error:</b> {exception}
        """,
    )

def on_success_callback(context):
    ti = context["task_instance"]
    print(f"Task {ti.task_id} succeeded!")

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Called when SLA is breached."""
    msg = f"SLA MISSED for DAG: {dag.dag_id}. Tasks: {task_list}"
    # Send Slack message, PagerDuty, etc.

with DAG(
    dag_id="monitored_dag",
    default_args={
        "on_failure_callback": on_failure_callback,
        "on_success_callback": on_success_callback,
        "sla": timedelta(hours=2),
    },
    sla_miss_callback=sla_miss_callback,
):
    ...
```

### StatsD & Prometheus Metrics

```ini
# airflow.cfg
[metrics]
statsd_on = True
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow
statsd_allow_list = ti.finish,ti.start,dagrun.duration,scheduler.heartbeat

# For Prometheus (via statsd_exporter or direct)
# Use: apache-airflow-providers-opentelemetry (2.7+)
```

Key metrics to monitor:

| Metric | Alert On |
|--------|----------|
| `airflow.scheduler.heartbeat` | > 30s gap → scheduler down |
| `airflow.dagrun.duration.*` | Exceeds SLA |
| `airflow.ti.finish.*.failed` | > 0 in 5m window |
| `airflow.pool.open_slots.*` | Pool exhausted |
| `airflow.executor.running_tasks` | Approaching `parallelism` |
| `airflow.dag.loading-duration.*` | > 30s → DAG parsing slow |

### SLAs

```python
from datetime import timedelta

with DAG("sla_dag", sla_miss_callback=my_sla_callback, ...):
    task = PythonOperator(
        task_id="critical_task",
        python_callable=fn,
        sla=timedelta(hours=1),   # must complete within 1hr of logical_date
    )
```

---

## 18. Kubernetes Executor & KubernetesPodOperator

### KubernetesPodOperator

```python
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

task = KubernetesPodOperator(
    task_id="k8s_task",
    name="airflow-worker-pod",
    namespace="airflow",
    image="python:3.11-slim",
    image_pull_policy="IfNotPresent",
    cmds=["python", "-c"],
    arguments=["print('Hello from K8s!')"],

    # Environment
    env_vars=[
        k8s.V1EnvVar(name="ENV", value="prod"),
        k8s.V1EnvVar(
            name="DB_PASSWORD",
            value_from=k8s.V1EnvVarSource(
                secret_key_ref=k8s.V1SecretKeySelector(name="db-secret", key="password")
            )
        ),
    ],
    env_from=[
        k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name="my-config")),
    ],

    # Resources
    container_resources=k8s.V1ResourceRequirements(
        requests={"cpu": "500m", "memory": "512Mi"},
        limits={"cpu": "2", "memory": "4Gi", "nvidia.com/gpu": "1"},
    ),

    # Volumes
    volumes=[
        k8s.V1Volume(
            name="shared-data",
            persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                claim_name="my-pvc"
            ),
        ),
    ],
    volume_mounts=[
        k8s.V1VolumeMount(mount_path="/data", name="shared-data"),
    ],

    # Pod config
    service_account_name="airflow-worker",
    image_pull_secrets=[k8s.V1LocalObjectReference(name="registry-secret")],
    labels={"team": "data", "version": "v1"},
    annotations={"iam.amazonaws.com/role": "arn:aws:iam::123:role/MyRole"},
    node_selector={"node.kubernetes.io/instance-type": "m5.xlarge"},
    tolerations=[
        k8s.V1Toleration(key="dedicated", operator="Equal", value="gpu", effect="NoSchedule")
    ],

    # Behavior
    get_logs=True,               # stream pod logs to Airflow logs
    log_events_on_failure=True,  # log K8s events if pod fails
    is_delete_operator_pod=True, # delete pod after completion
    startup_timeout_seconds=300,
    on_finish_action="delete_pod",   # 2.6+: delete_pod | keep_pod | delete_succeeded_pod

    # Sidecar injection
    init_containers=[
        k8s.V1Container(
            name="init-data",
            image="busybox",
            command=["sh", "-c", "echo initializing > /data/init.log"],
            volume_mounts=[k8s.V1VolumeMount(mount_path="/data", name="shared-data")],
        )
    ],

    # KubernetesExecutor pod template override
    executor_config={
        "pod_override": k8s.V1Pod(
            metadata=k8s.V1ObjectMeta(annotations={"cluster-autoscaler.kubernetes.io/safe-to-evict": "false"}),
            spec=k8s.V1PodSpec(priority_class_name="high-priority"),
        )
    },
)
```

### Pod Template File (KubernetesExecutor)

```yaml
# pod_template.yaml — base pod for ALL KubernetesExecutor tasks
apiVersion: v1
kind: Pod
metadata:
  name: placeholder
  labels:
    component: airflow-worker
spec:
  restartPolicy: Never
  serviceAccountName: airflow-worker
  automountServiceAccountToken: true
  containers:
    - name: base
      image: my-registry/airflow:2.9.0
      imagePullPolicy: IfNotPresent
      resources:
        requests:
          cpu: "1"
          memory: "2Gi"
        limits:
          cpu: "2"
          memory: "4Gi"
      env:
        - name: AIRFLOW__CORE__EXECUTOR
          value: KubernetesExecutor
      volumeMounts:
        - name: logs
          mountPath: /opt/airflow/logs
  volumes:
    - name: logs
      emptyDir: {}
  nodeSelector:
    workload: airflow
```

---

## 19. CLI Reference

### DAG Operations

```bash
# List all DAGs
airflow dags list
airflow dags list-runs --dag-id my_dag --num-runs 10
airflow dags list-jobs --dag-id my_dag

# Trigger
airflow dags trigger my_dag
airflow dags trigger my_dag --conf '{"key": "value"}'
airflow dags trigger my_dag --logical-date 2024-01-15

# Pause / Unpause
airflow dags pause my_dag
airflow dags unpause my_dag

# Test (dry-run DAG file load)
airflow dags test my_dag 2024-01-01

# Show DAG structure
airflow dags show my_dag                    # ASCII art
airflow dags show my_dag --imgcat           # render in terminal
airflow dags show-import-errors

# Delete DAG and all its metadata
airflow dags delete my_dag

# Reserialize (force DB refresh)
airflow dags reserialize
```

### Task Operations

```bash
# List tasks in a DAG
airflow tasks list my_dag
airflow tasks list my_dag --tree

# Run a single task (test mode — no state saved to DB)
airflow tasks test my_dag my_task 2024-01-01
airflow tasks test my_dag my_task 2024-01-01 --env-var MY_KEY=MY_VAL

# Run a task (real run — saves state to DB)
airflow tasks run my_dag my_task manual__2024-01-01T00:00:00+00:00

# Clear task state (to re-run)
airflow tasks clear my_dag --task-regex "extract.*" --start-date 2024-01-01
airflow tasks clear my_dag --dag-id my_dag --yes   # skip confirmation
airflow tasks clear my_dag --only-failed           # clear only failed tasks
airflow tasks clear my_dag --downstream            # also clear downstream

# Get task state
airflow tasks state my_dag my_task 2024-01-01

# Set task state manually
airflow tasks set-state my_dag my_task 2024-01-01 --state success

# Get XCom value
airflow tasks render my_dag my_task 2024-01-01    # render Jinja templates
```

### DagRun Operations

```bash
# List runs
airflow dags list-runs --dag-id my_dag

# Create manual run
airflow dags trigger my_dag --run-id my_custom_run_id --conf '{"env":"prod"}'

# Delete a run
airflow dags delete-dag-run --dag-id my_dag --run-id manual__2024-01-01

# Mark run state
airflow dags mark-failed-run my_dag --run-id <run_id>
airflow dags mark-success-run my_dag --run-id <run_id>
```

### Database Operations

```bash
airflow db check             # test DB connection
airflow db migrate           # apply schema migrations (replaces airflow db upgrade)
airflow db downgrade --to-revision <rev>
airflow db shell             # drop into DB SQL shell
airflow db clean --clean-before-timestamp "2023-01-01 00:00:00" \
  --tables dag_run,task_instance --yes    # purge old data
airflow db reset --yes       # DANGER: wipe entire DB
```

### User & Pool Management

```bash
# Users
airflow users create --username admin --firstname A --lastname B \
  --role Admin --email admin@example.com --password admin
airflow users list
airflow users delete --username bob

# Pools
airflow pools set etl_pool 10 "ETL task concurrency"
airflow pools list
airflow pools get etl_pool
airflow pools delete etl_pool

# Connections
airflow connections add --conn-id my_conn --conn-type http --conn-host api.example.com
airflow connections list
airflow connections delete --conn-id my_conn

# Variables
airflow variables set env prod
airflow variables get env
airflow variables list
airflow variables delete env
airflow variables import vars.json
airflow variables export vars_backup.json
```

### Info & Health

```bash
airflow info                  # system info, config, version
airflow version               # print Airflow version
airflow cheat-sheet           # quick reference (built-in)
airflow config get-value core executor
airflow config list
```

---

## 20. REST API Reference

### Authentication

```bash
# Basic auth
curl -u admin:admin http://localhost:8080/api/v1/health

# Token-based (session or JWT)
TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/dags
```

### Key Endpoints

```bash
BASE="http://localhost:8080/api/v1"

# DAGs
GET    $BASE/dags                          # list all DAGs
GET    $BASE/dags/{dag_id}                 # get DAG details
PATCH  $BASE/dags/{dag_id}                 # update (pause/unpause)
DELETE $BASE/dags/{dag_id}                 # delete DAG
GET    $BASE/dags/{dag_id}/tasks           # list tasks
GET    $BASE/dags/{dag_id}/tasks/{task_id} # task details
GET    $BASE/dags/{dag_id}/source          # DAG source code

# DAG Runs
GET    $BASE/dags/{dag_id}/dagRuns         # list runs
POST   $BASE/dags/{dag_id}/dagRuns         # trigger run
GET    $BASE/dags/{dag_id}/dagRuns/{run_id}
PATCH  $BASE/dags/{dag_id}/dagRuns/{run_id}  # update state
DELETE $BASE/dags/{dag_id}/dagRuns/{run_id}
POST   $BASE/dags/{dag_id}/dagRuns/{run_id}/clear  # clear run

# Task Instances
GET    $BASE/dags/{dag_id}/dagRuns/{run_id}/taskInstances
GET    $BASE/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}
PATCH  $BASE/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}  # set state
POST   $BASE/dags/{dag_id}/dagRuns/{run_id}/taskInstances/clear      # clear TIs

# XCom
GET    $BASE/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}/xcomEntries
GET    $BASE/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}/xcomEntries/{key}

# Connections
GET    $BASE/connections
POST   $BASE/connections
GET    $BASE/connections/{conn_id}
PATCH  $BASE/connections/{conn_id}
DELETE $BASE/connections/{conn_id}

# Variables
GET    $BASE/variables
POST   $BASE/variables
GET    $BASE/variables/{var_name}
PATCH  $BASE/variables/{var_name}
DELETE $BASE/variables/{var_name}

# Pools
GET    $BASE/pools
POST   $BASE/pools
GET    $BASE/pools/{pool_name}
PATCH  $BASE/pools/{pool_name}
DELETE $BASE/pools/{pool_name}

# Health
GET    $BASE/health       # {"metadatabase":{"status":"healthy"},"scheduler":{"status":"healthy"}}

# Monitoring
GET    $BASE/monitoring/metrics  # OpenMetrics endpoint (if enabled)
```

### Trigger DAG Run — Full Example

```bash
curl -X POST "http://localhost:8080/api/v1/dags/my_dag/dagRuns" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d '{
    "dag_run_id": "api_run_20240115",
    "logical_date": "2024-01-15T00:00:00Z",
    "conf": {"env": "prod", "batch_size": 5000},
    "note": "Triggered via API"
  }'
```

### Pause / Unpause DAG

```bash
curl -X PATCH "http://localhost:8080/api/v1/dags/my_dag" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d '{"is_paused": false}'
```

---

## 21. Performance Tuning

### Scheduler Tuning

```ini
[scheduler]
# Parse DAG files faster
parsing_processes = 4              # match CPU count
min_file_process_interval = 30     # seconds; lower = more fresh, higher CPU
dag_dir_list_interval = 30
file_parsing_sort_mode = modified_time  # parse recently changed files first

# Scheduling throughput
max_dagruns_to_create_per_loop = 10    # batch size for creating DagRuns
max_tis_per_query = 512                # TI batch size per scheduling loop

# Heartbeat
scheduler_heartbeat_sec = 5

[core]
parallelism = 64                   # global concurrent task limit
max_active_tasks_per_dag = 16
max_active_runs_per_dag = 3

[database]
sql_alchemy_pool_size = 10         # DB connection pool
sql_alchemy_max_overflow = 20
sql_alchemy_pool_pre_ping = True   # verify connections before using
```

### DAG File Optimization

```python
# BAD: heavy imports at module level slow all DAG parsing
import pandas as pd            # 200ms per parse
import tensorflow as tf        # 2s per parse

# GOOD: lazy imports inside task functions
@task
def process():
    import pandas as pd        # only loaded when task runs
    ...

# BAD: DB calls at module level
conn = get_db_connection()     # runs on every DAG parse

# GOOD: defer to execute()
class MyOp(BaseOperator):
    def execute(self, context):
        conn = get_db_connection()   # only at task runtime

# BAD: dynamic file loading
for file in glob.glob("/data/*.csv"):    # slow filesystem scan on parse
    create_task(file)

# GOOD: store file list in Variables or pass via conf
@task
def get_files():
    return Variable.get("file_list", deserialize_json=True)

files = get_files()
process.expand(filename=files)    # dynamic mapping
```

### DAG Parsing Metrics

```bash
# Watch parsing time
airflow dags list-jobs --job-type DagProcessorJob

# DAG loading duration metric
airflow_dag_loading_duration_seconds{dag_id="slow_dag"} > 5  # alert!
```

### Database Maintenance

```bash
# Purge old records (run periodically)
airflow db clean \
  --clean-before-timestamp "$(date -d '90 days ago' '+%Y-%m-%d %H:%M:%S')" \
  --tables dag_run,task_instance,log,xcom,sla_miss \
  --yes

# Check DB size (PostgreSQL)
SELECT
  table_name,
  pg_size_pretty(pg_total_relation_size(table_name::regclass)) AS size,
  n_live_tup AS rows
FROM information_schema.tables
JOIN pg_stat_user_tables USING (table_name)
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(table_name::regclass) DESC;
```

### Worker Tuning (Celery)

```ini
[celery]
worker_concurrency = 16           # tasks per worker
worker_prefetch_multiplier = 1    # 1 = fair distribution; higher = throughput
task_acks_late = True             # re-queue on worker crash

# Scale workers
# airflow celery worker -c 16 -l info --autoscale=16,4
# Autoscale: max=16 workers, min=4
```

---

## 22. Best Practices & Anti-Patterns

### ✅ DO

```python
# 1. Always set catchup=False unless you need historical backfill
DAG(catchup=False, ...)

# 2. Always set start_date to a static past date (never "today" or datetime.now())
start_date=datetime(2024, 1, 1)   # ✅ static

# 3. Use max_active_runs to prevent DAG pile-up
DAG(max_active_runs=1, ...)

# 4. Set retries and retry_delay in default_args
default_args={"retries": 3, "retry_delay": timedelta(minutes=5)}

# 5. Use task-level timeouts
BashOperator(..., execution_timeout=timedelta(hours=1))

# 6. Use sensors in "reschedule" mode for long waits
FileSensor(..., mode="reschedule", poke_interval=300, timeout=86400)

# 7. Keep DAG files fast to parse (< 1 second)
# Lazy imports, no DB calls, no file I/O at module level

# 8. Tag your DAGs
DAG(tags=["etl", "finance", "daily"])

# 9. Use pools to protect shared resources
task = MyOperator(..., pool="db_pool", pool_slots=1)

# 10. Store secrets in Secrets Backend, not Variables/Connections in plain text
# Use: Vault, AWS Secrets Manager, GCP Secret Manager

# 11. Idempotent tasks — running twice gives same result
@task
def write_data(ds):
    # DELETE then INSERT, or UPSERT — not plain INSERT
    db.execute("DELETE FROM table WHERE date = %s", [ds])
    db.execute("INSERT INTO table ...")

# 12. Use logical_date / data_interval_start for data partitioning
@task
def process(data_interval_start=None, **context):
    date = data_interval_start.date()
    ...

# 13. DAG IDs are unique and stable — never rename a running DAG
# 14. Use doc_md to document DAGs
DAG(doc_md="# My DAG\nDoes X when Y happens.", ...)

# 15. Use depends_on_past=True for tasks that depend on their own previous run
task = PythonOperator(..., depends_on_past=True)
```

### ❌ DON'T

```python
# 1. Never use execution_date as column name (deprecated — use logical_date)
# 2. Never use datetime.now() as start_date
start_date=datetime.now()  # ❌ shifts every parse; broken backfills

# 3. Never do expensive work at DAG file scope
df = pd.read_csv("huge_file.csv")  # ❌ runs on every parse

# 4. Never use DummyOperator for critical fan-in (use trigger_rule instead)
# 5. Never catch all exceptions and return silently
def bad_task():
    try:
        risky_op()
    except:
        pass  # ❌ hides failures from Airflow

# 6. Never write non-idempotent tasks (plain INSERT without dedup)
def bad_insert():
    db.execute("INSERT INTO table VALUES (...)")  # ❌ duplicates on retry

# 7. Never store large data in XCom
ti.xcom_push("huge_df", df.to_json())  # ❌ bloats metadata DB

# 8. Never use sleep() inside tasks
time.sleep(300)  # ❌ holds worker slot; use sensors instead

# 9. Never hardcode credentials in DAG files
PASS = "super_secret"  # ❌ use connections/variables/secrets

# 10. Never use SubDagOperator (deprecated in 2.x, removed in 3.x)
# Use TaskGroups instead

# 11. Avoid globals/shared mutable state in DAG files
SHARED_LIST = []  # ❌ shared across DAG parses
```

### Task Groups (SubDAG Replacement)

```python
from airflow.utils.task_group import TaskGroup

with DAG("my_dag", ...):
    with TaskGroup("extract_group") as extract:
        e1 = PythonOperator(task_id="extract_users", ...)
        e2 = PythonOperator(task_id="extract_orders", ...)

    with TaskGroup("load_group") as load:
        l1 = PythonOperator(task_id="load_users", ...)
        l2 = PythonOperator(task_id="load_orders", ...)

    extract >> load

# TaskFlow with TaskGroup
with DAG("flow_dag", ...):
    with TaskGroup("transform"):
        @task(task_id="normalize")
        def normalize(): ...

        @task(task_id="validate")
        def validate(): ...

        normalize() >> validate()
```

---

## 23. Airflow 2.x vs 3.x — Key Differences & Migration

### Feature Comparison Table

| Feature | Airflow 2.x | Airflow 3.x |
|---------|------------|------------|
| **DAG authoring** | Classic + TaskFlow | TaskFlow preferred; classic still works |
| **Scheduler** | Single (HA via DB) | Multi-scheduler native support improved |
| **SubDagOperator** | Deprecated | **Removed** — use TaskGroups |
| **`execution_date`** | Available (deprecated) | **Removed** — use `logical_date` |
| **`provide_context`** | Ignored (always True) | Removed |
| **`schedule_interval`** | Used | Renamed to `schedule` |
| **Datasets** | Introduced (2.4) | Enhanced: Dataset aliases, conditions |
| **Dynamic Task Mapping** | Introduced (2.3) | Improved; `expand_kwargs` enhanced |
| **Deferrable Operators** | Introduced (2.2) | Widely adopted, first-class |
| **REST API** | v1 (Stable) | v2 (breaking changes from v1) |
| **UI** | Flask + FAB | Rewritten (React-based in 3.x) |
| **Python support** | 3.8+ | 3.9+ |
| **`DagRunType`** | `scheduled`, `manual`, `backfill` | Added `dataset_triggered` |
| **Params** | Available | Enhanced validation |
| **`@dag` decorator** | Available | Preferred over `with DAG()` |
| **AIP-50 (Simplified Scheduler)** | N/A | Implemented |
| **`airflow db upgrade`** | Used | Replaced by `airflow db migrate` |

### Migration Steps: 2.x → 3.x

```python
# 1. Replace execution_date with logical_date
# OLD
def my_task(execution_date, **kwargs): ...
# NEW
def my_task(logical_date=None, **kwargs): ...
# or via context
def my_task(**context):
    logical_date = context["logical_date"]

# 2. Replace schedule_interval with schedule
# OLD
DAG(dag_id="x", schedule_interval="@daily", ...)
# NEW
DAG(dag_id="x", schedule="@daily", ...)

# 3. Remove SubDagOperator — use TaskGroups
# OLD (2.x deprecated)
from airflow.operators.subdag import SubDagOperator
# NEW
from airflow.utils.task_group import TaskGroup

# 4. Remove provide_context=True
# OLD
PythonOperator(python_callable=fn, provide_context=True)
# NEW
PythonOperator(python_callable=fn)   # context always provided

# 5. Update DB migration command
# OLD
airflow db upgrade
# NEW
airflow db migrate

# 6. REST API v1 → v2 (if you use the API programmatically)
# Endpoint paths and some response schemas changed
# Review: https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html
```

### 2.x Feature Timeline (Quick Ref)

| Version | Key Feature |
|---------|------------|
| 2.0 | TaskFlow API, new DAG serialization, REST API v1 |
| 2.1 | Smart sensors, scheduler HA |
| 2.2 | Timetables, deferrable operators, Triggerer |
| 2.3 | Dynamic task mapping (`expand/partial`) |
| 2.4 | Data-aware scheduling (Datasets) |
| 2.5 | `expand_kwargs`, setup/teardown tasks (preview) |
| 2.6 | Setup/teardown tasks GA, `on_finish_action` |
| 2.7 | Auth Manager, `airflow db migrate`, OpenTelemetry |
| 2.8 | Dataset aliases, `@setup`/`@teardown` decorators |
| 2.9 | Backfill UI, dataset conditions |
| 2.10 | Object storage (FAB), improved grid view |

### Setup & Teardown Tasks (2.6+)

```python
from airflow.decorators import dag, task, setup, teardown

@dag(...)
def pipeline():
    @setup
    def create_cluster():
        # Runs first; failure blocks main tasks
        return cluster_id

    @task
    def process(cluster_id: str):
        ...

    @teardown
    def destroy_cluster(cluster_id: str):
        # Always runs even if process fails
        ...

    cluster = create_cluster()
    work = process(cluster)
    destroy_cluster(cluster) << work   # teardown depends on work
```

---

## Appendix: Quick Reference Tables

### Common Jinja Macros

```python
"{{ macros.ds_add(ds, 7) }}"                    # ds + 7 days
"{{ macros.ds_format(ds, '%Y-%m-%d', '%d/%m/%Y') }}"  # reformat date
"{{ macros.datetime.utcnow() }}"                 # current UTC time
"{{ macros.uuid.uuid4() }}"                      # random UUID
"{{ macros.random.randint(1, 100) }}"            # random int
```

### Useful CLI One-Liners

```bash
# Re-run all failed tasks for a date range
airflow tasks clear my_dag --only-failed \
  --start-date 2024-01-01 --end-date 2024-01-31 --yes

# Find long-running task instances (PostgreSQL)
psql -c "SELECT dag_id, task_id, start_date, 
         now() - start_date AS duration 
         FROM task_instance 
         WHERE state='running' 
         ORDER BY duration DESC LIMIT 20;"

# Count tasks by state for a DAG
airflow tasks list my_dag | wc -l

# Unpause all DAGs at once
airflow dags list -o plain | tail -n+2 | awk '{print $1}' | \
  xargs -I{} airflow dags unpause {}
```

### Provider Package Install Reference

```bash
pip install apache-airflow-providers-postgres
pip install apache-airflow-providers-amazon
pip install apache-airflow-providers-google
pip install apache-airflow-providers-microsoft-azure
pip install apache-airflow-providers-apache-spark
pip install apache-airflow-providers-databricks
pip install apache-airflow-providers-dbt-cloud
pip install apache-airflow-providers-http
pip install apache-airflow-providers-slack
pip install apache-airflow-providers-cncf-kubernetes
pip install apache-airflow-providers-hashicorp  # Vault
pip install apache-airflow-providers-ssh
pip install apache-airflow-providers-sftp
pip install apache-airflow-providers-telegram
pip install apache-airflow-providers-pagerduty
pip install apache-airflow-providers-opentelemetry
```

### airflow.cfg Precedence (Highest to Lowest)

```
1. Environment variables (AIRFLOW__{SECTION}__{KEY})
2. Secrets Backend values
3. airflow.cfg file
4. Built-in defaults
```

---

*Generated for Apache Airflow — Version-Agnostic Core + 2.x/3.x migration notes*
*Covers: Beginner → Advanced → Architect*
