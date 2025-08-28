# Enhanced Collaborative Workflow

## Overview
Implemented sophisticated collaborative workflow that handles multiple Tier 2 users working on the same incumbent with proper visibility rules, submission sharing, and the ability to reopen approved plans.

## 🤝 **Collaborative Editing Scenarios**

### **Scenario 1: Multiple Tier 2s, One Submits First**

**Initial State**: 
- Tier 2 User A and User B both assigned to Incumbent X
- Both start working independently

**User A Workflow**:
1. **Creates Draft**: Saves plan with status 'saved' (only User A can see)
2. **Submits Plan**: Changes status to 'submitted' (now visible to all Tier 2s with access)
3. **Tier 1 Reviews**: Plan visible to Tier 1 for approval

**User B Workflow** (after User A submits):
1. **Sees Submission**: When User B starts planning, sees User A's submitted plan
2. **Pre-filled Form**: All fields populated with User A's values
3. **Can Edit & Resubmit**: User B can modify and submit their version
4. **Latest Wins**: User B's submission becomes the new "latest" version

### **Scenario 2: Approved Plan Needs Reopening**

**Approved State**:
- Plan has status 'approved' 
- Shows as "🟢 Approved 🔄" in dashboard
- Tier 2/3 users cannot edit

**Reopen Process**:
1. **Tier 1 Action**: Clicks "🔄 Reopen for Editing" button
2. **Status Change**: Plan status changes from 'approved' to 'needs_edit'
3. **Available for Editing**: All assigned Tier 2/3 users can now edit
4. **Collaborative Editing**: Multiple users can work on the reopened plan

## 🔍 **Visibility Rules**

### **Draft Visibility (Status: 'saved')**
- **Creator Only**: Only the user who created the draft can see it
- **Private Workspace**: Other Tier 2s assigned to same incumbent cannot see drafts
- **No Prepopulation**: Other users start with blank forms

### **Submission Visibility (Status: 'submitted')**
- **All Assigned Tier 2s**: Any Tier 2 user assigned to the incumbent can see
- **Prepopulation**: Forms pre-filled with submitted values
- **Collaboration Message**: Shows who submitted and when
- **Tier 1 Review**: Available for Tier 1 approval/rejection

### **Approved Visibility (Status: 'approved')**
- **Read-Only for Tier 2/3**: Cannot edit approved plans
- **Tier 1 Control**: Only Tier 1 can reopen for editing
- **Reopen Indicator**: Dashboard shows 🔄 symbol for reopenable plans

### **Needs Edit Visibility (Status: 'needs_edit')**
- **All Assigned Users**: Available for editing by all assigned Tier 2/3 users
- **Prepopulation**: Forms pre-filled with latest values
- **Collaborative Editing**: Multiple users can work simultaneously

## 🔧 **Technical Implementation**

### **Enhanced Prepopulation Logic**
```python
def get_collaborative_incumbent_values(employee_id, user_access):
    """
    Tier 1: Can see any submission (for review)
    Tier 2/3: Complex visibility rules:
    - Priority 1: Latest submitted/approved plan (visible to all)
    - Priority 2: User's own draft (if no submissions exist)
    """
```

### **Visibility Query (Tier 2/3)**
```sql
WITH latest_submission AS (
    -- Get latest submitted/approved plan (visible to all Tier 2s)
    SELECT * FROM succession_plans
    WHERE INCUMBENT_EMPLOYEE_ID = ?
    AND SUBMISSION_STATUS IN ('submitted', 'approved')
    ORDER BY CREATED_AT DESC LIMIT 1
),
user_draft AS (
    -- Get user's own draft (private)
    SELECT * FROM succession_plans
    WHERE INCUMBENT_EMPLOYEE_ID = ?
    AND SUBMITTED_BY = ?
    AND SUBMISSION_STATUS IN ('saved', 'needs_edit')
    ORDER BY CREATED_AT DESC LIMIT 1
)
-- Return submission if exists, otherwise user's draft
```

### **Reopen Functionality**
```python
def reopen_approved_plan(incumbent_employee_id, requester_user_access):
    """Change status from 'approved' to 'needs_edit' (Tier 1 only)"""
    UPDATE succession_plans 
    SET SUBMISSION_STATUS = 'needs_edit',
        EDIT_REQUESTED_BY = ?,
        EDIT_REQUESTED_ON = ?
    WHERE SUBMISSION_STATUS = 'approved'
```

## 📊 **Dashboard Enhancements**

### **Status Indicators**
- **🟢 Approved**: Standard approved plan
- **🟢 Approved 🔄**: Approved plan that can be reopened
- **🔵 Submitted 👥3**: Submitted plan with 3 contributors
- **🔴 Needs Edit**: Plan sent back for editing

### **Action Buttons**
- **📝 Create/Edit Plan**: Start or continue editing
- **👁️ View Existing Plan**: View read-only plan details
- **📋 Review Submission**: Review submitted plan (Tier 1 only)
- **🔄 Reopen for Editing**: Reopen approved plan (Tier 1 only)

## 🎮 **User Experience Workflows**

### **Collaborative Editing Flow**
```
Tier 2 User A:
1. Creates draft → Saves (private)
2. Submits plan → Visible to all

Tier 2 User B:
1. Starts planning → Sees User A's submission
2. Form pre-filled → Can modify and resubmit
3. Submits update → Becomes new latest version

Tier 1 User:
1. Reviews latest → Can approve or send back
2. If approved → Plan locked from editing
3. Can reopen → Makes available for editing again
```

### **Prepopulation Messages**
- **Own Draft**: "💡 Found your previous draft. Fields pre-filled with your latest values."
- **Other's Submission**: "💡 Found submission from user@email.com (Tier 2). Fields pre-filled with their latest values."
- **Own Submission**: "💡 Found your previous submission. Fields pre-filled with your latest values."

## 🔒 **Security & Data Integrity**

### **Access Control**
- **Draft Privacy**: Users can only see their own drafts
- **Submission Sharing**: Submitted plans visible to all assigned users
- **Tier Boundaries**: Tier 1 can reopen, Tier 2/3 cannot
- **Segment Restrictions**: Users only see incumbents in their segments

### **Data Consistency**
- **Latest Record Logic**: Always shows most recent submission
- **Audit Trail**: Tracks who submitted what when
- **Status Transitions**: Proper workflow state management
- **Concurrent Editing**: Handles multiple users editing same incumbent

### **Collaboration Rules**
- **Same Incumbent**: Multiple Tier 2s can work on same incumbent
- **Visibility Hierarchy**: Submissions > Drafts > Blank
- **Edit Permissions**: Based on status and user tier
- **Reopen Control**: Only Tier 1 can reopen approved plans

## 📈 **Real-World Scenarios**

### **Scenario A: Team Collaboration**
1. **Manager assigns** 3 Tier 2 users to plan for critical incumbent
2. **User 1 starts** working, saves draft (private)
3. **User 2 starts** working independently, saves draft (private)
4. **User 1 submits** first, plan becomes visible to all
5. **User 2 sees** User 1's submission, builds upon it
6. **User 3 joins** later, sees latest submission, adds input
7. **Tier 1 reviews** final collaborative result

### **Scenario B: Approved Plan Changes**
1. **Plan approved** by Tier 1, locked from editing
2. **Business changes** require plan updates
3. **Tier 1 reopens** plan for editing
4. **Tier 2 users** can now edit the approved plan
5. **Collaborative editing** resumes with latest approved version as baseline
6. **Resubmission cycle** begins again

### **Scenario C: Draft vs Submission Priority**
1. **User A** has private draft saved
2. **User B** submits plan for same incumbent
3. **User A** starts editing again
4. **System shows** User B's submission (higher priority)
5. **User A** can build upon User B's work
6. **Collaboration** happens naturally through shared submissions

## 🎯 **Benefits Achieved**

### **Enhanced Collaboration**
- ✅ **Natural Sharing**: Submissions automatically shared with team
- ✅ **Build Upon Work**: Users can enhance each other's contributions
- ✅ **No Data Loss**: Private drafts preserved until submission
- ✅ **Flexible Workflow**: Multiple paths to collaboration

### **Improved Control**
- ✅ **Tier 1 Oversight**: Can reopen approved plans when needed
- ✅ **Status Management**: Clear workflow states and transitions
- ✅ **Access Control**: Proper visibility rules for different scenarios
- ✅ **Audit Trail**: Complete tracking of collaborative activities

### **Better User Experience**
- ✅ **Smart Prepopulation**: Shows most relevant data automatically
- ✅ **Clear Messaging**: Users understand what they're seeing
- ✅ **Flexible Actions**: Different buttons for different scenarios
- ✅ **Seamless Collaboration**: Natural workflow for team planning

## 🚀 **Production Ready**

The enhanced collaborative workflow provides:

1. **Real Team Dynamics**: Multiple users can work together naturally
2. **Proper Visibility**: Right information to right users at right time
3. **Flexible Control**: Plans can be reopened when business needs change
4. **Data Integrity**: Consistent state management across all scenarios
5. **Audit Compliance**: Complete tracking of all collaborative activities

This system transforms succession planning from individual tasks into true collaborative team efforts with proper oversight and control mechanisms!
