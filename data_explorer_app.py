import streamlit as st
import pandas as pd

# ------------------------
# App Title
# ------------------------
st.title("📊 File Summarizer App")

# ------------------------
# Reset Button
# ------------------------
if st.button("🔄 Reset"):
    st.session_state.clear()
    st.cache_data.clear()
    st.rerun()

# ------------------------
# File Upload
# ------------------------
uploaded_file = st.file_uploader(
    "Upload a CSV, Excel, or TXT file", 
    type=["csv", "xlsx", "xls", "txt"],
    key="file_uploader"
)

# ------------------------
# File Processing
# ------------------------
if uploaded_file is not None:
    file_name = uploaded_file.name

    try:
        # Handle different file types
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        elif file_name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="\t")
        else:
            st.error("❌ Unsupported file type")
            st.stop()

        # Save in session state
        st.session_state["df"] = df

        # ------------------------
        # Show Summary
        # ------------------------
        st.success(f"✅ Successfully uploaded: {file_name}")

        st.subheader("📌 Preview of Data")
        st.dataframe(df.head())

        st.subheader("📌 Summary Statistics")
        st.write(df.describe(include="all"))

        st.subheader("📌 Columns Info")
        st.write(df.dtypes)

    except Exception as e:
        st.error(f"Error reading file: {e}")
