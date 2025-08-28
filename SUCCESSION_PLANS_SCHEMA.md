# Succession Plans Table Schema

## Overview
The succession plans table stores all succession planning data with full audit trails, collaborative workflow support, and email-based user tracking (OIDC compliant).

## 📊 **Complete Schema (47 columns)**

### **🔑 Primary Key & Timestamps**
| Column | Type | Description | Usage |
|--------|------|-------------|-------|
| `RECORD_ID` | TEXT (PK) | UUID primary key | Auto-generated unique identifier |
| `CREATED_AT` | TIMESTAMP | Record creation time | Auto-set to CURRENT_TIMESTAMP |

### **👤 Incumbent Information (9 columns)**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `INCUMBENT_EMPLOYEE_ID` | TEXT | ✓ | Employee ID of the incumbent |
| `INCUMBENT_FIRST_NAME` | TEXT | ✓ | Incumbent's first name |
| `INCUMBENT_LAST_NAME` | TEXT | ✓ | Incumbent's last name |
| `INCUMBENT_EMAIL` | TEXT | | Incumbent's email address |
| `INCUMBENT_POSITION` | TEXT | | Incumbent's position title |
| `INCUMBENT_MANAGEMENT_LEVEL` | TEXT | | Management level (Director, VP, etc.) |
| `INCUMBENT_JOB_LEVEL` | TEXT | | Job level (5, 6, 7, etc.) |
| `INCUMBENT_SEGMENT` | TEXT | | Business segment |

### **📋 Succession Plan Details (9 columns)**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `CRITICAL_ROLE` | BOOLEAN | ✓ | Is this a critical role? |
| `RESPONSIBILITIES` | TEXT | ✓ | Role responsibilities & key attributes |
| `INCUMBENT_TOP_SKILLS` | TEXT | | JSON array of top 3 leadership skills |
| `INCUMBENT_TOP_PLE` | TEXT | ✓ | Top People Leader Expectation |
| `INCUMBENT_CONTRACT_END_DATE` | DATE | | Contract end date (if applicable) |
| `SOURCING_STRATEGY` | TEXT | ✓ | JSON array of sourcing strategies |
| `ROLE_TYPE` | TEXT | | Type of role (Succession Plan, External, etc.) |
| `SCENARIO_PLAN` | TEXT | ✓ | Scenario plan (Direct Backfill, Split Position) |
| `NEW_POSITION_TITLE` | TEXT | | New position title (if split position) |

### **👥 Successor Information (8 columns)**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `SUCCESSOR_EMPLOYEE_ID` | TEXT | ✓ | Employee ID of the successor |
| `SUCCESSOR_FIRST_NAME` | TEXT | ✓ | Successor's first name |
| `SUCCESSOR_LAST_NAME` | TEXT | ✓ | Successor's last name |
| `SUCCESSOR_EMAIL` | TEXT | | Successor's email address |
| `SUCCESSOR_POSITION` | TEXT | | Successor's current position |
| `SUCCESSOR_MANAGEMENT_LEVEL` | TEXT | | Successor's management level |
| `SUCCESSOR_JOB_LEVEL` | TEXT | | Successor's job level |
| `SUCCESSOR_SEGMENT` | TEXT | | Successor's business segment |

### **📈 Successor Assessment (8 columns)**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `SUCCESSOR_READINESS` | TEXT | ✓ | Readiness level (Ready Now, Ready Future) |
| `SUCCESSOR_FUTURE_READINESS_TIMING` | TEXT | | Future readiness timing (+1-2 years, etc.) |
| `SUCCESSOR_CONTRACT_END_DATE` | DATE | | Successor's contract end date |
| `SUCCESSOR_STRENGTHS` | TEXT | ✓ | Successor's strengths |
| `SUCCESSOR_TOP_SKILLS` | TEXT | | JSON array of successor's top skills |
| `SUCCESSOR_TOP_PLE` | TEXT | ✓ | Successor's top PLE |
| `SUCCESSOR_DEVELOPMENT_FOCUS` | TEXT | ✓ | Development focus & opportunities |
| `SUCCESSOR_TALENT_ACTIONS` | TEXT | ✓ | Talent development actions |

### **🔄 Workflow Management (11 columns)**
| Column | Type | Default | Description | Usage |
|--------|------|---------|-------------|-------|
| `REMOVED` | BOOLEAN | FALSE | Soft delete flag | Marks deleted records |
| `SUBMISSION_STATUS` | TEXT | "not_complete" | Workflow status | saved, submitted, approved, needs_edit |
| `SUBMITTED_BY` | TEXT | | Who submitted (email) | **OIDC compliant - uses email** |
| `SUBMITTED_ON` | TIMESTAMP | | When submitted | Auto-set on submission |
| `APPROVED_BY` | TEXT | | Who approved (email) | **OIDC compliant - uses email** |
| `APPROVED_ON` | TIMESTAMP | | When approved | Auto-set on approval |
| `EDIT_REQUESTED_BY` | TEXT | | Who requested edits (email) | **OIDC compliant - uses email** |
| `EDIT_REQUESTED_ON` | TIMESTAMP | | When edits requested | Auto-set on edit request |
| `EDIT_COMMENTS` | TEXT | | Edit comments | **Currently unused** |
| `USER_TIER` | INTEGER | | Submitter's tier (1, 2, 3) | For collaboration tracking |
| `USER_SEGMENTS` | TEXT | | Submitter's segments (JSON) | For access control |

### **🆔 Legacy User Tracking (1 column)**
| Column | Type | Description | Status |
|--------|------|-------------|--------|
| `USER_EMAIL` | TEXT | Legacy user email field | **Deprecated - use SUBMITTED_BY** |

## 🔄 **Workflow Status Values**

| Status | Description | Who Can Set | Next States |
|--------|-------------|-------------|-------------|
| `not_complete` | Initial state | System | saved |
| `saved` | Draft saved | Tier 2/3 | submitted, saved |
| `submitted` | Submitted for review | Tier 2/3 | approved, needs_edit |
| `approved` | Approved by Tier 1 | Tier 1 | needs_edit (reopen) |
| `needs_edit` | Sent back for editing | Tier 1 | saved, submitted |

## 🤝 **Collaborative Features**

### **Latest Record Logic**
- **Per Successor**: Each successor has independent version history
- **Latest Wins**: Most recent `CREATED_AT` for each successor per incumbent
- **Cross-User Updates**: User B can update User A's successor

### **Visibility Rules**
- **Drafts** (`saved`): Only visible to creator (`SUBMITTED_BY`)
- **Submissions** (`submitted`): Visible to all Tier 2/3 with access to incumbent
- **Approved** (`approved`): Read-only until reopened by Tier 1
- **Needs Edit** (`needs_edit`): Editable by all assigned Tier 2/3

### **Email-Based Tracking (OIDC Compliant)**
- **SUBMITTED_BY**: Email of user who submitted
- **APPROVED_BY**: Email of Tier 1 user who approved
- **EDIT_REQUESTED_BY**: Email of Tier 1 user who requested edits
- **All audit fields**: Use email addresses as primary identifiers

## 📊 **Key Queries**

### **Get Latest Submission for Incumbent**
```sql
SELECT * FROM succession_plans 
WHERE INCUMBENT_EMPLOYEE_ID = ? 
AND SUBMISSION_STATUS IN ('submitted', 'approved')
AND REMOVED = FALSE
ORDER BY CREATED_AT DESC 
LIMIT 1
```

### **Get Latest Successors for Incumbent**
```sql
WITH latest_successors AS (
    SELECT SUCCESSOR_EMPLOYEE_ID, MAX(CREATED_AT) as latest_created_at
    FROM succession_plans
    WHERE INCUMBENT_EMPLOYEE_ID = ? AND REMOVED = FALSE
    GROUP BY SUCCESSOR_EMPLOYEE_ID
)
SELECT sp.* FROM succession_plans sp
INNER JOIN latest_successors ls ON 
    sp.SUCCESSOR_EMPLOYEE_ID = ls.SUCCESSOR_EMPLOYEE_ID 
    AND sp.CREATED_AT = ls.latest_created_at
WHERE sp.INCUMBENT_EMPLOYEE_ID = ?
```

### **Get Collaborative Contributors**
```sql
SELECT INCUMBENT_EMPLOYEE_ID,
       COUNT(DISTINCT SUBMITTED_BY) as contributor_count,
       GROUP_CONCAT(DISTINCT SUBMITTED_BY || ' (T' || USER_TIER || ')') as all_contributors
FROM succession_plans
WHERE REMOVED = FALSE
GROUP BY INCUMBENT_EMPLOYEE_ID
```

## 🔒 **Security & Compliance**

### **OIDC Compliance**
- ✅ **Primary Identifiers**: All user tracking uses email addresses
- ✅ **Audit Trail**: Complete email-based tracking of all actions
- ✅ **Cross-Reference**: Can link to OIDC user profiles via email

### **Data Integrity**
- ✅ **Soft Deletes**: Uses `REMOVED` flag instead of hard deletes
- ✅ **Immutable History**: Records are never updated, only new ones created
- ✅ **Concurrent Safety**: UUID primary keys prevent conflicts
- ✅ **Timestamp Tracking**: All actions have timestamps

### **Access Control**
- ✅ **Segment-Based**: Users only see incumbents in their segments
- ✅ **Tier-Based**: Different permissions for Tier 1, 2, 3
- ✅ **Status-Based**: Edit permissions based on workflow status
- ✅ **User-Based**: Draft visibility limited to creator

## 🚀 **Production Ready Features**

1. **Scalability**: UUID primary keys, indexed lookups
2. **Audit Compliance**: Complete email-based audit trail
3. **Collaboration**: Multi-user editing with proper visibility
4. **Workflow Management**: Full approval/rejection cycle
5. **Data Integrity**: Soft deletes, immutable history
6. **OIDC Integration**: Email-based user identification
7. **Flexible Schema**: JSON fields for arrays, extensible design

The schema supports enterprise-grade succession planning with full collaboration, audit trails, and OIDC compliance!
