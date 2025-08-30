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

# --- Helper Functions ---
def convert_to_line_drawing(image):
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return Image.fromarray(255 - edges)

def convert_to_watercolor(image):
    img_array = np.array(image)
    smooth = cv2.bilateralFilter(img_array, 15, 80, 80)
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 200, 200)
    watercolor = Image.fromarray(smooth)
    watercolor = ImageEnhance.Color(watercolor).enhance(1.3)
    return watercolor.filter(ImageFilter.GaussianBlur(0.5))

def convert_to_negative(image):
    return ImageOps.invert(image.convert('RGB'))

def convert_to_black_white(image):
    bw = ImageOps.grayscale(image)
    return ImageEnhance.Contrast(bw).enhance(1.2)

def convert_to_pencil_sketch(image):
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (111, 111), 0)
    sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
    return Image.fromarray(sketch)

def convert_to_cartoon(image):
    img_array = np.array(image)
    smooth = cv2.bilateralFilter(img_array, 15, 40, 40)
    gray = cv2.cvtColor(smooth, cv2.COLOR_RGB2GRAY)
    edges = cv2.adaptiveThreshold(gray, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    cartoon = cv2.bitwise_and(smooth, edges)
    return Image.fromarray(cartoon)

# --- New Effects ---
def convert_to_oil_painting(image):
    img_array = np.array(image)
    try:
        oil = cv2.xphoto.oilPainting(img_array, 7, 1)
    except Exception:
        oil = cv2.medianBlur(img_array, 15)  # fallback
    return Image.fromarray(oil)

def convert_to_sepia(image):
    img_array = np.array(image)
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img_array, kernel)
    return Image.fromarray(np.clip(sepia, 0, 255).astype(np.uint8))

def convert_to_pop_art(image):
    return ImageEnhance.Color(image).enhance(2.5)

def convert_to_hdr(image):
    img_array = np.array(image)
    hdr = cv2.detailEnhance(img_array, sigma_s=12, sigma_r=0.15)
    return Image.fromarray(hdr)

def convert_to_pixel_art(image):
    small = image.resize((image.width // 16, image.height // 16), Image.NEAREST)
    return small.resize(image.size, Image.NEAREST)

def convert_to_vignette(image):
    img_array = np.array(image)
    rows, cols = img_array.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, 200)
    kernel_y = cv2.getGaussianKernel(rows, 200)
    mask = kernel_y * kernel_x.T
    mask = 255 * mask / np.linalg.norm(mask)
    vignette = np.copy(img_array)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * mask
    return Image.fromarray(vignette.astype(np.uint8))

def convert_to_glitch(image):
    img_array = np.array(image)
    b, g, r = cv2.split(img_array)
    r = np.roll(r, 5, axis=1)
    g = np.roll(g, -5, axis=0)
    glitch = cv2.merge([b, g, r])
    return Image.fromarray(glitch)

def convert_to_posterize(image):
    return ImageOps.posterize(image, bits=3)

def convert_to_emboss(image):
    return image.filter(ImageFilter.EMBOSS)

# --- Mapping of categories to styles ---
STYLE_CATEGORIES = {
    "✏️ Sketch & Drawing": {
        "🖊️ Line Drawing": convert_to_line_drawing,
        "✏️ Pencil Sketch": convert_to_pencil_sketch,
        "⚫ Black & White": convert_to_black_white,
    },
    "🎨 Artistic & Painting": {
        "🎨 Watercolor": convert_to_watercolor,
        "🖌️ Oil Painting": convert_to_oil_painting,
        "🌈 Pop Art": convert_to_pop_art,
        "🔆 HDR": convert_to_hdr,
        "📰 Posterization": convert_to_posterize,
    },
    "📸 Photography Effects": {
        "📜 Sepia Vintage": convert_to_sepia,
        "📸 Negative": convert_to_negative,
        "🌓 Vignette": convert_to_vignette,
        "🎭 Cartoon": convert_to_cartoon,
    },
    "🤖 Fun & Experimental": {
        "🟦 Pixel Art": convert_to_pixel_art,
        "💥 Glitch": convert_to_glitch,
        "🔩 Emboss": convert_to_emboss,
    }
}

# --- Utility ---
def image_to_bytes(image, format='PNG'):
    buf = io.BytesIO()
    image.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()

# --- Main App ---
st.title("🎨 Image Style Converter")
st.markdown("Transform your photos with artistic effects and filters!")

uploaded_file = st.file_uploader("📤 Upload an image",
                                 type=["jpg","jpeg","png","bmp","tiff"])

if uploaded_file:
    original_image = Image.open(uploaded_file).convert("RGB")
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # Select Category
    st.subheader("🎭 Choose Style Category")
    category = st.selectbox("Select a category:", list(STYLE_CATEGORIES.keys()))

    # Show previews of styles in that category
    st.subheader("👀 Preview Styles")
    cols = st.columns(3)
    previews = list(STYLE_CATEGORIES[category].items())
    for i, (style_name, func) in enumerate(previews):
        with cols[i % 3]:
            try:
                thumb = original_image.copy().resize((200, 200))
                thumb_result = func(thumb)
                st.image(thumb_result, caption=style_name, use_container_width=True)
            except Exception:
                st.write(f"{style_name} (preview failed)")

    # Select specific style
    st.subheader("🎨 Select Specific Style")
    style_option = st.selectbox("Available styles:", list(STYLE_CATEGORIES[category].keys()))

    if st.button("🔄 Convert Image", type="primary", use_container_width=True):
        converted_image = STYLE_CATEGORIES[category][style_option](original_image)

        col1, col2 = st.columns(2)
        with col1: st.image(original_image, caption="Original", use_container_width=True)
        with col2: st.image(converted_image, caption=style_option, use_container_width=True)

        # Download
        fmt = st.selectbox("Download format:", ["PNG", "JPEG", "BMP"])
        base_name = uploaded_file.name.rsplit(".", 1)[0]
        file_name = f"{base_name}_{style_option.replace(' ', '_')}.{fmt.lower()}"
        st.download_button("📥 Download Image",
                           data=image_to_bytes(converted_image, fmt),
                           file_name=file_name,
                           mime=f"image/{fmt.lower()}")
