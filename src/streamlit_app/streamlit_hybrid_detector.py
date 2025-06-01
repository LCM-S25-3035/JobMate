# streamlit_hybrid_detector.py
import streamlit as st
import json
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from streamlit_app.ghost_core import hybrid_detect_ghost_jobs

st.set_page_config(page_title="Hybrid Ghost Job Detector")
st.title("Hybrid Ghost Job Detector")

st.markdown("""
Upload a job list JSON file to detect ghost jobs using both rule-based and ML detection.
""")

uploaded_file = st.file_uploader("📂 Upload job listings (JSON)", type=["json"])

if uploaded_file:
    try:
        jobs_data = json.load(uploaded_file)
        st.success(f"✅ Loaded {len(jobs_data)} job entries.")

        if st.button("🚨 Run Ghost Detection"):
            results = hybrid_detect_ghost_jobs(jobs_data)
            df = pd.DataFrame(results)

            def highlight_risk(val):
                if val >= 80:
                    return 'background-color: #b30000; color: white'
                elif val >= 60:
                    return 'background-color: #ff1a1a; color: white'
                elif val >= 40:
                    return 'background-color: #ffd633; color: black'
                return ''

            styled_df = df.style.applymap(highlight_risk, subset=['ghost_risk_%'])\
                                .format({'rule_score': '{:.2f}', 'ml_prob': '{:.2f}'})

            st.subheader("🧾 Detection Results")
            st.dataframe(styled_df, use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Download CSV", data=csv, file_name="ghost_detection_results.csv")

    except Exception as e:
        st.error(f"❌ Error: {e}")
