import streamlit as st
import io
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np
import cv2

# --- Page Config ---
st.set_page_config(
    page_title="🎨 Image Style Converter",
    page_icon="🎨",
    layout="wide"
)

# Check for required libraries
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# --- Helper Functions ---
def convert_to_line_drawing(image):
    """Convert image to line drawing/sketch"""
    try:
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Create line drawing effect
        # Method 1: Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Invert edges (black lines on white background)
        line_drawing = 255 - edges
        
        # Convert back to PIL
        line_img = Image.fromarray(line_drawing)
        
        return line_img
    except Exception as e:
        st.error(f"Error creating line drawing: {str(e)}")
        return None

def convert_to_watercolor(image):
    """Convert image to watercolor painting effect"""
    try:
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Resize for processing speed
        height, width = img_array.shape[:2]
        if width > 800:
            scale = 800 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_array = cv2.resize(img_array, (new_width, new_height))
        
        # Apply bilateral filter for smoothing while preserving edges
        smooth = cv2.bilateralFilter(img_array, 15, 80, 80)
        
        # Create watercolor effect
        # Apply multiple bilateral filters
        for _ in range(3):
            smooth = cv2.bilateralFilter(smooth, 9, 200, 200)
        
        # Enhance saturation for watercolor effect
        watercolor = Image.fromarray(smooth)
        enhancer = ImageEnhance.Color(watercolor)
        watercolor = enhancer.enhance(1.3)
        
        # Add slight blur for painting effect
        watercolor = watercolor.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return watercolor
    except Exception as e:
        st.error(f"Error creating watercolor effect: {str(e)}")
        return None

def convert_to_negative(image):
    """Convert image to negative/inverted colors"""
    try:
        # Simple inversion using PIL
        negative = ImageOps.invert(image.convert('RGB'))
        return negative
    except Exception as e:
        st.error(f"Error creating negative: {str(e)}")
        return None

def convert_to_black_white(image):
    """Convert image to black and white"""
    try:
        # Convert to grayscale
        bw_image = ImageOps.grayscale(image)
        
        # Enhance contrast for better B&W effect
        enhancer = ImageEnhance.Contrast(bw_image)
        bw_enhanced = enhancer.enhance(1.2)
        
        return bw_enhanced
    except Exception as e:
        st.error(f"Error creating black and white: {str(e)}")
        return None

def convert_to_pencil_sketch(image):
    """Convert image to pencil sketch"""
    try:
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Invert the grayscale image
        inverted = 255 - gray
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(inverted, (111, 111), 0)
        
        # Create sketch by blending
        sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
        
        return Image.fromarray(sketch)
    except Exception as e:
        st.error(f"Error creating pencil sketch: {str(e)}")
        return None

def convert_to_cartoon(image):
    """Convert image to cartoon effect"""
    try:
        img_array = np.array(image)
        
        # Resize for processing
        height, width = img_array.shape[:2]
        if width > 600:
            scale = 600 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_array = cv2.resize(img_array, (new_width, new_height))
        
        # Apply bilateral filter to reduce noise while preserving edges
        smooth = cv2.bilateralFilter(img_array, 15, 40, 40)
        
        # Create edge mask
        gray = cv2.cvtColor(smooth, cv2.COLOR_RGB2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        # Combine smooth image with edges
        cartoon = cv2.bitwise_and(smooth, edges)
        
        # Resize back to original size
        if width > 600:
            cartoon = cv2.resize(cartoon, (width, height))
        
        return Image.fromarray(cartoon)
    except Exception as e:
        st.error(f"Error creating cartoon effect: {str(e)}")
        return None

def image_to_bytes(image, format='PNG'):
    """Convert PIL image to bytes for download"""
    img_buffer = io.BytesIO()
    image.save(img_buffer, format=format)
    img_buffer.seek(0)
    return img_buffer.getvalue()

# --- Main App ---
st.title("🎨 Image Style Converter")
st.markdown("Transform your photos with artistic effects and filters!")

# Check for OpenCV
if not CV2_AVAILABLE:
    st.error("""
    **Missing Required Library!**
    
    Please add the following to your `requirements.txt` file:
    
    ```
    streamlit
    Pillow
    opencv-python-headless
    numpy
    ```
    """)
    st.stop()

# File upload
uploaded_file = st.file_uploader(
    "📤 Upload an image",
    type=["jpg", "jpeg", "png", "bmp", "tiff"],
    help="Supported formats: JPG, PNG, BMP, TIFF"
)

if uploaded_file is not None:
    # Load and display original image
    try:
        original_image = Image.open(uploaded_file)
        
        # Convert to RGB if necessary
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        
        st.success(f"✅ Image uploaded: {uploaded_file.name}")
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 Dimensions", f"{original_image.width} × {original_image.height}")
        with col2:
            st.metric("📁 Format", original_image.format or "Unknown")
        with col3:
            st.metric("💾 Size", f"{uploaded_file.size / 1024:.1f} KB")
        
        st.divider()
        
        # Style selection
        st.subheader("🎨 Choose Your Style")
        
        style_option = st.selectbox(
            "Select conversion style:",
            [
                "🖊️ Line Drawing",
                "🎨 Watercolor Painting", 
                "📸 Negative/Inverted",
                "⚫ Black & White",
                "✏️ Pencil Sketch",
                "🎭 Cartoon Effect"
            ]
        )
        
        # Advanced options for some styles
        if style_option in ["🎨 Watercolor Painting", "✏️ Pencil Sketch", "🎭 Cartoon Effect"]:
            with st.expander("⚙️ Advanced Options"):
                if style_option == "🎨 Watercolor Painting":
                    intensity = st.slider("Effect Intensity", 0.5, 2.0, 1.3, 0.1)
                elif style_option == "⚫ Black & White":
                    contrast = st.slider("Contrast", 0.5, 2.0, 1.2, 0.1)
        
        # Convert button
        if st.button("🔄 Convert Image", type="primary", use_container_width=True):
            with st.spinner(f"Converting to {style_option}... Please wait."):
                converted_image = None
                
                if style_option == "🖊️ Line Drawing":
                    converted_image = convert_to_line_drawing(original_image)
                elif style_option == "🎨 Watercolor Painting":
                    converted_image = convert_to_watercolor(original_image)
                elif style_option == "📸 Negative/Inverted":
                    converted_image = convert_to_negative(original_image)
                elif style_option == "⚫ Black & White":
                    converted_image = convert_to_black_white(original_image)
                elif style_option == "✏️ Pencil Sketch":
                    converted_image = convert_to_pencil_sketch(original_image)
                elif style_option == "🎭 Cartoon Effect":
                    converted_image = convert_to_cartoon(original_image)
                
                if converted_image:
                    st.success("✅ Conversion completed!")
                    
                    # Display before and after
                    st.subheader("🔄 Before & After Comparison")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📷 Original Image**")
                        st.image(original_image, use_column_width=True)
                    
                    with col2:
                        st.markdown(f"**{style_option} Result**")
                        st.image(converted_image, use_column_width=True)
                    
                    st.divider()
                    
                    # Download options
                    st.subheader("📥 Download Your Converted Image")
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col2:
                        # Format selection
                        download_format = st.selectbox(
                            "Choose download format:",
                            ["PNG", "JPEG", "BMP"],
                            index=0
                        )
                        
                        # Generate filename
                        base_name = uploaded_file.name.rsplit('.', 1)[0]
                        style_name = style_option.split(' ')[1].lower() if ' ' in style_option else style_option.lower()
                        style_name = style_name.replace('/', '_').replace('&', 'and')
                        download_filename = f"{base_name}_{style_name}.{download_format.lower()}"
                        
                        # Download button
                        img_bytes = image_to_bytes(converted_image, download_format)
                        
                        st.download_button(
                            label=f"📥 Download {style_option} Image",
                            data=img_bytes,
                            file_name=download_filename,
                            mime=f"image/{download_format.lower()}",
                            type="primary",
                            use_container_width=True
                        )
                        
                        st.info(f"💾 File will be saved as: `{download_filename}`")
                
                else:
                    st.error("❌ Conversion failed. Please try with a different image or style.")
    
    except Exception as e:
        st.error(f"❌ Error loading image: {str(e)}")
        st.info("💡 Make sure you're uploading a valid image file (JPG, PNG, etc.)")

else:
    # Instructions when no image is uploaded
    st.info("👆 **Upload an image to get started!**")
    
    st.subheader("🎨 Available Style Conversions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🖊️ Line Drawing**
        • Creates clean line art from your photo
        • Perfect for coloring books or minimalist art
        • Uses edge detection algorithms
        
        **🎨 Watercolor Painting**
        • Artistic watercolor painting effect
        • Smooths details while preserving main features
        • Enhanced colors with painting-like texture
        
        **✏️ Pencil Sketch**
        • Realistic pencil drawing effect
        • Grayscale sketch appearance
        • Highlights edges and textures
        """)
    
    with col2:
        st.markdown("""
        **📸 Negative/Inverted**
        • Classic photo negative effect
        • Inverts all colors
        • Creates interesting artistic results
        
        **⚫ Black & White**
        • Classic monochrome conversion
        • Enhanced contrast
        • Timeless photography look
        
        **🎭 Cartoon Effect**
        • Cartoon/animation style
        • Simplified colors and bold edges
        • Comic book appearance
        """)
    
    st.subheader("💡 Tips for Best Results")
    st.markdown("""
    1. **High-quality images work best** - Clear, well-lit photos give better results
    2. **Portrait photos** are great for line drawings and sketches
    3. **Landscape photos** work well for watercolor effects
    4. **Experiment with different styles** - Each image responds differently
    5. **Download in PNG** for best quality preservation
    """)
    
    # Sample image showcase
    st.subheader("🖼️ What to Expect")
    st.markdown("""
    **Line Drawing:** Perfect for creating coloring pages or minimalist wall art
    
    **Watercolor:** Great for artistic prints or social media posts
    
    **Pencil Sketch:** Ideal for portrait drawings or artistic studies
    
    **Negative:** Creates surreal, artistic effects
    
    **Black & White:** Classic photography for timeless appeal
    
    **Cartoon:** Fun for profile pictures or creative projects
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>
    🎨 **Image Style Converter** - Transform your photos into artistic masterpieces!<br>
    💡 **Tip:** Try different styles on the same image for various artistic effects.
    </small>
</div>
""", unsafe_allow_html=True)
