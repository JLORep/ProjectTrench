import streamlit as st

st.set_page_config(page_title="Test Deploy", layout="wide")

st.title("🚀 TrenchCoat Pro - Test Deploy")
st.write("If you see this, basic deployment is working!")

# Test tabs
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    st.write("Tab 1 content")
    
with tab2:
    st.write("Tab 2 content")
    
with tab3:
    st.write("Tab 3 content")

st.success("✅ Basic Streamlit features working!")