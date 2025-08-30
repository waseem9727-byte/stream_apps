import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------
# App Title
# ------------------------
st.set_page_config(page_title="EDA App", layout="wide")
st.title("📊 Automated EDA App")

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
# Process File
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

        # Store in session
        st.session_state["df"] = df

        st.success(f"✅ File uploaded: {file_name}")

        # ------------------------
        # Dataset Overview
        # ------------------------
        st.header("📌 Dataset Overview")
        st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
        st.dataframe(df.head())

        # ------------------------
        # Column Info
        # ------------------------
        st.header("📌 Columns Info")
        col_info = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Missing Values": df.isnull().sum().values,
            "Unique Values": df.nunique().values
        })
        st.dataframe(col_info)

        # ------------------------
        # Summary Stats
        # ------------------------
        st.header("📌 Summary Statistics")
        st.write(df.describe(include="all").T)

        # ------------------------
        # Correlation Heatmap
        # ------------------------
        st.header("📌 Correlation Heatmap (Numerical Features)")
        num_df = df.select_dtypes(include=["int64", "float64"])
        if not num_df.empty:
            corr = num_df.corr()

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            st.pyplot(fig)
        else:
            st.info("No numerical columns available for correlation analysis.")

        # ------------------------
        # Distribution Plots
        # ------------------------
        st.header("📌 Distributions of Numerical Columns")
        for col in num_df.columns:
            fig, ax = plt.subplots()
            sns.histplot(df[col].dropna(), kde=True, ax=ax)
            ax.set_title(f"Distribution of {col}")
            st.pyplot(fig)

        # ------------------------
        # Categorical Value Counts
        # ------------------------
        st.header("📌 Categorical Columns Value Counts")
        cat_df = df.select_dtypes(include=["object", "category"])
        if not cat_df.empty:
            for col in cat_df.columns:
                st.subheader(f"🔹 {col}")
                st.bar_chart(df[col].value_counts().head(20))
        else:
            st.info("No categorical columns available.")

    except Exception as e:
        st.error(f"Error reading file: {e}")
