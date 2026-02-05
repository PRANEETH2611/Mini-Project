import json
import os
import streamlit as st

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_config():
    """Load configuration from JSON file"""
    if not os.path.exists(CONFIG_PATH):
        # Default config if file missing
        return {
            "cpu_threshold": 80,
            "memory_threshold": 8,
            "latency_threshold": 1000
        }
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {
            "cpu_threshold": 80,
            "memory_threshold": 8,
            "latency_threshold": 1000
        }

def save_config(config):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
