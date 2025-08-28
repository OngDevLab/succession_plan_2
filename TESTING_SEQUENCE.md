# Collaborative Workflow Testing Sequence

## 🎯 **Test Users & Scenarios**

Based on our collaborative test data, here are the optimal testing sequences:

### **Test Users Available:**
- **Tier 1**: `tier1.user1@disney.com` (oversees Walt Disney Television + 3 other segments)
- **Tier 2**: `tier2.user1@disney.com`, `tier2.user2@disney.com`, `tier2.user3@disney.com` (all work on Walt Disney Television)
- **Shared Incumbents**: These 3 Tier 2 users have overlapping access to the same incumbents

## 🧪 **Testing Sequence**

### **Phase 1: Draft Privacy Testing**
**Objective**: Verify drafts are private to creators

1. **Login as `tier2.user1@disney.com`**
   - Go to dashboard
   - Select a Walt Disney Television incumbent (one that shows in your list)
   - Click "📝 Create/Edit Plan"
   - Fill out incumbent plan details
   - **Save as Draft** (don't submit yet)
   - Note the incumbent Employee ID

2. **Login as `tier2.user2@disney.com`**
   - Go to dashboard
   - Find the SAME incumbent that user1 just worked on
   - Click "📝 Create/Edit Plan"
   - **Verify**: Form should be blank (no prepopulation from user1's draft)
   - Fill out different plan details
   - **Save as Draft**

3. **Login as `tier2.user1@disney.com`**
   - Go back to the same incumbent
   - **Verify**: Should see your own draft values, not user2's

**Expected Result**: ✅ Drafts are private to each user

---

### **Phase 2: Submission Sharing Testing**
**Objective**: Verify submissions are shared among all assigned Tier 2s

4. **Continue as `tier2.user1@disney.com`**
   - Edit the same incumbent plan
   - Complete all required fields
   - **Submit for Review** (change status to 'submitted')
   - Note submission confirmation

5. **Login as `tier2.user2@disney.com`**
   - Go to dashboard
   - Find the same incumbent
   - **Verify**: Status should show "🔵 Submitted" 
   - Click "📝 Create/Edit Plan"
   - **Verify**: Form should be pre-filled with user1's submitted values
   - **Verify**: Should see message like "Found submission from tier2.user1@disney.com (Tier 2)"

6. **Continue as `tier2.user2@disney.com`**
   - Modify some fields (add different successors, change details)
   - **Submit for Review** (this creates a new latest submission)

7. **Login as `tier2.user3@disney.com`**
   - Find the same incumbent
   - Click "📝 Create/Edit Plan"
   - **Verify**: Should see user2's latest submission (not user1's original)
   - **Verify**: Message should show user2 as the submitter

**Expected Result**: ✅ Latest submission is shared and visible to all assigned Tier 2s

---

### **Phase 3: Tier 1 Review & Approval**
**Objective**: Test Tier 1 review process

8. **Login as `tier1.user1@disney.com`**
   - Go to dashboard
   - **Verify**: Should see the incumbent with "🔵 Submitted" status
   - **Verify**: Should see collaboration indicator if multiple contributors
   - Click "📋 Review Submission"
   - **Verify**: Forms should be read-only
   - **Verify**: Should see approval controls (Approve / Send Back)

9. **Test Approval**
   - Click "✅ Approve Submission"
   - **Verify**: Success message appears
   - **Verify**: Dashboard now shows "🟢 Approved 🔄"

**Expected Result**: ✅ Tier 1 can review and approve collaborative submissions

---

### **Phase 4: Approved Plan Lockdown**
**Objective**: Verify approved plans are locked from Tier 2/3 editing

10. **Login as `tier2.user1@disney.com`**
    - Find the approved incumbent
    - **Verify**: Status shows "🟢 Approved"
    - Try to click "📝 Create/Edit Plan"
    - **Verify**: Should either be disabled or show read-only mode

11. **Login as `tier2.user2@disney.com`**
    - Same verification - approved plans should be locked

**Expected Result**: ✅ Tier 2 users cannot edit approved plans

---

### **Phase 5: Reopen Approved Plans**
**Objective**: Test Tier 1 ability to reopen approved plans

12. **Login as `tier1.user1@disney.com`**
    - Find the approved incumbent
    - **Verify**: Should see "🔄 Reopen for Editing" button
    - Click "🔄 Reopen for Editing"
    - **Verify**: Success message appears
    - **Verify**: Status changes to "🔴 Needs Edit"

**Expected Result**: ✅ Tier 1 can reopen approved plans

---

### **Phase 6: Collaborative Editing After Reopen**
**Objective**: Verify collaborative editing works on reopened plans

13. **Login as `tier2.user1@disney.com`**
    - Find the reopened incumbent
    - **Verify**: Status shows "🔴 Needs Edit"
    - Click "📝 Create/Edit Plan"
    - **Verify**: Form pre-filled with approved plan data
    - Make some changes and save

14. **Login as `tier2.user3@disney.com`**
    - Find the same incumbent
    - Click "📝 Create/Edit Plan"
    - **Verify**: Should see user1's latest changes
    - Add more changes and submit

**Expected Result**: ✅ Collaborative editing works on reopened plans

---

### **Phase 7: Send Back for Editing**
**Objective**: Test Tier 1 rejection workflow

15. **Login as `tier1.user1@disney.com`**
    - Review the resubmitted plan
    - Click "❌ Send Back for Editing"
    - **Verify**: Status changes to "🔴 Needs Edit"

16. **Login as `tier2.user2@disney.com`**
    - **Verify**: Can now edit the plan again
    - **Verify**: Form shows latest values

**Expected Result**: ✅ Send back workflow works properly

---

## 🎮 **Quick Test Script**

### **Rapid Testing Sequence (15 minutes)**

1. **`tier2.user1@disney.com`** → Create draft → Submit
2. **`tier2.user2@disney.com`** → See submission → Modify → Submit  
3. **`tier1.user1@disney.com`** → Review → Approve
4. **`tier2.user1@disney.com`** → Verify locked (cannot edit)
5. **`tier1.user1@disney.com`** → Reopen plan
6. **`tier2.user3@disney.com`** → Edit reopened → Submit
7. **`tier1.user1@disney.com`** → Send back for editing
8. **`tier2.user2@disney.com`** → Edit again

### **Key Things to Verify:**
- ✅ **Draft Privacy**: Only creator sees drafts
- ✅ **Submission Sharing**: All assigned Tier 2s see submissions
- ✅ **Latest Wins**: Most recent submission is shown
- ✅ **Read-Only Review**: Tier 1 cannot edit during review
- ✅ **Approval Lockdown**: Approved plans locked from Tier 2/3
- ✅ **Reopen Functionality**: Tier 1 can reopen approved plans
- ✅ **Collaboration Messages**: Clear indication of who did what

## 🔍 **What to Look For**

### **Success Indicators:**
- **Prepopulation Messages**: "Found submission from user@email.com (Tier 2)"
- **Status Changes**: Draft → Submitted → Approved → Needs Edit
- **Collaboration Icons**: 👥 indicators for multiple contributors
- **Button Availability**: Right buttons for right users at right times
- **Form States**: Read-only vs editable based on context

### **Potential Issues:**
- **Missing Prepopulation**: Forms not pre-filling with shared data
- **Wrong Visibility**: Users seeing drafts they shouldn't
- **Button Errors**: Wrong buttons showing for user tier
- **Status Confusion**: Incorrect status displays
- **Permission Errors**: Users editing when they shouldn't be able to

## 📊 **Test Data Tracking**

Keep track of:
- **Incumbent Employee ID**: Which incumbent you're testing with
- **User Actions**: Who did what when
- **Status Changes**: How status progresses through workflow
- **Collaboration**: How many users contributed
- **Messages**: What prepopulation messages appear

This testing sequence will validate all the collaborative workflow features and ensure the system handles real-world team dynamics properly! 🚀
