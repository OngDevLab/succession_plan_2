# User Access Control System

## Overview
Implemented a comprehensive 3-tier user access control system with submission status tracking for succession planning. The system includes role-based permissions, filtered search results, and approval workflows.

## ✅ **Features Implemented**

### 1. **User Access Database**
- **SQLite Table**: `user_access` (mirrors Snowflake structure)
- **Test Data**: 6 users across 3 tiers with realistic access patterns
- **JSON Arrays**: Segments and employee IDs stored as JSON text

### 2. **Three-Tier Access System**

#### **Tier 1 Users** (HR/Senior Leadership)
- ✅ **Full segment access**: Can see all employees in their assigned segments
- ✅ **Search capability**: Full search with segment filtering
- ✅ **Approval rights**: Can approve Tier 2 submissions
- ✅ **Self-approval**: Can approve their own submissions
- **Test Users**: 2 users with multiple segments each

#### **Tier 2 Users** (Middle Management)
- ✅ **Employee-specific access**: Can only see employees assigned to them
- ✅ **Search capability**: Search with employee ID filtering
- ✅ **Submit for approval**: Must submit to Tier 1 for approval
- ✅ **Segment restriction**: Must be in their assigned segments
- **Test Users**: 2 users with 5 employees each

#### **Tier 3 Users** (Individual Contributors)
- ✅ **No search capability**: Cannot perform searches
- ✅ **Assigned incumbents only**: See only pre-assigned incumbents
- ✅ **Form completion**: Can fill out forms for assigned employees
- ✅ **Submit for approval**: Must submit to Tier 1 for approval
- **Test Users**: 2 users with 1 employee each

### 3. **Submission Status Tracking**
- **Status Values**: `not_complete`, `saved`, `submitted`, `approved`, `needs_edit`
- **Audit Trail**: Tracks who submitted, approved, or requested edits
- **Timestamps**: Full timestamp tracking for all status changes

### 4. **User Interface Enhancements**

#### **User Selection (Testing)**
- **Dropdown**: Select from 6 test users in sidebar
- **Display Info**: Shows tier, segment count, employee count
- **Access Validation**: Prevents actions without user selection

#### **Filtered Search Results**
- **Tier 1**: Shows all employees in user's segments
- **Tier 2**: Shows only assigned employees in user's segments  
- **Tier 3**: No search - shows assigned incumbents directly
- **Result Counts**: Displays "X of Y results (filtered by access level)"

#### **Enhanced Save Options**
- **Save Draft**: Saves with `saved` status
- **Submit for Review**: Saves with `submitted` status
- **Access Control**: Validates user permissions before saving

## 🔧 **Technical Implementation**

### Database Schema

#### **user_access Table**
```sql
CREATE TABLE user_access (
    WORK_PRIMARY_EMAIL TEXT,
    USER_ID TEXT,
    EMPLOYEE_ID TEXT,
    HR_ACCESS BOOLEAN,
    TIER_1_ACCESS_IND BOOLEAN,
    TIER_2_ACCESS_IND BOOLEAN,
    TIER_3_ACCESS_IND BOOLEAN,
    SUCCESSION_PLAN_SEGMENT TEXT,  -- JSON array
    L2_LEADER_EMPLOYEE_ID TEXT,
    L3_LEADER_EMPLOYEE_ID TEXT,
    LEADER_EMPLOYEE_ID TEXT,  -- JSON array
    POSITION_SPECIFIC_ACCESS TEXT,
    MARKET_MOVING_ID TEXT,
    CREATED_BY TEXT,
    CREATED_ON TIMESTAMP,
    UPDATED_BY TEXT,
    UPDATED_ON TIMESTAMP
)
```

#### **succession_plans Table (Enhanced)**
```sql
-- Added columns:
SUBMISSION_STATUS TEXT DEFAULT "not_complete"
SUBMITTED_BY TEXT
SUBMITTED_ON TIMESTAMP
APPROVED_BY TEXT
APPROVED_ON TIMESTAMP
EDIT_REQUESTED_BY TEXT
EDIT_REQUESTED_ON TIMESTAMP
EDIT_COMMENTS TEXT
```

### Access Control Functions

#### **Core Functions**
- `get_user_access(email)` - Retrieve user permissions
- `get_all_test_users()` - Get test users for dropdown
- `filter_incumbents_by_access(results, user_access)` - Filter search results
- `can_user_search(user_access)` - Check search permissions
- `can_user_submit(user_access)` - Check submission permissions
- `can_user_approve(user_access)` - Check approval permissions

#### **Filtering Logic**
```python
# Tier 1: Segment-based filtering
if person_segment in user_segments:
    include_person()

# Tier 2: Segment + Employee ID filtering  
if person_segment in user_segments and person_id in leader_ids:
    include_person()

# Tier 3: Employee ID only (no search)
if person_id in leader_ids:
    include_person()
```

## 📊 **Test Data Structure**

### **Sample Users Created**
1. **tier1.user1@disney.com** - Tier 1, 3 segments, 0 specific employees
2. **tier1.user2@disney.com** - Tier 1, 3 segments, 0 specific employees  
3. **tier2.user1@disney.com** - Tier 2, 1 segment, 5 employees
4. **tier2.user2@disney.com** - Tier 2, 1 segment, 5 employees
5. **tier3.user1@disney.com** - Tier 3, 1 segment, 1 employee
6. **tier3.user2@disney.com** - Tier 3, 1 segment, 1 employee

### **Segments Used**
- Disney Experiences
- Walt Disney Studio Entertainment  
- Disney Entertainment & ESPN Technology
- And others from existing employee data

## 🎯 **User Experience Flow**

### **Tier 1 Workflow**
1. Select Tier 1 user from dropdown
2. Search for any employee in their segments
3. Create succession plans
4. Save as draft or submit for review
5. Can approve their own or others' submissions

### **Tier 2 Workflow**  
1. Select Tier 2 user from dropdown
2. Search limited to their assigned employees
3. Create succession plans for assigned employees
4. Submit for Tier 1 approval
5. Cannot approve submissions

### **Tier 3 Workflow**
1. Select Tier 3 user from dropdown
2. See only their assigned incumbent(s)
3. Fill out succession plan forms
4. Submit for Tier 1 approval
5. No search capability

## 🔒 **Security Features**

### **Access Validation**
- ✅ User must be selected before any actions
- ✅ Search results filtered by user permissions
- ✅ Save/submit actions validate user tier
- ✅ Approval actions restricted to Tier 1

### **Data Isolation**
- ✅ Users only see data they have access to
- ✅ Search results automatically filtered
- ✅ No data leakage between access levels

## 📁 **Files Created/Modified**

### **New Files**
1. **`database/user_access.py`** - User access management functions
2. **`USER_ACCESS_SYSTEM.md`** - This documentation

### **Modified Files**
1. **`main.py`** - Added user selection UI and access control
2. **Database tables** - Added user_access and submission status columns

### **Database Changes**
1. **`user_access` table** - Created with 6 test users
2. **`succession_plans` table** - Added 8 submission status columns

## 🚀 **Ready for Testing**

The system is fully functional and ready for testing:

1. **Run the app**: `streamlit run main.py`
2. **Select a test user** from the sidebar dropdown
3. **Test different access levels** by switching between users
4. **Verify filtering** works correctly for each tier
5. **Test submission workflow** with different user types

The system provides a complete foundation for role-based access control and can be easily extended when OIDC authentication is implemented later.
