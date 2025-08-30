import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="Correlation Heatmap Generator", layout="wide")

st.title("📊 Correlation Heatmap Generator")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Load data
    df = pd.read_csv(uploaded_file)

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    # Select numeric columns only
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if not numeric_cols:
        st.warning("No numeric columns found in the dataset to calculate correlations.")
    else:
        st.sidebar.header("⚙️ Options")

        # Allow user to select subset of columns
        selected_cols = st.sidebar.multiselect(
            "Select columns for correlation",
            numeric_cols,
            default=numeric_cols
        )

        # Correlation method
        corr_method = st.sidebar.radio(
            "Correlation Method",
            ["pearson", "kendall", "spearman"],
            index=0
        )

        if selected_cols:
            # Compute correlation
            corr_matrix = df[selected_cols].corr(method=corr_method)

            st.subheader(f"Correlation Heatmap ({corr_method.capitalize()} method)")

            # Plot heatmap
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(
                corr_matrix,
                annot=True,
                cmap="coolwarm",
                fmt=".2f",
                linewidths=0.5,
                ax=ax
            )
            st.pyplot(fig)

            # Show raw correlation matrix
            with st.expander("See Raw Correlation Matrix"):
                st.dataframe(corr_matrix)
        else:
            st.info("Please select at least one column from the sidebar.")
else:
    st.info("👆 Upload a CSV file to begin.")
