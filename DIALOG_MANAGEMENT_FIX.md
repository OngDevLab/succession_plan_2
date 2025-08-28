# Dialog Management Fix

## The Problem
When you selected an incumbent and then selected another person from the list, it was incorrectly opening a successor form instead of clearing the current incumbent and showing the new person's options.

## Root Cause
The dialog management logic was checking:
1. `st.session_state.selected_person` (new person selected)
2. `st.session_state.app_data['incumbent']` (old incumbent still loaded)

This combination triggered the successor dialog logic instead of recognizing that a new incumbent was being selected.

## The Fix
Added logic to detect when a different person is being selected as incumbent:

```python
# Check if a new incumbent is being selected (different from current incumbent)
if (st.session_state.selected_person and 
    st.session_state.app_data['incumbent'] and 
    st.session_state.selected_person['EMPLOYEE_ID'] != st.session_state.app_data['incumbent']['metadata']['EMPLOYEE_ID']):
    # Clear existing incumbent data when selecting a different person
    st.session_state.app_data['incumbent'] = None
    st.session_state.app_data['successors'] = []
    st.session_state.editing_incumbent = False
    st.session_state.editing_successor_index = None
```

## What This Does

### ✅ **Before the Fix:**
1. Select Person A → Shows incumbent options ✅
2. Select Person B → Opens successor form ❌ (Wrong!)

### ✅ **After the Fix:**
1. Select Person A → Shows incumbent options ✅
2. Select Person B → Clears Person A, shows Person B options ✅ (Correct!)

## User Experience Now

### **Scenario 1: Fresh Selection**
- Select any person → Shows Create/Edit Plan, View Existing Plan options

### **Scenario 2: Switching Between People**
- Select Person A → Shows Person A options
- Select Person B → **Automatically clears Person A**, shows Person B options
- No unwanted successor dialogs

### **Scenario 3: Adding Successors (Still Works)**
- Select Person A → Create/Edit Plan
- Complete incumbent form
- Select Person B → Now correctly opens successor form (because Person A is the established incumbent)

## Technical Details

### **Detection Logic:**
- Compares `selected_person['EMPLOYEE_ID']` with `incumbent['metadata']['EMPLOYEE_ID']`
- Only triggers when they're different (new person selected)

### **Cleanup Actions:**
- Clears incumbent data
- Clears successors array
- Resets editing states
- Allows fresh start with new person

### **Preserved Functionality:**
- Normal successor addition still works
- Edit modes still work
- All existing features remain intact

## Benefits

1. **Intuitive Behavior**: Selecting a new person behaves as expected
2. **Clean State Management**: No leftover data from previous selections
3. **Prevents Confusion**: No more unexpected successor dialogs
4. **Maintains Functionality**: All existing features work as before

The dialog management now correctly handles person switching while preserving all existing functionality! 🚀
