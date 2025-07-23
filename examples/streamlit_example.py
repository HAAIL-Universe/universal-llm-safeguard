import sys
print("PYTHONPATH:", sys.path)
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import streamlit as st
from core.orchestrator import run_all_filters

st.set_page_config(page_title="LLM Safeguard Tester", layout="centered")

st.title("🛡️ Universal LLM Safeguard Tester")
st.markdown("Test any input through the full safeguard layer in real-time. Useful for debugging or verifying system behavior.")

# --- Text input
input_text = st.text_area("🔤 Enter text to evaluate", height=200)

# --- Safeguard check button
if st.button("Run Safeguard Check"):
    if input_text.strip() == "":
        st.warning("⚠️ Please enter some text to check.")
    else:
        try:
            result = run_all_filters(input_text)

            allowed = result.get("status") == "allowed"
            flags = result.get("flags", [])
            reasons = result.get("reasons", [])

            st.markdown("---")
            st.subheader("🧾 Result")
            st.write(f"**Status:** {'✅ Allowed' if allowed else '❌ Blocked'}")
            st.write(f"**Flags Raised:** {', '.join(flags) if flags else 'None'}")
            st.write("**Reasons:**")
            for reason in reasons:
                st.markdown(f"- {reason}")

        except Exception as e:
            st.error(f"Error during safeguard check: {e}")

# Optional footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size: 0.85em;'>"
    "Universal LLM Safeguard – Streamlit Dev Adapter • "
    "<a href='https://github.com/HAAIL-Universe/universal-llm-safeguard' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
