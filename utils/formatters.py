"""
Formatting utilities for display purposes
"""

def format_management_level(management_level):
    """Convert management level to L1, L2, L3 format"""
    if not management_level:
        return ""
    
    # Handle different possible formats
    level_str = str(management_level).strip().upper()
    
    # If already in L1, L2, L3 format, return as is
    if level_str.startswith('L') and len(level_str) == 2:
        return level_str
    
    # Convert numeric values
    if level_str.isdigit():
        return f"L{level_str}"
    
    # Handle text descriptions
    level_mapping = {
        'LEVEL 1': 'L1',
        'LEVEL 2': 'L2', 
        'LEVEL 3': 'L3',
        'LEVEL 4': 'L4',
        'LEVEL 5': 'L5',
        'LEVEL 6': 'L6',
        'LEVEL 7': 'L7',
        'LEVEL 8': 'L8',
        'LEVEL 9': 'L9',
        'LEVEL 10': 'L10',
        'LEVEL1': 'L1',
        'LEVEL2': 'L2',
        'LEVEL3': 'L3',
        'LEVEL4': 'L4',
        'LEVEL5': 'L5',
        'LEVEL6': 'L6',
        'LEVEL7': 'L7',
        'LEVEL8': 'L8',
        'LEVEL9': 'L9',
        'LEVEL10': 'L10',
        '1': 'L1',
        '2': 'L2',
        '3': 'L3',
        '4': 'L4',
        '5': 'L5',
        '6': 'L6',
        '7': 'L7',
        '8': 'L8',
        '9': 'L9',
        '10': 'L10'
    }
    
    return level_mapping.get(level_str, level_str)

def format_job_level(job_level):
    """Format job level for display"""
    if not job_level:
        return ""
    return str(job_level).strip()

def format_employee_name(first_name, last_name):
    """Format employee name for display"""
    first = str(first_name).strip() if first_name else ""
    last = str(last_name).strip() if last_name else ""
    
    if first and last:
        return f"{first} {last}"
    elif last:
        return last
    elif first:
        return first
    else:
        return "Unknown"
