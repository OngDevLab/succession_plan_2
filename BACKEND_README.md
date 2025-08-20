# Backend Selection Feature

This succession planning tool now supports multiple database backends:

## Available Backends

### 1. SQLite (Local)
- **Default backend** for development and testing
- Uses local database files (`succession_db.sqlite`, `succession_plans.sqlite`)
- No additional configuration required
- Fast for small datasets

### 2. Snowflake (Cloud)
- **Production backend** for enterprise use
- Connects to Snowflake data warehouse
- Requires connection configuration
- Scalable for large datasets

## Configuration

### Snowflake Setup

#### Option 1: Streamlit Secrets (Recommended)
Create `.streamlit/secrets.toml`:
```toml
[snowflake]
account = "your-account"
user = "your-username"
password = "your-password"
warehouse = "your-warehouse"
database = "your-database"
schema = "your-schema"
```

#### Option 2: Environment Variables
Set these environment variables:
```bash
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_WAREHOUSE="your-warehouse"
export SNOWFLAKE_DATABASE="your-database"
export SNOWFLAKE_SCHEMA="your-schema"
```

#### Option 3: Config File
Update `config/config.yaml`:
```yaml
database:
  snowflake:
    account: "your-account"
    user: "your-username"
    password: "your-password"
    warehouse: "your-warehouse"
    database: "your-database"
    schema: "your-schema"
```

### Table Configuration

Update table names in `config/config.yaml`:
```yaml
database:
  snowflake:
    tables:
      incumbents: "YOUR_INCUMBENTS_TABLE"
      successors: "YOUR_SUCCESSORS_TABLE"
      succession_plans: "YOUR_SUCCESSION_PLANS_TABLE"
```

## Required Table Schema

Your Snowflake tables should have these columns:

### Incumbents/Successors Tables
- `SEGMENT_HIER_LEVEL_2_NAME` (VARCHAR)
- `PREFERRED_NAME_FIRST_NAME` (VARCHAR)
- `PREFERRED_NAME_LAST_NAME` (VARCHAR)
- `EMPLOYEE_ID` (VARCHAR)
- `POSITION_REFERENCE_ID` (VARCHAR)
- `POSITION_NBR_DESCRIPTION` (VARCHAR)
- `MANAGEMENT_LEVEL` (VARCHAR)
- `JOB_LEVEL` (VARCHAR)
- `DAYS_IN_MGMT_LEVEL` (NUMBER)
- `MGMT_LEVEL_GROUP` (VARCHAR)
- `EMAIL_PRIMARY_WORK` (VARCHAR)

## Usage

1. **Start the application**
2. **Select backend** in the sidebar under "🗄️ Database Backend"
3. **Configure Snowflake** if needed (help available in the UI)
4. **Search and create succession plans** as usual

## Features

- **Automatic backend switching** - seamlessly switch between SQLite and Snowflake
- **Connection testing** - automatic validation of Snowflake connections
- **Fallback support** - graceful degradation if Snowflake is unavailable
- **Cache management** - automatic cache clearing when switching backends
- **Status indicators** - clear visual feedback on backend status

## Installation

Install the Snowflake connector:
```bash
pip install snowflake-connector-python
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Snowflake Connection Issues
1. Check your connection parameters
2. Verify network connectivity
3. Ensure your Snowflake account is active
4. Check warehouse and database permissions

### Table Not Found Errors
1. Verify table names in config match your Snowflake schema
2. Check schema permissions
3. Ensure tables exist in the specified database/schema

### Performance Considerations
- Snowflake queries may be slower than SQLite for small datasets
- Consider using appropriate warehouse sizes for your workload
- Monitor query costs in Snowflake console

## Development

### Adding New Backends
1. Create operations module in `database/`
2. Update `backend_manager.py`
3. Add configuration to `config.yaml`
4. Update UI components as needed

### Testing
- SQLite backend works out of the box
- Snowflake backend requires valid connection parameters
- Use the connection test feature in the UI
