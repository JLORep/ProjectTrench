import streamlit as st
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(__file__))

# Import our ultra premium dashboard
from ultra_premium_dashboard import main

if __name__ == "__main__":
    main()