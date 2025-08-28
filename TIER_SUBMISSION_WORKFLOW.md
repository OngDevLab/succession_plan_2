# Corrected Tier Submission Workflow

## Overview
Updated the submission workflow to properly reflect the tier-based permissions and approval process based on organizational hierarchy and responsibilities.

## ✅ **Corrected Workflow by Tier**

### **Tier 1 Users (Senior Leadership)**
- **Button**: "📤 Submit" 
- **Status**: `approved` (auto-approved)
- **Workflow**: Submit → Automatically Approved
- **Rationale**: Senior leadership can approve their own succession plans
- **Message**: "As a Tier 1 user, your submission is automatically approved."

### **Tier 2 Users (Middle Management)**  
- **Button**: "📤 Submit for Review"
- **Status**: `submitted` (needs Tier 1 approval)
- **Workflow**: Submit → Tier 1 Review → Approved/Rejected/Edit Request
- **Rationale**: Middle management needs senior leadership approval
- **Message**: "Your submission will be reviewed by a Tier 1 user."

### **Tier 3 Users (Individual Contributors)**
- **Button**: "📤 Submit"
- **Status**: `submitted` (fire and forget to Tier 1)
- **Workflow**: Submit → Tier 1 Review → Approved/Rejected/Edit Request  
- **Rationale**: Individual contributors submit directly to senior leadership
- **Message**: "Your submission has been sent for review."

## 🔄 **Approval Workflow Logic**

### **Tier 1 Review Dashboard**
- **Shows**: Only submissions from Tier 2 and Tier 3 users
- **Filters**: `USER_TIER IN (2, 3)` and `SUBMISSION_STATUS = 'submitted'`
- **Actions**: Approve, Accept & Edit, Request Edits
- **Scope**: All submissions within their segments

### **Auto-Approval Logic**
- **Tier 1**: Submissions automatically get `approved` status
- **Tier 2/3**: Submissions get `submitted` status and require Tier 1 review
- **Database**: Status field tracks the workflow state

## 🎯 **Button Labels by Tier**

| Tier | Button Text | Status Saved | Needs Review |
|------|-------------|--------------|--------------|
| 1 | "📤 Submit" | `approved` | No (auto-approved) |
| 2 | "📤 Submit for Review" | `submitted` | Yes (Tier 1) |
| 3 | "📤 Submit" | `submitted` | Yes (Tier 1) |

## 🔧 **Technical Implementation**

### **Submission Logic**
```python
if user_access['tier'] == 1:
    # Tier 1: Auto-approved
    status = 'approved'
    message = "automatically approved"
    
elif user_access['tier'] == 2:
    # Tier 2: Needs review
    status = 'submitted' 
    message = "submitted for Tier 1 review"
    
elif user_access['tier'] == 3:
    # Tier 3: Fire and forget
    status = 'submitted'
    message = "sent for review"
```

### **Review Dashboard Filtering**
```sql
-- Only show Tier 2 and 3 submissions for Tier 1 review
WHERE USER_TIER IN (2, 3) 
AND SUBMISSION_STATUS = 'submitted'
```

### **Approval Functions**
```sql
-- Approval/edit requests only work on Tier 2/3 submissions
WHERE USER_TIER IN (2, 3)
AND SUBMISSION_STATUS = 'submitted'
```

## 📊 **Workflow States**

### **Status Progression**
```
Tier 1: Draft → approved (final)
Tier 2: Draft → submitted → approved/needs_edit
Tier 3: Draft → submitted → approved/needs_edit
```

### **Status Meanings**
- **`saved`**: Draft saved but not submitted
- **`submitted`**: Submitted for Tier 1 review (Tier 2/3 only)
- **`approved`**: Approved by Tier 1 or auto-approved (Tier 1)
- **`needs_edit`**: Tier 1 requested changes (Tier 2/3 only)

## 🎮 **User Experience by Tier**

### **Tier 1 Experience**
1. Create succession plan
2. Click "Submit" → Automatically approved
3. See "Your submission is automatically approved"
4. Review Tier 2/3 submissions in dashboard
5. Approve/reject/request edits on others' submissions

### **Tier 2 Experience**  
1. Create succession plan for assigned employees
2. Click "Submit for Review" → Goes to Tier 1
3. See "Your submission will be reviewed by a Tier 1 user"
4. Wait for Tier 1 approval/feedback
5. Address edit requests if needed

### **Tier 3 Experience**
1. Create succession plan for assigned incumbent
2. Click "Submit" → Goes to Tier 1  
3. See "Your submission has been sent for review"
4. Fire and forget - no further action needed
5. Address edit requests if Tier 1 sends feedback

## 🔒 **Security & Access Control**

### **Submission Rights**
- **Tier 1**: Can submit and auto-approve own plans
- **Tier 2**: Can submit plans for assigned employees (needs approval)
- **Tier 3**: Can submit plans for assigned incumbent (needs approval)

### **Review Rights**
- **Tier 1**: Can review all Tier 2/3 submissions in their segments
- **Tier 2/3**: Cannot review others' submissions

### **Approval Rights**
- **Tier 1**: Can approve/reject/request edits on Tier 2/3 submissions
- **Tier 2/3**: Cannot approve submissions

## 🚀 **Benefits of Corrected Workflow**

### **Organizational Alignment**
- ✅ **Tier 1**: Senior leadership autonomy (auto-approval)
- ✅ **Tier 2**: Middle management oversight (needs approval)
- ✅ **Tier 3**: Individual contributor simplicity (fire and forget)

### **Efficient Process**
- ✅ **Reduced Bottlenecks**: Tier 1 doesn't need approval from anyone
- ✅ **Appropriate Oversight**: Tier 2/3 get proper review
- ✅ **Clear Workflow**: Each tier knows exactly what happens

### **User Experience**
- ✅ **Clear Expectations**: Button text matches actual workflow
- ✅ **Appropriate Messaging**: Users know what to expect
- ✅ **Simplified Process**: Each tier has appropriate complexity level

The corrected workflow now properly reflects organizational hierarchy and provides the right level of oversight and autonomy for each tier level.
