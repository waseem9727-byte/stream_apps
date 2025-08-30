import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Data Explorer", layout="wide")

st.title("📊 Data Explorer App")
st.write("Upload your dataset (CSV/Excel) to explore it interactively.")

# ---- Reset Button ----
if st.button("🔄 Reset App"):
    st.session_state.clear()
    st.rerun()

# ---- File Upload ----
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"], key="file_uploader")

if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    st.success("✅ File uploaded successfully!")

    # ---- Data Overview ----
    st.subheader("🔎 Dataset Preview")
    st.dataframe(df.head())

    st.subheader("📐 Dataset Summary")
    st.write(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")
    st.write("**Column Types:**")
    st.write(df.dtypes)

    # ---- Missing Values ----
    st.subheader("🚨 Missing Values")
    missing = df.isnull().sum()
    st.write(missing[missing > 0])

    # ---- Numeric Summary ----
    st.subheader("📈 Numeric Summary Stats")
    st.write(df.describe())

    # ---- Column Selection ----
    st.subheader("📊 Column Explorer")
    column = st.selectbox("Select a column to explore", df.columns)

    if pd.api.types.is_numeric_dtype(df[column]):
        st.write(f"**Distribution of {column}**")
        fig, ax = plt.subplots()
        sns.histplot(df[column].dropna(), kde=True, ax=ax)
        st.pyplot(fig)
    else:
        st.write(f"**Value counts of {column}**")
        st.bar_chart(df[column].value_counts().head(20))

    # ---- Correlation Heatmap ----
    st.subheader("🔗 Correlation Heatmap (Numerical Columns)")
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    if not numeric_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.info("No numerical columns available for correlation.")

else:
    st.info("👆 Upload a dataset to get started.")
