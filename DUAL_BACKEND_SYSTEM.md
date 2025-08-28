# Dual Backend System

## Overview
The succession planning application now supports **separate backend selection** for read operations (queries) and write operations (saves), giving you maximum flexibility in how you use SQLite and Snowflake.

## 🔧 **How It Works**

### **📖 Read Backend (Queries)**
Controls where the app **reads data from**:
- Employee searches
- Loading existing succession plans
- Dashboard displays
- User access lookups
- Collaborative plan prepopulation

### **💾 Write Backend (Saves)**
Controls where the app **writes data to**:
- Saving succession plans
- Workflow operations (approve, reject, reopen)
- Audit trail updates
- Status changes

## 🎯 **Configuration Options**

### **Option 1: Development Mode**
```
📖 Read Backend:  SQLite
💾 Write Backend: SQLite
```
**Use Case**: Local development and testing
- All data stays on your machine
- Fast and reliable for development
- No network dependencies

### **Option 2: Hybrid Query Mode**
```
📖 Read Backend:  Snowflake
💾 Write Backend: SQLite
```
**Use Case**: Query live data, save locally
- Search real employee data from Snowflake
- Save succession plans to local SQLite for testing
- Good for development with real employee data

### **Option 3: Production Mode**
```
📖 Read Backend:  Snowflake
💾 Write Backend: Snowflake
```
**Use Case**: Full production deployment
- All operations use Snowflake
- Complete enterprise setup
- All data centralized in Snowflake

### **Option 4: Hybrid Save Mode**
```
📖 Read Backend:  SQLite
💾 Write Backend: Snowflake
```
**Use Case**: Test with local data, save to production
- Use local test employee data
- Save succession plans directly to Snowflake
- Good for testing Snowflake integration

## 🖥️ **User Interface**

### **Sidebar Configuration**
The sidebar now shows two separate selectors:

```
🗄️ Database Configuration

📖 Read/Query Backend:
[SQLite (Local) ▼]

💾 Write/Save Backend:
[Snowflake ▼]

Current Setup:
📖 Queries: SQLITE
💾 Saves: SNOWFLAKE
```

### **Status Display**
Shows the health of both backends:

```
🔧 Backend Status

📖 Read Backend Status:        💾 Write Backend Status:
🟢 SQLite (Local)             🟢 Snowflake
Status: Ready                  Status: Connected
```

## 🔄 **Technical Implementation**

### **Backend Manager Updates**
```python
class BackendManager:
    def get_read_backend(self):
        """Returns: 'sqlite' or 'snowflake'"""
    
    def get_write_backend(self):
        """Returns: 'sqlite' or 'snowflake'"""
    
    def set_read_backend(self, backend):
        """Set read backend independently"""
    
    def set_write_backend(self, backend):
        """Set write backend independently"""
```

### **Operation Routing**
```python
# Read operations use read backend
def search_incumbents(self, search_term):
    backend = self.get_read_backend()  # 📖
    if backend == 'snowflake':
        return search_incumbents_snowflake(search_term)
    else:
        return search_incumbents_sqlite(search_term)

# Write operations use write backend
def save_succession_plan(self, data):
    backend = self.get_write_backend()  # 💾
    if backend == 'snowflake':
        return save_succession_plan_snowflake(data)
    else:
        return save_succession_plan_sqlite(data)
```

## 📊 **Operation Mapping**

### **Read Operations** 📖
| Operation | Description | Backend Used |
|-----------|-------------|--------------|
| `search_incumbents()` | Search for incumbents | Read Backend |
| `search_successors()` | Search for successors | Read Backend |
| `get_user_access()` | Get user permissions | Read Backend |
| `get_collaborative_values()` | Load existing plans | Read Backend |
| `get_employee_dashboard()` | Dashboard data | Read Backend |

### **Write Operations** 💾
| Operation | Description | Backend Used |
|-----------|-------------|--------------|
| `save_succession_plan()` | Save new plans | Write Backend |
| `approve_submission()` | Approve plans | Write Backend |
| `request_edits()` | Request changes | Write Backend |
| `reopen_approved_plan()` | Reopen plans | Write Backend |

## 🎮 **Usage Scenarios**

### **Scenario 1: Development**
**Setup**: SQLite → SQLite
```
1. Use local test data for searches
2. Save plans to local database
3. Test all features offline
4. No Snowflake connection needed
```

### **Scenario 2: Data Validation**
**Setup**: Snowflake → SQLite
```
1. Query real employee data from Snowflake
2. Validate data quality and completeness
3. Save test plans locally
4. Verify search functionality with real data
```

### **Scenario 3: Integration Testing**
**Setup**: SQLite → Snowflake
```
1. Use controlled test employee data
2. Test Snowflake save functionality
3. Verify table structure and data types
4. Test collaborative workflow in Snowflake
```

### **Scenario 4: Production**
**Setup**: Snowflake → Snowflake
```
1. Full production deployment
2. All data in Snowflake
3. Complete audit trail
4. Enterprise-grade performance
```

## 🔒 **Security & Compliance**

### **Data Flow Control**
- **Read Backend**: Controls data sources and access patterns
- **Write Backend**: Controls data persistence and audit trails
- **Independent Security**: Each backend can have different security models

### **Audit Trail**
- **SQLite Writes**: Local audit trail in SQLite database
- **Snowflake Writes**: Enterprise audit trail in Snowflake
- **Mixed Mode**: Audit trails in respective write backends

### **OIDC Compliance**
- Both backends support email-based user identification
- Consistent user tracking across read/write operations
- Full compliance regardless of backend combination

## 🚀 **Benefits**

### **Flexibility**
✅ **Development Freedom**: Use any combination for different needs
✅ **Gradual Migration**: Move from SQLite to Snowflake incrementally
✅ **Testing Options**: Test components independently
✅ **Deployment Flexibility**: Different setups for different environments

### **Performance**
✅ **Optimized Reads**: Use fastest backend for queries
✅ **Optimized Writes**: Use most reliable backend for saves
✅ **Load Distribution**: Separate read/write loads
✅ **Caching Strategy**: Independent caching per backend

### **Risk Management**
✅ **Backup Strategy**: Save to multiple backends if needed
✅ **Fallback Options**: Switch backends if one fails
✅ **Data Validation**: Compare results across backends
✅ **Incremental Rollout**: Test writes while keeping reads stable

## 🎯 **Recommended Configurations**

### **For Development**
- **Read**: SQLite (fast, reliable, offline)
- **Write**: SQLite (immediate feedback, no network issues)

### **For Testing Snowflake Integration**
- **Read**: SQLite (controlled test data)
- **Write**: Snowflake (test production saves)

### **For Data Validation**
- **Read**: Snowflake (real employee data)
- **Write**: SQLite (don't affect production)

### **For Production**
- **Read**: Snowflake (live employee data)
- **Write**: Snowflake (centralized succession plans)

The dual backend system gives you complete control over your data flow while maintaining all the collaborative workflow features and OIDC compliance! 🎉
