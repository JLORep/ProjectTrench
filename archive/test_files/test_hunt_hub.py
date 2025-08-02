"""Test Hunt Hub rendering issue"""

import streamlit as st

st.set_page_config(page_title="Test Hunt Hub", layout="wide")

st.title("Hunt Hub Test")

# Test 1: Simple HTML
st.subheader("Test 1: Simple HTML")
simple_html = """<div style="background: red; padding: 20px;">This should have red background</div>"""
st.markdown(simple_html, unsafe_allow_html=True)

# Test 2: Complex HTML like token card
st.subheader("Test 2: Token Card HTML")
card_html = """
<div style="background: #1a1a1a; padding: 20px; border-radius: 10px; margin: 10px 0;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <div>
            <h3 style="margin: 0; font-size: 24px; font-weight: 700;">
                PEPE2.0
                <span class="risk-indicator risk-low"></span>
            </h3>
            <p style="margin: 0; color: rgba(255,255,255,0.6); font-size: 14px;">
                Pepe 2.0 • EPjF...3n2 • <span class="launch-time">2 mins ago</span>
            </p>
        </div>
    </div>
</div>
"""
st.markdown(card_html, unsafe_allow_html=True)

# Test 3: Import actual Hunt Hub
st.subheader("Test 3: Actual Hunt Hub Import")
try:
    from memecoin_hunt_hub_ui import render_hunt_hub_dashboard
    st.success("Import successful!")
    render_hunt_hub_dashboard()
except ImportError as e:
    st.error(f"Import failed: {e}")
except Exception as e:
    st.error(f"Render failed: {e}")
    import traceback
    st.code(traceback.format_exc())