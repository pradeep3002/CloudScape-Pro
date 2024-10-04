import streamlit as st
import cv2
from PIL import Image, ImageEnhance
import numpy as np
import os
from io import BytesIO
import time
from datetime import datetime

# Custom theme and styling
def set_custom_theme():
    st.markdown("""
        <style>
        .main {
            background-color: #f5f7f9;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            border-radius: 5px;
            border: none;
        }
        .stProgress .st-bo {
            background-color: #4CAF50;
        }
        </style>
    """, unsafe_allow_html=True)

# Enhanced image processing functions
def apply_enhancements(our_image, enhance_type):
    img = np.array(our_image.convert("RGB"))
    
    if "Gray-Scale" in enhance_type:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # Convert back to RGB for consistency
        
    if "Contrast" in enhance_type:
        rate = st.sidebar.slider("Contrast", 0.1, 6.0, 1.0)
        enhancer = ImageEnhance.Contrast(Image.fromarray(img))
        img = np.array(enhancer.enhance(rate))
        
    if "Brightness" in enhance_type:
        rate = st.sidebar.slider("Brightness", 0.1, 10.0, 1.0)
        enhancer = ImageEnhance.Brightness(Image.fromarray(img))
        img = np.array(enhancer.enhance(rate))
        
    if "Sharpness" in enhance_type:
        rate = st.sidebar.slider("Sharpness", 0.1, 10.0, 1.0)
        enhancer = ImageEnhance.Sharpness(Image.fromarray(img))
        img = np.array(enhancer.enhance(rate))
        
    if "Shadow & Blur" in enhance_type:
        alpha = st.sidebar.slider("Shadow intensity", 1.0, 7.0, 1.0)
        kernel_size = st.sidebar.slider("Blur", 3, 21, 3, step=2)
        kernel = np.zeros((kernel_size, kernel_size), np.float32)
        kernel.fill(1.0 / (kernel_size * kernel_size))
        shadow = cv2.filter2D(img, -1, kernel)
        img = cv2.addWeighted(img, 1 - alpha, shadow, alpha, 0)
        
    if "Rotate" in enhance_type:
        angle = st.sidebar.slider("Rotation angle", 0, 360, 0)
        rows, cols = img.shape[:2]
        M = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
        img = cv2.warpAffine(img, M, (cols, rows))
        
    if "Vintage Effect" in enhance_type:
        # Add a sepia tone effect
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        img = cv2.transform(img, kernel)
        
    if "Vignette" in enhance_type:
        rows, cols = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols/4)
        kernel_y = cv2.getGaussianKernel(rows, rows/4)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        img = img * mask[:, :, np.newaxis]
        
    return img.astype(np.uint8)

def cartoonize_image(our_image):
    img = np.array(our_image.convert('RGB'))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def main():
    set_custom_theme()
    
    st.title('🎨 CloudScape Pro')
    st.markdown("### Professional Image Enhancement Studio")
    
    activities = ["Image Studio", "Batch Processing", "About"]
    choice = st.sidebar.selectbox("Select Workspace", activities)
    
    if choice == "Image Studio":
        st.sidebar.markdown("### Enhancement Tools")
        
        image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "heic"])
        
        if image_file is not None:
            our_image = Image.open(image_file)
            
            # Display original image with some stats
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Original Image")
                st.image(our_image)
            with col2:
                st.markdown("#### Image Information")
                st.write(f"Size: {our_image.size}")
                st.write(f"Mode: {our_image.mode}")
                st.write(f"Format: {image_file.type}")
            
            enhance_type = st.sidebar.multiselect(
                "Select Enhancement Features",
                ["Gray-Scale", "Contrast", "Brightness", "Sharpness", 
                 "Rotate", "Shadow & Blur", "Vintage Effect", "Vignette"]
            )
            
            if enhance_type:
                with st.spinner('Applying enhancements...'):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    enhanced_img = apply_enhancements(our_image, enhance_type)
                    st.markdown("#### Enhanced Result")
                    st.image(enhanced_img)
                    
                    # Add download button for enhanced image
                    enhanced_pil = Image.fromarray(enhanced_img)
                    buf = BytesIO()
                    enhanced_pil.save(buf, format="PNG")
                    st.download_button(
                        label="Download Enhanced Image",
                        data=buf.getvalue(),
                        file_name=f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png"
                    )
            
            # Special effects section
            st.sidebar.markdown("### Special Effects")
            if st.sidebar.button("Apply Cartoon Effect"):
                with st.spinner('Applying cartoon effect...'):
                    cartoon = cartoonize_image(our_image)
                    st.image(cartoon, caption="Cartoonized Image")
    
    elif choice == "Batch Processing":
        st.markdown("### Batch Image Processing")
        st.info("Upload multiple images to process them with the same settings")
        # Add batch processing functionality here
        
    elif choice == "About":
        st.markdown("### About CloudScape Pro")
        st.write("""
        CloudScape Pro is a professional-grade image processing application built with 
        state-of-the-art computer vision and image processing techniques. Our tool 
        provides photographers and digital artists with powerful yet intuitive controls 
        for image enhancement and manipulation.
        
        #### Key Features:
        - Advanced image enhancement algorithms
        - Real-time preview of adjustments
        - Professional-grade filters and effects
        - Batch processing capabilities
        - Easy-to-use interface
        
        #### Technical Details:
        - Built with Python, OpenCV, and Streamlit
        - Utilizes advanced computer vision algorithms
        - Optimized for performance and quality
        
        #### Development Team:
        - Midhilesh
        - Revanth
        - Pradeep
        - Deepak
        """)

if __name__ == "__main__":
    main()