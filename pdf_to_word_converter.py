import streamlit as st
import io
from datetime import datetime
import os

# Try importing required libraries with proper error handling
try:
    import PyPDF2
    PDF_LIBRARY_AVAILABLE = True
    PDF_LIBRARY = "PyPDF2"
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY_AVAILABLE = True
        PDF_LIBRARY = "pdfplumber"
    except ImportError:
        PDF_LIBRARY_AVAILABLE = False
        PDF_LIBRARY = None

try:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    DOCX_LIBRARY_AVAILABLE = True
except ImportError:
    DOCX_LIBRARY_AVAILABLE = False

# --- Page Config ---
st.set_page_config(
    page_title="📄➡️📝 PDF to Word Converter",
    page_icon="📄",
    layout="wide"
)

st.title("📄➡️📝 PDF to Word Converter")
st.markdown("Convert your PDF files to editable Word documents with ease!")

# Check for required libraries
if not PDF_LIBRARY_AVAILABLE or not DOCX_LIBRARY_AVAILABLE:
    st.error("""
    **Missing Required Libraries!**
    
    Please add the following to your `requirements.txt` file:
    
    ```
    streamlit
    PyPDF2
    pdfplumber
    python-docx
    ```
    
    **Alternative requirements.txt:**
    ```
    streamlit
    pdfplumber==0.9.0
    python-docx==0.8.11
    ```
    """)
    st.stop()

# --- Helper Functions ---
def extract_text_pypdf2(pdf_file):
    """Extract text from PDF using PyPDF2"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = []
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text_content.append({
                        'page_number': page_num + 1,
                        'text': page_text
                    })
            except Exception as e:
                st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                continue
        
        return text_content, len(pdf_reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF with PyPDF2: {str(e)}")
        return None, 0

def extract_text_pdfplumber(pdf_file):
    """Extract text from PDF using pdfplumber"""
    try:
        import pdfplumber
        text_content = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content.append({
                            'page_number': page_num + 1,
                            'text': page_text
                        })
                except Exception as e:
                    st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            return text_content, len(pdf.pages)
    except Exception as e:
        st.error(f"Error reading PDF with pdfplumber: {str(e)}")
        return None, 0

def create_word_document(text_content, original_filename, formatting_options):
    """Create a Word document from extracted text"""
    try:
        doc = Document()
        
        # Add title
        title = doc.add_heading(f'Converted from: {original_filename}', 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Add conversion info
        info_para = doc.add_paragraph()
        info_run = info_para.add_run(f'Converted on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        info_run.italic = True
        info_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Add a page break
        doc.add_page_break()
        
        # Process each page
        for page_data in text_content:
            page_num = page_data['page_number']
            page_text = page_data['text']
            
            # Add page header if requested
            if formatting_options['include_page_numbers']:
                page_header = doc.add_heading(f'Page {page_num}', level=2)
                page_header.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            
            # Split text into paragraphs
            paragraphs = page_text.split('\n\n')
            
            for para_text in paragraphs:
                if para_text.strip():
                    # Clean up the text
                    cleaned_text = para_text.strip().replace('\n', ' ')
                    
                    # Add paragraph
                    para = doc.add_paragraph(cleaned_text)
                    
                    # Apply formatting
                    if formatting_options['font_size'] != 11:
                        for run in para.runs:
                            run.font.size = Pt(formatting_options['font_size'])
                    
                    # Add spacing
                    para.space_after = Pt(6)
            
            # Add page break between PDF pages if requested
            if formatting_options['page_breaks'] and page_num < len(text_content):
                doc.add_page_break()
        
        # Save to BytesIO
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)
        
        return doc_io
    except Exception as e:
        st.error(f"Error creating Word document: {str(e)}")
        return None

# --- Main App Interface ---
col1, col2 = st.columns([2, 1])

with col2:
    st.info(f"📚 Using **{PDF_LIBRARY}** for PDF processing")

# File upload
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a PDF file to convert to Word format"
)

if uploaded_file is not None:
    # Display file info
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.1f} KB",
        "File type": uploaded_file.type
    }
    
    with st.expander("📋 File Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filename", uploaded_file.name)
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("Type", "PDF")
    
    # Formatting options
    st.subheader("🎨 Formatting Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        include_page_numbers = st.checkbox("Include page numbers", value=True)
    
    with col2:
        page_breaks = st.checkbox("Page breaks between PDF pages", value=True)
    
    with col3:
        font_size = st.selectbox("Font size", [9, 10, 11, 12, 14, 16], index=2)
    
    with col4:
        extraction_method = st.selectbox(
            "Extraction method",
            ["Auto", "PyPDF2", "pdfplumber"] if PDF_LIBRARY_AVAILABLE else ["Auto"],
            help="Choose PDF text extraction method"
        )
    
    formatting_options = {
        'include_page_numbers': include_page_numbers,
        'page_breaks': page_breaks,
        'font_size': font_size
    }
    
    # Convert button
    if st.button("🔄 Convert PDF to Word", type="primary", use_container_width=True):
        with st.spinner("Converting PDF to Word... This may take a moment."):
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Extract text based on method selection
            text_content = None
            total_pages = 0
            
            if extraction_method == "PyPDF2" or (extraction_method == "Auto" and PDF_LIBRARY == "PyPDF2"):
                text_content, total_pages = extract_text_pypdf2(uploaded_file)
            elif extraction_method == "pdfplumber" or (extraction_method == "Auto" and PDF_LIBRARY == "pdfplumber"):
                uploaded_file.seek(0)  # Reset file pointer
                text_content, total_pages = extract_text_pdfplumber(uploaded_file)
            
            if text_content and len(text_content) > 0:
                # Show extraction results
                st.success(f"✅ Successfully extracted text from {len(text_content)} pages out of {total_pages} total pages")
                
                # Preview extracted text
                with st.expander("👁️ Preview Extracted Text", expanded=False):
                    preview_text = ""
                    char_count = 0
                    
                    for page_data in text_content[:3]:  # Show first 3 pages
                        page_preview = page_data['text'][:500]  # First 500 chars
                        preview_text += f"**Page {page_data['page_number']}:**\n{page_preview}...\n\n"
                        char_count += len(page_data['text'])
                    
                    st.text_area("Text Preview", preview_text, height=200, disabled=True)
                    st.info(f"Total characters extracted: {char_count:,}")
                
                # Create Word document
                original_filename = uploaded_file.name.replace('.pdf', '')
                word_doc = create_word_document(text_content, original_filename, formatting_options)
                
                if word_doc:
                    # Generate filename
                    output_filename = f"{original_filename}_converted.docx"
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Word Document",
                        data=word_doc,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.success("🎉 Conversion completed successfully!")
                    
                    # Show conversion summary
                    with st.expander("📊 Conversion Summary", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Pages Processed", len(text_content))
                        
                        with col2:
                            total_chars = sum(len(page['text']) for page in text_content)
                            st.metric("Characters Extracted", f"{total_chars:,}")
                        
                        with col3:
                            st.metric("Output Format", "DOCX")
            
            elif total_pages > 0:
                st.warning(f"⚠️ Could not extract readable text from the PDF. The document may contain:")
                st.write("• Scanned images (requires OCR)")
                st.write("• Protected/encrypted content")
                st.write("• Complex formatting that's difficult to parse")
                st.write("• Non-text elements only")
                
                st.info("💡 **Tip:** Try using OCR software for scanned PDFs, or ensure the PDF contains selectable text.")
            
            else:
                st.error("❌ Failed to process the PDF file. Please check if the file is valid and not corrupted.")

else:
    # Instructions when no file is uploaded
    st.info("👆 **Upload a PDF file to get started!**")
    
    st.subheader("📋 How it works:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **✅ What this app does:**
        • Extracts text from PDF files
        • Converts to editable Word documents
        • Preserves basic formatting
        • Adds page numbers and breaks
        • Customizable font settings
        """)
    
    with col2:
        st.markdown("""
        **⚠️ Limitations:**
        • Works best with text-based PDFs
        • Images are not converted
        • Complex layouts may be simplified
        • Scanned PDFs need OCR (not included)
        • Tables may lose formatting
        """)
    
    st.subheader("💡 Tips for best results:")
    st.markdown("""
    1. **Text-based PDFs work best** - Documents created from Word, Google Docs, etc.
    2. **Avoid scanned documents** - These need OCR processing
    3. **Simple layouts convert better** - Complex multi-column layouts may be reformatted
    4. **Check the preview** - Review extracted text before downloading
    5. **Try different extraction methods** - If one doesn't work well, try the other
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>
    🔧 **Technical Note:** This app extracts selectable text from PDFs. For scanned documents or images, 
    you'll need OCR (Optical Character Recognition) software.
    </small>
</div>
""", unsafe_allow_html=True)
