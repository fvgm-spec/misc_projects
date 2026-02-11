---
title: Processing engine and Python plugins
description: Use the InfluxDB 3 Processing engine with Python to trigger and execute custom code on different events in an InfluxDB 3 Core instance.
url: https://docs.influxdata.com/influxdb3/core/plugins/
product: InfluxDB 3 Core
type: section
pages: 3
estimated_tokens: 29926
child_pages:
  - url: https://docs.influxdata.com/influxdb3/core/plugins/library/
    title: Plugin library
  - url: https://docs.influxdata.com/influxdb3/core/plugins/extend-plugin/
    title: Extend plugins with API features and state management
---

# Processing engine and Python plugins

Use the Processing Engine in InfluxDB 3 Core to extend your database with custom Python code. Trigger your code on write, on a schedule, or on demand to automate workflows, transform data, and create API endpoints.

## What is the Processing Engine?

The Processing Engine is an embedded Python virtual machine that runs inside your InfluxDB 3 Core database. You configure *triggers* to run your Python *plugin* code in response to:

-   **Data writes** - Process and transform data as it enters the database
-   **Scheduled events** - Run code at defined intervals or specific times
-   **HTTP requests** - Expose custom API endpoints that execute your code

You can use the Processing Engine’s in-memory cache to manage state between executions and build stateful applications directly in your database.

This guide walks you through setting up the Processing Engine, creating your first plugin, and configuring triggers that execute your code on specific events.

## Before you begin

Ensure you have:

-   A working InfluxDB 3 Core instance
-   Access to command line
-   Python installed if you’re writing your own plugin
-   Basic knowledge of the InfluxDB CLI

Once you have all the prerequisites in place, follow these steps to implement the Processing Engine for your data automation needs.

-   [Set up the Processing Engine](#set-up-the-processing-engine)
-   [Add a Processing Engine plugin](#add-a-processing-engine-plugin)
    -   [Upload plugins from local machine](#upload-plugins-from-local-machine)
    -   [Update existing plugins](#update-existing-plugins)
    -   [View loaded plugins](#view-loaded-plugins)
-   [Set up a trigger](#set-up-a-trigger)
-   [Manage plugin dependencies](#manage-plugin-dependencies)
-   [Plugin security](#plugin-security)

## Set up the Processing Engine

To activate the Processing Engine, start your InfluxDB 3 Core server with the `--plugin-dir` flag. This flag tells InfluxDB where to load your plugin files.

#### Keep the influxdb3 binary with its python directory

The influxdb3 binary requires the adjacent `python/` directory to function. If you manually extract from tar.gz, keep them in the same parent directory:

```
your-install-location/
├── influxdb3
└── python/
```

Add the parent directory to your PATH; do not move the binary out of this directory.

```bash
influxdb3 serve \
  --NODE_ID \
  --object-store OBJECT_STORE_TYPE \
  --plugin-dir PLUGIN_DIR
```

In the example above, replace the following:

-   `NODE_ID`: Unique identifier for your instance
-   `OBJECT_STORE_TYPE`: Type of object store (for example, file or s3)
-   `PLUGIN_DIR`: Absolute path to the directory where plugin files are stored. Store all plugin files in this directory or its subdirectories.

#### Use custom plugin repositories

By default, plugins referenced with the `gh:` prefix are fetched from the official [influxdata/influxdb3\_plugins](https://github.com/influxdata/influxdb3_plugins) repository. To use a custom repository, add the `--plugin-repo` flag when starting the server. See [Use a custom plugin repository](#option-3-use-a-custom-plugin-repository) for details.

### Configure distributed environments

When running InfluxDB 3 Core in a distributed setup, follow these steps to configure the Processing Engine:

1. Decide where each plugin should run
    -   Data processing plugins, such as WAL plugins, run on ingester nodes
    -   HTTP-triggered plugins run on nodes handling API requests
    -   Scheduled plugins can run on any configured node
2. Enable plugins on the correct instance
3. Maintain identical plugin files across all instances where plugins run
    -   Use shared storage or file synchronization tools to keep plugins consistent

#### Provide plugins to nodes that run them

Configure your plugin directory on the same system as the nodes that run the triggers and plugins.

## Add a Processing Engine plugin

A plugin is a Python script that defines a function with a trigger-compatible (*trigger spec*) signature. When the specified event occurs, InfluxDB runs the plugin.

### Choose a plugin strategy

You have two main options for adding plugins to your InfluxDB instance:

-   [Use example plugins](#use-example-plugins) - Get started with prebuilt plugins
-   [Create a custom plugin](#create-a-custom-plugin) - Build your own for specialized use cases

### Use example plugins

InfluxData maintains a repository of official and community plugins that you can use immediately in your Processing Engine setup.

Browse the [plugin library](/influxdb3/core/plugins/library/) to find examples and InfluxData official plugins for:

-   **Data transformation**: Process and transform incoming data
-   **Alerting**: Send notifications based on data thresholds
-   **Aggregation**: Calculate statistics on time series data
-   **Integration**: Connect to external services and APIs
-   **System monitoring**: Track resource usage and health metrics

For community contributions, see the [influxdb3\_plugins repository](https://github.com/influxdata/influxdb3_plugins) on GitHub.

#### Add example plugins

You have two options for using plugins from the repository:

##### Option 1: Copy plugins locally

Clone the `influxdata/influxdb3_plugins` repository and copy plugins to your configured plugin directory:

```bash
# Clone the repository
git clone https://github.com/influxdata/influxdb3_plugins.git
   
# Copy a plugin to your configured plugin directory
cp influxdb3_plugins/influxdata/system_metrics/system_metrics.py /path/to/plugins/
```

##### Option 2: Reference plugins directly from GitHub

Skip downloading plugins by referencing them directly from GitHub using the `gh:` prefix:

```bash
# Create a trigger using a plugin from GitHub
influxdb3 create trigger \
  --trigger-spec "every:1m" \
  --path "gh:influxdata/system_metrics/system_metrics.py" \
  --database my_database \
  system_metrics
```

This approach:

-   Ensures you’re using the latest version
-   Simplifies updates and maintenance
-   Reduces local storage requirements

##### Option 3: Use a custom plugin repository

For organizations that maintain their own plugin repositories or need to use private/internal plugins, configure a custom plugin repository URL:

```bash
# Start the server with a custom plugin repository
influxdb3 serve \
  --node-id node0 \
  --object-store file \
  --data-dir ~/.influxdb3 \
  --plugin-dir ~/.plugins \
  --plugin-repo "https://internal.company.com/influxdb-plugins/"
```

Then reference plugins from your custom repository using the `gh:` prefix:

```bash
# Fetches from: https://internal.company.com/influxdb-plugins/myorg/custom_plugin.py
influxdb3 create trigger \
  --trigger-spec "every:5m" \
  --path "gh:myorg/custom_plugin.py" \
  --database my_database \
  custom_trigger
```

**Use cases for custom repositories:**

-   **Private plugins**: Host proprietary plugins not suitable for public repositories
-   **Air-gapped environments**: Use internal mirrors when external internet access is restricted
-   **Development and staging**: Test plugins from development branches before production deployment
-   **Compliance requirements**: Meet data governance policies requiring internal hosting

The `--plugin-repo` option accepts any HTTP/HTTPS URL that serves raw plugin files. See the [plugin-repo configuration option](/influxdb3/core/reference/config-options/#plugin-repo) for more details.

Plugins have various functions such as:

-   Receive plugin-specific arguments (such as written data, call time, or an HTTP request)
-   Access keyword arguments (as `args`) passed from *trigger arguments* configurations
-   Access the `influxdb3_local` shared API to write data, query data, and managing state between executions

For more information about available functions, arguments, and how plugins interact with InfluxDB, see how to [Extend plugins](/influxdb3/core/extend-plugin/).

### Create a custom plugin

To build custom functionality, you can create your own Processing Engine plugin.

#### Prerequisites

Before you begin, make sure:

-   The Processing Engine is enabled on your InfluxDB 3 Core instance.
-   You’ve configured the `--plugin-dir` where plugin files are stored.
-   You have access to that plugin directory.

#### Steps to create a plugin:

-   [Choose your plugin type](#choose-your-plugin-type)
-   [Create your plugin file](#create-your-plugin-file)
-   [Next Steps](#next-steps)

#### Choose your plugin type

Choose a plugin type based on your automation goals:

| Plugin Type | Best For |
| --- | --- |
| Data write | Processing data as it arrives |
| Scheduled | Running code at specific intervals or times |
| HTTP request | Running code on demand via API endpoints |

#### Create your plugin file

Plugins now support both single-file and multifile architectures:

**Single-file plugins:**

-   Create a `.py` file in your plugins directory
-   Add the appropriate function signature based on your chosen plugin type
-   Write your processing logic inside the function

**Multifile plugins:**

-   Create a directory in your plugins directory
-   Add an `__init__.py` file as the entry point (required)
-   Organize supporting modules in additional `.py` files
-   Import and use modules within your plugin code

##### Example multifile plugin structure

```
my_plugin/
├── __init__.py       # Required - entry point with trigger function
├── utils.py          # Supporting module
├── processors.py     # Data processing functions
└── config.py         # Configuration helpers
```

The `__init__.py` file must contain your trigger function:

```python
# my_plugin/__init__.py
from .processors import process_data
from .config import get_settings

def process_writes(influxdb3_local, table_batches, args=None):
    settings = get_settings()
    for table_batch in table_batches:
        process_data(influxdb3_local, table_batch, settings)
```

Supporting modules can contain helper functions:

```python
# my_plugin/processors.py
def process_data(influxdb3_local, table_batch, settings):
    # Processing logic here
    pass
```

After writing your plugin, [create a trigger](#use-the-create-trigger-command) to connect it to a database event and define when it runs.

#### Create a data write plugin

Use a data write plugin to process data as it’s written to the database. These plugins use [`table:` or `all_tables:`](#trigger-on-data-writes) trigger specifications. Ideal use cases include:

-   Data transformation and enrichment
-   Alerting on incoming values
-   Creating derived metrics

```python
def process_writes(influxdb3_local, table_batches, args=None):
    # Process data as it's written to the database
    for table_batch in table_batches:
        table_name = table_batch["table_name"]
        rows = table_batch["rows"]
        
        # Log information about the write
        influxdb3_local.info(f"Processing {len(rows)} rows from {table_name}")
        
        # Write derived data back to the database
        line = LineBuilder("processed_data")
        line.tag("source_table", table_name)
        line.int64_field("row_count", len(rows))
        influxdb3_local.write(line)
```

#### Create a scheduled plugin

Scheduled plugins run at defined intervals using [`every:` or `cron:`](#trigger-on-a-schedule) trigger specifications. Use them for:

-   Periodic data aggregation
-   Report generation
-   System health checks

```python
def process_scheduled_call(influxdb3_local, call_time, args=None):
    # Run code on a schedule
    
    # Query recent data
    results = influxdb3_local.query("SELECT * FROM metrics WHERE time > now() - INTERVAL '1 hour'")
    
    # Process the results
    if results:
        influxdb3_local.info(f"Found {len(results)} recent metrics")
    else:
        influxdb3_local.warn("No recent metrics found")
```

#### Create an HTTP request plugin

HTTP request plugins respond to API calls using [`request:`](#trigger-on-http-requests) trigger specifications. Use them for:

-   Creating custom API endpoints
-   Webhooks for external integrations
-   User interfaces for data interaction

```python
def process_request(influxdb3_local, query_parameters, request_headers, request_body, args=None):
    # Handle HTTP requests to a custom endpoint
    
    # Log the request parameters
    influxdb3_local.info(f"Received request with parameters: {query_parameters}")
    
    # Process the request body
    if request_body:
        import json
        data = json.loads(request_body)
        influxdb3_local.info(f"Request data: {data}")
    
    # Return a response (automatically converted to JSON)
    return {"status": "success", "message": "Request processed"}
```

#### Next steps

After writing your plugin:

-   [Create a trigger](#use-the-create-trigger-command) to connect your plugin to database events
-   [Install any Python dependencies](#manage-plugin-dependencies) your plugin requires
-   Learn how to [extend plugins with the API](/influxdb3/core/extend-plugin/)

### Upload plugins from local machine

For local development and testing, you can upload plugin files directly from your machine when creating triggers. This eliminates the need to manually copy files to the server’s plugin directory.

Use the `--upload` flag with `--path` to transfer local files or directories:

```bash
# Upload single-file plugin
influxdb3 create trigger \
  --trigger-spec "every:10s" \
  --path "/local/path/to/plugin.py" \
  --upload \
  --database metrics \
  my_trigger

# Upload multifile plugin directory
influxdb3 create trigger \
  --trigger-spec "every:30s" \
  --path "/local/path/to/plugin-dir" \
  --upload \
  --database metrics \
  complex_trigger
```

#### Admin privileges required

Plugin uploads require an admin token. This security measure prevents unauthorized code execution on the server.

**When to use plugin upload:**

-   Local plugin development and testing
-   Deploying plugins without SSH access to the server
-   Rapid iteration on plugin code
-   Automating plugin deployment in CI/CD pipelines

For more information, see the [`influxdb3 create trigger` CLI reference](/influxdb3/core/reference/cli/influxdb3/create/trigger/).

### Update existing plugins

Modify plugin code for running triggers without recreating them. This allows you to iterate on plugin development while preserving trigger configuration and history.

Use the `influxdb3 update trigger` command:

```bash
# Update single-file plugin
influxdb3 update trigger \
  --database metrics \
  --trigger-name my_trigger \
  --path "/path/to/updated/plugin.py"

# Update multifile plugin
influxdb3 update trigger \
  --database metrics \
  --trigger-name complex_trigger \
  --path "/path/to/updated/plugin-dir"
```

The update operation:

-   Replaces plugin files immediately
-   Preserves trigger configuration (spec, schedule, arguments)
-   Requires admin token for security
-   Works with both local paths and uploaded files

For complete reference, see [`influxdb3 update trigger`](/influxdb3/core/reference/cli/influxdb3/update/trigger/).

### View loaded plugins

Monitor which plugins are loaded in your system for operational visibility and troubleshooting.

**Option 1: Use the CLI command**

```bash
# List all plugins
influxdb3 show plugins --token $ADMIN_TOKEN

# JSON format for programmatic access
influxdb3 show plugins --format json --token $ADMIN_TOKEN
```

**Option 2: Query the system table**

The `system.plugin_files` table in the `_internal` database provides detailed plugin file information:

```bash
influxdb3 query \
  -d _internal \
  "SELECT * FROM system.plugin_files ORDER BY plugin_name" \
  --token $ADMIN_TOKEN
```

**Available columns:**

-   `plugin_name` (String): Trigger name
-   `file_name` (String): Plugin file name
-   `file_path` (String): Full server path
-   `size_bytes` (Int64): File size
-   `last_modified` (Int64): Modification timestamp (milliseconds)

**Example queries:**

```sql
-- Find plugins by name
SELECT * FROM system.plugin_files WHERE plugin_name = 'my_trigger';

-- Find large plugins
SELECT plugin_name, size_bytes
FROM system.plugin_files
WHERE size_bytes > 10000;

-- Check modification times
SELECT plugin_name, file_name, last_modified
FROM system.plugin_files
ORDER BY last_modified DESC;
```

For more information, see the [`influxdb3 show plugins` reference](/influxdb3/core/reference/cli/influxdb3/show/plugins/) and [Query system data](/influxdb3/core/admin/query-system-data/#query-plugin-files).

## Set up a trigger

### Understand trigger types

| Plugin Type | Trigger Specification | When Plugin Runs |
| --- | --- | --- |
| Data write | table:<TABLE_NAME> or all_tables | When data is written to tables |
| Scheduled | every:<DURATION> or cron:<EXPRESSION> | At specified time intervals |
| HTTP request | request:<REQUEST_PATH> | When HTTP requests are received |

### Use the create trigger command

Use the `influxdb3 create trigger` command with the appropriate trigger specification:

```bash
influxdb3 create trigger \
  --trigger-spec SPECIFICATION \
  --path PLUGIN_FILE \
  --database DATABASE_NAME \
  TRIGGER_NAME
```

In the example above, replace the following:

-   `SPECIFICATION`: Trigger specification
-   `PLUGIN_FILE`: Plugin filename relative to your configured plugin directory
-   `DATABASE_NAME`: Name of the database
-   `TRIGGER_NAME`: Name of the new trigger

#### Plugin paths

-   For **single-file plugins**, provide just the `.py` filename to `--path` (for example, `test_plugin.py`).
-   For **multi-file plugins**, provide the directory name containing `__init__.py`.

When not using `--upload`, the server resolves paths relative to the configured `--plugin-dir`. For details about multi-file plugin structure, see [Create your plugin file](#create-your-plugin-file).

### Trigger specification examples

#### Trigger on data writes

```bash
# Trigger on writes to a specific table
# The plugin file must be in your configured plugin directory
influxdb3 create trigger \
  --trigger-spec "table:sensor_data" \
  --path "process_sensors.py" \
  --database my_database \
  sensor_processor

# Trigger on writes to all tables
influxdb3 create trigger \
  --trigger-spec "all_tables" \
  --path "process_all_data.py" \
  --database my_database \
  all_data_processor
```

The trigger runs when the database flushes ingested data for the specified tables to the Write-Ahead Log (WAL) in the Object store (default is every second).

The plugin receives the written data and table information.

#### Trigger on data writes with table exclusion

If you want to use a single trigger for all tables but exclude specific tables, you can use trigger arguments and your plugin code to filter out unwanted tables–for example:

```bash
influxdb3 create trigger \
  --database DATABASE_NAME \
  --token AUTH_TOKEN \
  --path processor.py \
  --trigger-spec "all_tables" \
  --trigger-arguments "exclude_tables=temp_data,debug_info,system_logs" \
  data_processor
```

Replace the following:

-   DATABASE\_NAME: the name of the database
-   AUTH\_TOKEN: your [token](/influxdb3/core/admin/tokens/)

Then, in your plugin:

```python
# processor.py
def on_write(self, database, table_name, batch):
    # Get excluded tables from trigger arguments
    excluded_tables = set(self.args.get('exclude_tables', '').split(','))

    if table_name in excluded_tables:
        return

    # Process allowed tables
    self.process_data(database, table_name, batch)
```

##### Recommendations

-   **Early return**: Check exclusions as early as possible in your plugin.
-   **Efficient lookups**: Use sets for O(1) lookup performance with large exclusion lists.
-   **Performance**: Log skipped tables for debugging but avoid excessive logging in production.
-   **Multiple triggers**: For few tables, consider creating separate table-specific triggers instead of filtering within plugin code. See HTTP API [Processing engine endpoints](/influxdb3/core/api/v3/#tag/Processing-engine) for managing triggers.

#### Trigger on a schedule

```bash
# Run every 5 minutes
influxdb3 create trigger \
  --trigger-spec "every:5m" \
  --path "periodic_check.py" \
  --database my_database \
  regular_check

# Run on a cron schedule (8am daily)
# Supports extended cron format with seconds
influxdb3 create trigger \
  --trigger-spec "cron:0 0 8 * * *" \
  --path "daily_report.py" \
  --database my_database \
  daily_report
```

The plugin receives the scheduled call time.

#### Trigger on HTTP requests

```bash
# Create an endpoint at /api/v3/engine/webhook
influxdb3 create trigger \
  --trigger-spec "request:webhook" \
  --path "webhook_handler.py" \
  --database my_database \
  webhook_processor
```

Access your endpoint at `/api/v3/engine/{REQUEST_PATH}` (in this example, `/api/v3/engine/webhook`). The trigger is enabled by default and runs when an HTTP request is received at the specified path.

To run the plugin, send a `GET` or `POST` request to the endpoint–for example:

```bash
curl http://localhost:8181/api/v3/engine/webhook
```

The plugin receives the HTTP request object with methods, headers, and body.

To view triggers associated with a database, use the `influxdb3 show summary` command:

```bash
influxdb3 show summary --database my_database --token AUTH_TOKEN
```

### Pass arguments to plugins

Use trigger arguments to pass configuration from a trigger to the plugin it runs. You can use this for:

-   Threshold values for monitoring
-   Connection properties for external services
-   Configuration settings for plugin behavior

```bash
influxdb3 create trigger \
  --trigger-spec "every:1h" \
  --path "threshold_check.py" \
  --trigger-arguments threshold=90,notify_email=admin@example.com \
  --database my_database \
  threshold_monitor
```

The arguments are passed to the plugin as a `Dict[str, str]` where the key is the argument name and the value is the argument value:

```python
def process_scheduled_call(influxdb3_local, call_time, args=None):
    if args and "threshold" in args:
        threshold = float(args["threshold"])
        email = args.get("notify_email", "default@example.com")
        
        # Use the arguments in your logic
        influxdb3_local.info(f"Checking threshold {threshold}, will notify {email}")
```

### Control trigger execution

By default, triggers run synchronously—each instance waits for previous instances to complete before executing.

To allow multiple instances of the same trigger to run simultaneously, configure triggers to run asynchronously:

```bash
# Allow multiple trigger instances to run simultaneously
influxdb3 create trigger \
  --trigger-spec "table:metrics" \
  --path "heavy_process.py" \
  --run-asynchronous \
  --database my_database \
  async_processor
```

### Configure error handling for a trigger

To configure error handling behavior for a trigger, use the `--error-behavior <ERROR_BEHAVIOR>` CLI option with one of the following values:

-   `log` (default): Log all plugin errors to stdout and the `system.processing_engine_logs` system table.
-   `retry`: Attempt to run the plugin again immediately after an error.
-   `disable`: Automatically disable the plugin when an error occurs (can be re-enabled later via CLI).

```bash
# Automatically retry on error
influxdb3 create trigger \
  --trigger-spec "table:important_data" \
  --path "critical_process.py" \
  --error-behavior retry \
  --database my_database \
  critical_processor

# Disable the trigger on error
influxdb3 create trigger \
  --trigger-spec "request:webhook" \
  --path "webhook_handler.py" \
  --error-behavior disable \
  --database my_database \
  auto_disable_processor
```

## Manage plugin dependencies

Use the `influxdb3 install package` command to add third-party libraries (like `pandas`, `requests`, or `influxdb3-python`) to your plugin environment.  
This installs packages into the Processing Engine’s embedded Python environment to ensure compatibility with your InfluxDB instance.

<!-- Tabbed content: Select one of the following options -->

**CLI:**

```bash
# Use the CLI to install a Python package
influxdb3 install package pandas
```

**Docker:**

```bash
# Use the CLI to install a Python package in a Docker container
docker exec -it CONTAINER_NAME influxdb3 install package pandas
```

<!-- End tabbed content -->

These examples install the specified Python package (for example, pandas) into the Processing Engine’s embedded virtual environment.

-   Use the CLI command when running InfluxDB directly on your system.
-   Use the Docker variant if you’re running InfluxDB in a containerized environment.

#### Use bundled Python for plugins

When you start the server with the `--plugin-dir` option, InfluxDB 3 creates a Python virtual environment (`<PLUGIN_DIR>/venv`) for your plugins. If you need to create a custom virtual environment, use the Python interpreter bundled with InfluxDB 3. Don’t use the system Python. Creating a virtual environment with the system Python (for example, using `python -m venv`) can lead to runtime errors and plugin failures.

For more information, see the [processing engine README](https://github.com/influxdata/influxdb/blob/main/README_processing_engine.md).

InfluxDB creates a Python virtual environment in your plugins directory with the specified packages installed.

### Disable package installation for secure environments

For air-gapped deployments or environments with strict security requirements, you can disable Python package installation while maintaining Processing Engine functionality.

Start the server with `--package-manager disabled`:

```bash
influxdb3 serve \
  --node-id node0 \
  --object-store file \
  --data-dir ~/.influxdb3 \
  --plugin-dir ~/.plugins \
  --package-manager disabled
```

When package installation is disabled:

-   The Processing Engine continues to function normally for triggers
-   Plugin code executes without restrictions
-   Package installation commands are blocked
-   Pre-installed dependencies in the virtual environment remain available

**Pre-install required dependencies:**

Before disabling the package manager, install all required Python packages:

```bash
# Install packages first
influxdb3 install package pandas requests numpy

# Then start with disabled package manager
influxdb3 serve \
  --plugin-dir ~/.plugins \
  --package-manager disabled
```

**Use cases for disabled package management:**

-   Air-gapped environments without internet access
-   Compliance requirements prohibiting runtime package installation
-   Centrally managed dependency environments
-   Security policies requiring pre-approved packages only

For more configuration options, see [–package-manager](/influxdb3/core/reference/config-options/#package-manager).

## Plugin security

The Processing Engine includes security features to protect your InfluxDB 3 Core instance from unauthorized code execution and file system attacks.

### Plugin path validation

All plugin file paths are validated to prevent directory traversal attacks. The system blocks:

-   **Relative paths with parent directory references** (`../`, `../../`)
-   **Absolute paths** (`/etc/passwd`, `/usr/bin/script.py`)
-   **Symlinks that escape the plugin directory**

When creating or updating triggers, plugin paths must resolve within the configured `--plugin-dir`.

**Example of blocked paths:**

```bash
# These will be rejected
influxdb3 create trigger \
  --path "../../../etc/passwd" \  # Blocked: parent directory traversal
  ...

influxdb3 create trigger \
  --path "/tmp/malicious.py" \    # Blocked: absolute path
  ...
```

**Valid plugin paths:**

```bash
# These are allowed
influxdb3 create trigger \
  --path "myapp/plugin.py" \      # Relative to plugin-dir
  ...

influxdb3 create trigger \
  --path "transforms/data.py" \    # Subdirectory in plugin-dir
  ...
```

### Upload and update permissions

Plugin upload and update operations require admin tokens to prevent unauthorized code deployment:

-   `--upload` flag requires admin privileges
-   `update trigger` command requires admin token
-   Standard resource tokens cannot upload or modify plugin code

This security model ensures only administrators can introduce or modify executable code in your database.

### Best practices

**For development:**

-   Use the `--upload` flag to deploy plugins during development
-   Test plugins in non-production environments first
-   Review plugin code before deployment

**For production:**

-   Pre-deploy plugins to the server’s plugin directory via secure file transfer
-   Use custom plugin repositories for vetted, approved plugins
-   Disable package installation (`--package-manager disabled`) in locked-down environments
-   Audit plugin files using the [`system.plugin_files` table](#view-loaded-plugins)
-   Implement change control processes for plugin updates

For more security configuration options, see [Configuration options](/influxdb3/core/reference/config-options/).

#### Related

-   [influxdb3 test wal\_plugin](/influxdb3/core/reference/cli/influxdb3/test/wal_plugin/)
-   [influxdb3 create trigger](/influxdb3/core/reference/cli/influxdb3/create/trigger/)

[processing engine](/influxdb3/core/tags/processing-engine/) [python](/influxdb3/core/tags/python/)


---

## Plugin library

Browse plugins for InfluxDB 3 Core. Use these plugins to extend your database functionality with custom Python code that runs on write events, schedules, or HTTP requests.

### [Example plugins](/influxdb3/core/plugins/library/examples/)

Start with example plugins that demonstrate common use cases.

### [Official plugins](/influxdb3/core/plugins/library/official/)

Production-ready plugins developed and maintained by InfluxData.

## Requirements

All plugins require:

-   InfluxDB 3 Core or InfluxDB 3 Enterprise with Processing Engine enabled
-   Python environment (managed automatically by InfluxDB 3)
-   Appropriate trigger configuration

## Plugin metadata

Plugins in this library include a JSON metadata schema in a docstring header that defines supported trigger types and configuration parameters. This metadata enables:

-   the [InfluxDB 3 Explorer UI](/influxdb3/explorer/) to display and configure the plugin
-   automated testing and validation of plugins in the repository

## Using TOML Configuration Files

Many plugins in this library support using TOML configuration files to specify all plugin arguments. This is useful for complex configurations or when you want to version control your plugin settings.

### Important Requirements

**To use TOML configuration files, you must set the `PLUGIN_DIR` environment variable in the InfluxDB 3 Core host environment.** This is required in addition to the `--plugin-dir` flag when starting InfluxDB 3 Core:

-   `--plugin-dir` tells InfluxDB 3 Core where to find plugin Python files
-   `PLUGIN_DIR` environment variable tells the plugins where to find TOML configuration files

### Set up TOML Configuration

1. **Start InfluxDB 3 Core with the PLUGIN\_DIR environment variable set**:
    
    ```bash
    PLUGIN_DIR=~/.plugins influxdb3 serve --node-id node0 --object-store file --data-dir ~/.influxdb3 --plugin-dir ~/.plugins
    ```
    
2. **Copy or create a TOML configuration file in your plugin directory**:
    
    ```bash
    # Example: copy a plugin's configuration template
    cp plugin_config_example.toml ~/.plugins/my_config.toml
    ```
    
3. **Edit the TOML file** to match your requirements. The TOML file should contain all the arguments defined in the plugin’s argument schema.
    
4. **Create a trigger with the `config_file_path` argument**: When creating a trigger, specify the `config_file_path` argument to point to your TOML configuration file.
    
    -   Specify only the filename (not the full path)
    -   The file must be located under `PLUGIN_DIR`
    
    ```bash
    influxdb3 create trigger \
      --database mydb \
      --plugin-filename plugin_name.py \
      --trigger-spec "every:1d" \
      --trigger-arguments config_file_path=my_config.toml \
      my_trigger_name
    ```
    

For more information on using TOML configuration files, see the project [README](https://github.com/influxdata/influxdb3_plugins/blob/master/README.md).

[plugins](/influxdb3/core/tags/plugins/) [processing engine](/influxdb3/core/tags/processing-engine/) [python](/influxdb3/core/tags/python/)


---

## Extend plugins with API features and state management

The Processing Engine includes a shared API that your plugins can use to interact with data, write new records in line protocol format, and maintain state between executions. These capabilities let you build plugins that transform, analyze, and respond to time series data as it flows through your database.

The plugin API lets you:

-   [Write data](#write-data)
-   [Query data](#query-data)
-   [Log messages for monitoring and debugging](#log-messages-for-monitoring-and-debugging)
-   [Maintain state with the in-memory cache](#maintain-state-with-in-memory-cache)
    -   [Store and retrieve cached data](#store-and-retrieve-cached-data)
    -   [Use TTL appropriately](#use-ttl-appropriately)
    -   [Share data across plugins](#share-data-across-plugins)
    -   [Build a counter](#building-a-counter)
-   [Guidelines for in-memory caching](#guidelines-for-in-memory-caching)
    -   [Consider cache limitations](#consider-cache-limitations)

## Get started with the shared API

Each plugin automatically has access to the shared API through the `influxdb3_local` object. You don’t need to import any libraries. The API becomes available as soon as your plugin runs.

If your plugin requires third-party Python packages (like `pandas`, `requests`, or `influxdb3-python`), see [Manage plugin dependencies](/influxdb3/core/plugins/#manage-plugin-dependencies) for installation instructions.

## Write data

To write data into your database, use the `LineBuilder` API to create line protocol data:

```python
# Create a line protocol entry
line = LineBuilder("weather")
line.tag("location", "us-midwest")
line.float64_field("temperature", 82.5)
line.time_ns(1627680000000000000)

# Write the data to the database
influxdb3_local.write(line)
```

InfluxDB 3 buffers your writes while the plugin runs and flushes them when the plugin completes.

[](#view-the-linebuilder-python-implementation)

View the `LineBuilder` Python implementation

```python
from typing import Optional
from collections import OrderedDict

class InfluxDBError(Exception):
    """Base exception for InfluxDB-related errors"""
    pass

class InvalidMeasurementError(InfluxDBError):
    """Raised when measurement name is invalid"""
    pass

class InvalidKeyError(InfluxDBError):
    """Raised when a tag or field key is invalid"""
    pass

class InvalidLineError(InfluxDBError):
    """Raised when a line protocol string is invalid"""
    pass

class LineBuilder:
    def __init__(self, measurement: str):
        if ' ' in measurement:
            raise InvalidMeasurementError("Measurement name cannot contain spaces")
        self.measurement = measurement
        self.tags: OrderedDict[str, str] = OrderedDict()
        self.fields: OrderedDict[str, str] = OrderedDict()
        self._timestamp_ns: Optional[int] = None

    def _validate_key(self, key: str, key_type: str) -> None:
        """Validate that a key does not contain spaces, commas, or equals signs."""
        if not key:
            raise InvalidKeyError(f"{key_type} key cannot be empty")
        if ' ' in key:
            raise InvalidKeyError(f"{key_type} key '{key}' cannot contain spaces")
        if ',' in key:
            raise InvalidKeyError(f"{key_type} key '{key}' cannot contain commas")
        if '=' in key:
            raise InvalidKeyError(f"{key_type} key '{key}' cannot contain equals signs")

    def tag(self, key: str, value: str) -> 'LineBuilder':
        """Add a tag to the line protocol."""
        self._validate_key(key, "tag")
        self.tags[key] = str(value)
        return self

    def uint64_field(self, key: str, value: int) -> 'LineBuilder':
        """Add an unsigned integer field to the line protocol."""
        self._validate_key(key, "field")
        if value < 0:
            raise ValueError(f"uint64 field '{key}' cannot be negative")
        self.fields[key] = f"{value}u"
        return self

    def int64_field(self, key: str, value: int) -> 'LineBuilder':
        """Add an integer field to the line protocol."""
        self._validate_key(key, "field")
        self.fields[key] = f"{value}i"
        return self

    def float64_field(self, key: str, value: float) -> 'LineBuilder':
        """Add a float field to the line protocol."""
        self._validate_key(key, "field")
        # Check if value has no decimal component
        self.fields[key] = f"{int(value)}.0" if value % 1 == 0 else str(value)
        return self

    def string_field(self, key: str, value: str) -> 'LineBuilder':
        """Add a string field to the line protocol."""
        self._validate_key(key, "field")
        # Escape quotes and backslashes in string values
        escaped_value = value.replace('"', '\\"').replace('\\', '\\\\')
        self.fields[key] = f'"{escaped_value}"'
        return self

    def bool_field(self, key: str, value: bool) -> 'LineBuilder':
        """Add a boolean field to the line protocol."""
        self._validate_key(key, "field")
        self.fields[key] = 't' if value else 'f'
        return self

    def time_ns(self, timestamp_ns: int) -> 'LineBuilder':
        """Set the timestamp in nanoseconds."""
        self._timestamp_ns = timestamp_ns
        return self

    def build(self) -> str:
        """Build the line protocol string."""
        # Start with measurement name (escape commas only)
        line = self.measurement.replace(',', '\\,')

        # Add tags if present
        if self.tags:
            tags_str = ','.join(
                f"{k}={v}" for k, v in self.tags.items()
            )
            line += f",{tags_str}"

        # Add fields (required)
        if not self.fields:
            raise InvalidLineError(f"At least one field is required: {line}")

        fields_str = ','.join(
            f"{k}={v}" for k, v in self.fields.items()
        )
        line += f" {fields_str}"

        # Add timestamp if present
        if self._timestamp_ns is not None:
            line += f" {self._timestamp_ns}"

        return line
```

## Query data

Your plugins can execute SQL queries and process results directly:

```python
# Simple query
results = influxdb3_local.query("SELECT * FROM metrics WHERE time > now() - INTERVAL '1 hour'")

# Parameterized query for safer execution
params = {"table": "metrics", "threshold": 90}
results = influxdb3_local.query("SELECT * FROM $table WHERE value > $threshold", params)
```

Query results are a `List` of `Dict[String, Any]`, where each dictionary represents a row. Column names are keys, and column values are the corresponding values.

## Log messages for monitoring and debugging

Use the shared API’s `info`, `warn`, and `error` functions to log messages from your plugin. Each function accepts one or more arguments, converts them to strings, and logs them as a space-separated message.

Add logging to monitor plugin execution and assist with debugging:

```python
influxdb3_local.info("Starting data processing")
influxdb3_local.warn("Could not process some records")
influxdb3_local.error("Failed to connect to external API")

# Log structured data
obj_to_log = {"records": 157, "errors": 3}
influxdb3_local.info("Processing complete", obj_to_log)
```

The system writes all log messages to the server logs and stores them in [system tables](/influxdb3/core/reference/cli/influxdb3/show/system/summary/), where you can query them using SQL.

## Maintain state with the in-memory cache

The Processing Engine provides an in-memory cache that enables your plugins to persist and retrieve data between executions.

Access the cache using the `cache` property of the shared API:

```python
# Basic usage pattern  
influxdb3_local.cache.METHOD(PARAMETERS)
```

`cache` provides the following methods to retrieve and manage cached values:

| Method | Parameters | Returns | Description |
| --- | --- | --- | --- |
| put | key (str): The key to store the value undervalue (Any): Any Python object to cachettl (Optional[float], default=None): Time in seconds before expirationuse_global (bool, default=False): If True, uses global namespace | None | Stores a value in the cache with an optional time-to-live |
| get | key (str): The key to retrievedefault (Any, default=None): Value to return if key not founduse_global (bool, default=False): If True, uses global namespace | Any | Retrieves a value from the cache or returns default if not found |
| delete | key (str): The key to deleteuse_global (bool, default=False): If True, uses global namespace | bool | Deletes a value from the cache. Returns True if deleted, False if not found |

### Understanding cache namespaces

The cache system offers two distinct namespaces:

| Namespace | Scope | Best For |
| --- | --- | --- |
| Trigger-specific (default) | Isolated to a single trigger | Plugin state, counters, timestamps specific to one plugin |
| Global | Shared across all triggers | Configuration, lookup tables, service states that should be available to all plugins |

### Common cache operations

-   [Store and retrieve cached data](#store-and-retrieve-cached-data)
-   [Store cached data with expiration](#store-cached-data-with-expiration)
-   [Share data across plugins](#share-data-across-plugins)
-   [Build a counter](#build-a-counter)

### Store and retrieve cached data

```python
# Store a value
influxdb3_local.cache.put("last_run_time", time.time())

# Retrieve a value with a default if not found
last_time = influxdb3_local.cache.get("last_run_time", default=0)

# Delete a cached value
influxdb3_local.cache.delete("temporary_data")
```

### Store cached data with expiration

```python
# Cache with a 5-minute TTL (time-to-live)
influxdb3_local.cache.put("api_response", response_data, ttl=300)
```

### Share data across plugins

```python
# Store in the global namespace
influxdb3_local.cache.put("config", {"version": "1.0"}, use_global=True)

# Retrieve from the global namespace
config = influxdb3_local.cache.get("config", use_global=True)
```

### Building a counter

You can track how many times a plugin has run:

```python
# Get current counter or default to 0
counter = influxdb3_local.cache.get("execution_count", default=0)

# Increment counter
counter += 1

# Store the updated value
influxdb3_local.cache.put("execution_count", counter)

influxdb3_local.info(f"This plugin has run {counter} times")
```

## Guidelines for in-memory caching

To get the most out of the in-memory cache, follow these guidelines:

-   [Use the trigger-specific namespace](#use-the-trigger-specific-namespace)
-   [Use TTL appropriately](#use-ttl-appropriately)
-   [Cache computation results](#cache-computation-results)
-   [Warm the cache](#warm-the-cache)
-   [Consider cache limitations](#consider-cache-limitations)

### Use the trigger-specific namespace

The Processing Engine provides a cache that supports stateful operations while maintaining isolation between different triggers. For most use cases, use the trigger-specific namespace to keep plugin state isolated. Use the global namespace only when you need to share data across triggers.

### Use TTL appropriately

Set appropriate expiration times based on how frequently your data changes:

```python
# Cache external API responses for 5 minutes  
influxdb3_local.cache.put("weather_data", api_response, ttl=300)
```

### Cache computation results

Store the results of expensive calculations that you frequently utilize:

```python
# Cache aggregated statistics  
influxdb3_local.cache.put("daily_stats", calculate_statistics(data), ttl=3600)
```

### Warm the cache

For critical data, prime the cache at startup. This can be especially useful for global namespace data where multiple triggers need the data:

```python
# Check if cache needs to be initialized  
if not influxdb3_local.cache.get("lookup_table"):   
    influxdb3_local.cache.put("lookup_table", load_lookup_data())
```

### Consider cache limitations

-   **Memory Usage**: Since the system stores cache contents in memory, monitor your memory usage when caching large datasets.
-   **Server Restarts**: Because the server clears the cache on restart, design your plugins to handle cache initialization (as noted above).
-   **Concurrency**: Be cautious of accessing inaccurate or out-of-date data when multiple trigger instances might simultaneously update the same cache key.

## Next Steps

With an understanding of the InfluxDB 3 Shared Plugin API, you can start building data workflows that transform, analyze, and respond to your time series data.

For official plugins and examples that you can extend, see the [plugin library](/influxdb3/core/plugins/library/).

#### Related

-   [influxdb3 create trigger](/influxdb3/core/reference/cli/influxdb3/create/trigger/)
-   [influxdb3 test](/influxdb3/core/reference/cli/influxdb3/test/)
-   [Processing engine reference](/influxdb3/core/reference/processing-engine/)

[processing engine](/influxdb3/core/tags/processing-engine/) [plugins](/influxdb3/core/tags/plugins/) [API](/influxdb3/core/tags/api/) [python](/influxdb3/core/tags/python/)

