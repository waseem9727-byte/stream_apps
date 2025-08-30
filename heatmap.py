import streamlit as st
import pandas as pd

# Handle imports with proper error messages
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    VISUALIZATION_AVAILABLE = False
    missing_packages = []
    if 'matplotlib' in str(e):
        missing_packages.append('matplotlib')
    if 'seaborn' in str(e):
        missing_packages.append('seaborn')

# --- Page Config ---
st.set_page_config(page_title="Correlation Heatmap Generator", layout="wide")

st.title("📊 Correlation Heatmap Generator")

# Show error if visualization packages are missing
if not VISUALIZATION_AVAILABLE:
    st.error(f"""
    Missing required packages for visualization. Please add the following to your `requirements.txt` file:
    - matplotlib
    - seaborn
    
    Your `requirements.txt` should contain:
    ```
    streamlit
    pandas
    matplotlib
    seaborn
    ```
    """)
    st.stop()

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Load data
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error loading CSV file: {str(e)}")
        st.stop()

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

        # Heatmap customization options
        st.sidebar.subheader("🎨 Visualization Options")
        
        # Color palette options
        color_palette = st.sidebar.selectbox(
            "Color Palette",
            ["coolwarm", "viridis", "RdBu", "RdYlBu", "seismic"],
            index=0
        )
        
        # Figure size
        fig_width = st.sidebar.slider("Figure Width", 6, 16, 10)
        fig_height = st.sidebar.slider("Figure Height", 4, 12, 6)
        
        # Annotation options
        show_annotations = st.sidebar.checkbox("Show Values", value=True)
        decimal_places = st.sidebar.slider("Decimal Places", 0, 4, 2)

        if selected_cols:
            # Compute correlation
            try:
                corr_matrix = df[selected_cols].corr(method=corr_method)
            except Exception as e:
                st.error(f"Error calculating correlation: {str(e)}")
                st.stop()

            st.subheader(f"Correlation Heatmap ({corr_method.capitalize()} method)")

            # Plot heatmap
            try:
                fig, ax = plt.subplots(figsize=(fig_width, fig_height))
                
                # Create heatmap
                sns.heatmap(
                    corr_matrix,
                    annot=show_annotations,
                    cmap=color_palette,
                    fmt=f".{decimal_places}f",
                    linewidths=0.5,
                    ax=ax,
                    center=0,  # Center colormap at 0
                    square=True,  # Make cells square-shaped
                    cbar_kws={"shrink": 0.8}  # Adjust colorbar size
                )
                
                # Improve layout
                plt.title(f'Correlation Matrix ({corr_method.capitalize()})', 
                         fontsize=14, fontweight='bold', pad=20)
                plt.tight_layout()
                
                # Display plot
                st.pyplot(fig)
                
                # Clear the figure to prevent memory issues
                plt.close(fig)
                
            except Exception as e:
                st.error(f"Error creating visualization: {str(e)}")

            # Show raw correlation matrix
            with st.expander("📋 Raw Correlation Matrix"):
                st.dataframe(corr_matrix.style.format(f"{{:.{decimal_places}f}}"))
                
            # Download correlation matrix as CSV
            csv = corr_matrix.to_csv()
            st.download_button(
                label="📥 Download Correlation Matrix as CSV",
                data=csv,
                file_name=f"correlation_matrix_{corr_method}.csv",
                mime="text/csv"
            )
            
            # Summary statistics
            with st.expander("📈 Correlation Summary"):
                st.write("**Highest Correlations:**")
                
                # Get upper triangle of correlation matrix (avoid duplicates)
                mask = pd.DataFrame(True, index=corr_matrix.index, columns=corr_matrix.columns)
                mask = mask.where(~(mask & pd.DataFrame(False, index=corr_matrix.index, columns=corr_matrix.columns).T))
                
                # Create a series of correlations
                corr_series = corr_matrix.where(mask).stack().sort_values(ascending=False)
                
                # Remove self-correlations (diagonal = 1.0)
                corr_series = corr_series[corr_series < 0.99]
                
                # Show top 10 correlations
                if len(corr_series) > 0:
                    top_correlations = corr_series.head(10)
                    for (var1, var2), corr_val in top_correlations.items():
                        st.write(f"• **{var1}** ↔ **{var2}**: {corr_val:.{decimal_places}f}")
                else:
                    st.write("No correlations to display.")
                    
        else:
            st.info("Please select at least one column from the sidebar.")
else:
    st.info("👆 Upload a CSV file to begin.")
    
    # Show example of expected data format
    st.subheader("📝 Expected Data Format")
    st.write("Your CSV should contain numeric columns. Here's an example:")
    
    example_data = pd.DataFrame({
        'Temperature': [23, 25, 22, 28, 30],
        'Humidity': [45, 50, 40, 60, 65],
        'Pressure': [1013, 1015, 1010, 1020, 1025],
        'Sales': [100, 120, 90, 150, 180]
    })
    
    st.dataframe(example_data)
