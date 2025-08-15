"""
Configuration loader for YAML config file
"""

import yaml
import os

def load_config():
    """Load configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return default config if file can't be loaded
        return get_default_config()

def get_default_config():
    """Fallback default configuration"""
    return {
        'skills': [
            "Thinks Strategically", "Plans and Prioritizes", "Ensures Accountability",
            "Collaborates", "Instills Trust", "Drives Engagement", "Values Differences",
            "Business Insight", "Courage", "Change Adaptability"
        ],
        'ple_options': [
            "-- Select an Option --",
            "Inspire Individual and Business Success",
            "Define Strategies, Priorities, and Expectations",
            "Provide Continuous Coaching and Feedback",
            "Develop Self and Others and Support Career Aspirations",
            "Demonstrate Care and Compassion",
            "Create an Environment Where Disney Values are Experienced"
        ],
        'database': {
            'employee_db': 'succession_db.sqlite',
            'succession_plans_db': 'succession_plans.sqlite'
        },
        'ui': {
            'page_title': 'Succession Planning Tool',
            'layout': 'wide',
            'logo_path': 'people_insights_logo.png',
            'logo_width': 100
        }
    }

# Load config once when module is imported
CONFIG = load_config()

# Export commonly used values for easy access
SKILLS_LIST = CONFIG['skills']
PLE_LIST = CONFIG['ple_options']
FORM_OPTIONS = CONFIG.get('form_options', {})
