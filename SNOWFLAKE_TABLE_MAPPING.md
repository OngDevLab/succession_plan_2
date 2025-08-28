# Snowflake Table Update Mapping

## Overview
Mapping between your original Snowflake table and the updated version with collaborative workflow support.

## 📊 **Column Mapping**

### **✅ Columns Kept (Same Name)**
| Original Column | Status | Usage |
|----------------|--------|-------|
| `SUCCESSION_RECORD_ID` | ✅ Kept | Primary key (auto-increment) |
| `INCUMBENT_EMPLOYEE_ID` | ✅ Kept | Incumbent identifier |
| `INCUMBENT_L2_LEADER_ID` | ✅ Kept | Leadership hierarchy |
| `INCUMBENT_L3_LEADER_ID` | ✅ Kept | Leadership hierarchy |
| `INCUMBENT_SUCCESSION_PLAN_SEGMENT_GROUP` | ✅ Kept | Segment grouping |
| `CRITICAL_ROLE_IND` | ✅ Kept | Critical role flag |
| `INCUMBENT_TOP_PLE` | ✅ Kept | People Leader Expectation |
| `INCUMBENT_CONTRACT_END_DATE` | ✅ Kept | Contract end date |
| `SUCCESSOR_EMPLOYEE_ID` | ✅ Kept | Successor identifier |
| `SUCCESSOR_READINESS` | ✅ Kept | Readiness level |
| `SUCCESSOR_FUTURE_READINESS_TIMING` | ✅ Kept | Future timing |
| `SUCCESSOR_CONTRACT_END_DATE` | ✅ Kept | Successor contract |
| `SUCCESSOR_STRENGTHS` | ✅ Kept | Successor strengths |
| `SUCCESSOR_TOP_SKILLS` | ✅ Kept | Successor skills (JSON) |
| `SUCCESSOR_TOP_PLE` | ✅ Kept | Successor PLE |
| `SUCCESSOR_DEVELOPMENT_FOCUS` | ✅ Kept | Development focus |
| `SUCCESSOR_TALENT_ACTIONS` | ✅ Kept | Talent actions |

### **🔄 Columns Renamed**
| Original Column | New Column | Reason |
|----------------|------------|--------|
| `SUCCESSION_PLAN_STATUS` | `SUCCESSION_PLAN_STATUS` | ✅ Same (workflow status) |
| `INCUMBENT_ROLE_RESPONSIBILITIES` | `INCUMBENT_ROLE_RESPONSIBILITIES` | ✅ Same |
| `INCUMBENT_TOP_SKILLS` | `INCUMBENT_TOP_SKILLS` | ✅ Same (JSON array) |
| `INCUMBENT_SOURCING_STRATEGY` | `INCUMBENT_SOURCING_STRATEGY` | ✅ Same (JSON array) |
| `INCUMBENT_ROLE_TYPE` | `INCUMBENT_ROLE_TYPE` | ✅ Same |
| `INCUMBENT_ROLE_SCENARIO_PLAN` | `INCUMBENT_ROLE_SCENARIO_PLAN` | ✅ Same |
| `INCUMBENT_ADDITIONAL_POSITION_TITLE` | `INCUMBENT_ADDITIONAL_POSITION_TITLE` | ✅ Same |
| `ROW_CREATED_BY` | `ROW_CREATED_BY` | ✅ Same (now email-based) |
| `ROW_CREATED_ON` | `ROW_CREATED_ON` | ✅ Same (auto-timestamp) |
| `ROW_CREATED_TIER` | `ROW_CREATED_TIER` | ✅ Same (user tier) |

### **➕ New Columns Added**
| New Column | Type | Purpose |
|------------|------|---------|
| `INCUMBENT_FIRST_NAME` | VARCHAR | Person identification |
| `INCUMBENT_LAST_NAME` | VARCHAR | Person identification |
| `INCUMBENT_EMAIL` | VARCHAR | Contact information |
| `INCUMBENT_POSITION_TITLE` | VARCHAR | Position details |
| `INCUMBENT_MANAGEMENT_LEVEL` | VARCHAR | Management hierarchy |
| `INCUMBENT_JOB_LEVEL` | VARCHAR | Job level |
| `INCUMBENT_SEGMENT` | VARCHAR | Business segment |
| `SUCCESSOR_FIRST_NAME` | VARCHAR | Person identification |
| `SUCCESSOR_LAST_NAME` | VARCHAR | Person identification |
| `SUCCESSOR_EMAIL` | VARCHAR | Contact information |
| `SUCCESSOR_POSITION_TITLE` | VARCHAR | Position details |
| `SUCCESSOR_MANAGEMENT_LEVEL` | VARCHAR | Management hierarchy |
| `SUCCESSOR_JOB_LEVEL` | VARCHAR | Job level |
| `SUCCESSOR_SEGMENT` | VARCHAR | Business segment |
| `REMOVED` | BOOLEAN | Soft delete flag |
| `SUBMITTED_BY` | VARCHAR | Email of submitter (OIDC) |
| `SUBMITTED_ON` | TIMESTAMP | Submission timestamp |
| `APPROVED_BY` | VARCHAR | Email of approver (OIDC) |
| `APPROVED_ON` | TIMESTAMP | Approval timestamp |
| `EDIT_REQUESTED_BY` | VARCHAR | Email of edit requester (OIDC) |
| `EDIT_REQUESTED_ON` | TIMESTAMP | Edit request timestamp |
| `EDIT_COMMENTS` | VARCHAR | Edit comments (unused) |
| `ROW_CREATED_USER_SEGMENTS` | VARCHAR | User segments (JSON) |

### **❌ Columns Removed**
| Original Column | Reason for Removal |
|----------------|-------------------|
| `INCUMBENT_POSITION_ID` | Replaced with `INCUMBENT_POSITION_TITLE` |
| `SUCCESSOR_POSITION_ID` | Replaced with `SUCCESSOR_POSITION_TITLE` |

## 🔄 **Key Changes**

### **1. Enhanced Person Data**
- **Added Names**: First/Last names for both incumbent and successor
- **Added Emails**: Contact information for both parties
- **Added Position Titles**: Human-readable position names
- **Added Levels**: Management and job levels for hierarchy

### **2. Collaborative Workflow**
- **SUBMITTED_BY**: Email of user who submitted (OIDC compliant)
- **APPROVED_BY**: Email of Tier 1 user who approved
- **EDIT_REQUESTED_BY**: Email of user who requested edits
- **Timestamps**: Full audit trail of all workflow actions

### **3. Data Integrity**
- **REMOVED**: Soft delete flag instead of hard deletes
- **Enhanced Tracking**: User segments and tier information
- **OIDC Compliance**: All user references use email addresses

### **4. Status Values**
| Status | Description |
|--------|-------------|
| `not_complete` | Initial state |
| `saved` | Draft saved by user |
| `submitted` | Submitted for Tier 1 review |
| `approved` | Approved by Tier 1 |
| `needs_edit` | Sent back for editing |

## 📝 **Migration Notes**

### **Data Migration Required**
1. **Person Names**: Need to populate from HR system
2. **Position Titles**: Map from position IDs to titles
3. **Management/Job Levels**: Extract from HR hierarchy
4. **Email Addresses**: Populate from employee directory

### **Workflow Status Migration**
```sql
-- Map old status values to new ones
UPDATE TBL_SL_SUCCESSION_PLAN_DETAIL 
SET SUCCESSION_PLAN_STATUS = CASE 
    WHEN SUCCESSION_PLAN_STATUS = 'DRAFT' THEN 'saved'
    WHEN SUCCESSION_PLAN_STATUS = 'SUBMITTED' THEN 'submitted'
    WHEN SUCCESSION_PLAN_STATUS = 'APPROVED' THEN 'approved'
    ELSE 'not_complete'
END;
```

### **User Tracking Migration**
```sql
-- Convert user IDs to emails (requires lookup table)
UPDATE TBL_SL_SUCCESSION_PLAN_DETAIL t1
SET ROW_CREATED_BY = (
    SELECT email FROM user_lookup t2 
    WHERE t2.user_id = t1.ROW_CREATED_BY
);
```

## 🚀 **Benefits of New Structure**

### **Enhanced Collaboration**
- ✅ **Full Audit Trail**: Track every action with email and timestamp
- ✅ **Workflow Management**: Complete submission/approval cycle
- ✅ **User Attribution**: Know exactly who did what when
- ✅ **Soft Deletes**: Maintain data integrity

### **OIDC Compliance**
- ✅ **Email-Based Tracking**: All user references use email addresses
- ✅ **Authentication Ready**: Direct integration with OIDC systems
- ✅ **Cross-Reference**: Can link to user profiles via email
- ✅ **Security**: Proper user identification and authorization

### **Better Data Quality**
- ✅ **Rich Person Data**: Names, emails, positions, levels
- ✅ **Hierarchical Information**: Management and job levels
- ✅ **Contact Information**: Email addresses for communication
- ✅ **Business Context**: Segments and organizational structure

### **Operational Excellence**
- ✅ **Performance**: Proper indexing on key columns
- ✅ **Scalability**: Auto-increment primary keys
- ✅ **Maintainability**: Clear column naming and documentation
- ✅ **Flexibility**: JSON fields for arrays and extensible data

The updated table structure provides enterprise-grade succession planning with full collaboration support, audit trails, and OIDC compliance while maintaining compatibility with your existing Snowflake environment!
