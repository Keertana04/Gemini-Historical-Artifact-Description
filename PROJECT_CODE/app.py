from dotenv import load_dotenv
import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables
load_dotenv()

# Client gets API key from GEMINI_API_KEY or GOOGLE_API_KEY env variable
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

# Prompt templates based on user selection
PROMPT_OPTIONS = {
    "Describe": """You are a historian. Provide a comprehensive description of the historical artifact in the image. Include its physical appearance, materials, craftsmanship, and overall significance.""",
    "Identify & Classify": """You are an expert art historian. Identify and classify the artifact in the image. Specify its type, estimated era or period, materials used, cultural origin, and any distinguishing features that help with identification.""",
    "Historical Context": """You are a historian. Analyze the historical context of this artifact. Explain the time period it comes from, the historical events or culture it relates to, and how it would have been used or valued in its time.""",
    "Origin & Significance": """You are a cultural historian. Describe the origin of this artifact—where it likely came from, the culture that produced it—and explain its historical and cultural significance. Why does it matter today?""",
    "Cultural Analysis": """You are an expert in cultural heritage. Analyze the artifact's cultural meaning, symbolism, religious or social significance, and how it reflects the values or beliefs of the people who created it.""",
    "Conservation & Condition": """You are a museum conservator. Assess the artifact's current condition, visible signs of wear or aging, potential materials and techniques used in its creation, and any conservation considerations or restoration that might be relevant.""",
}


def get_gemini_response(input_text, image_bytes, mime_type, prompt):
    full_prompt = f"{prompt}\n\nAdditional context from user: {input_text}" if input_text.strip() else prompt
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[full_prompt, image_part],
    )
    return response.text


# Page config
st.set_page_config(
    page_title="Gemini Historical Artifact Description",
    page_icon="🏺",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Fixed dimensions for image display (medium size)
IMAGE_DISPLAY_WIDTH = 500

# Custom styling for a cleaner look

st.markdown("""
    <style>
    .main-header {
        font-size: 40px !important;
        font-weight: 700;
        color: #ffffff;
        margin: 20px 0;
        text-align: center;
    }
    </style>
    <div class="main-header">🏺 Historical Artifact Description App</div>
""", unsafe_allow_html=True)


# Single-column layout
st.subheader("📷 Upload Image")
uploaded_file = st.file_uploader(
    "Drag and drop or browse",
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, JPEG, PNG",
    label_visibility="collapsed",
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded artifact image", width=IMAGE_DISPLAY_WIDTH)
else:
    st.info("Upload an image of a historical artifact to get started.")

st.subheader("⚙️ Analysis Options")
prompt_choice = st.selectbox(
    "What would you like to know?",
    options=list(PROMPT_OPTIONS.keys()),
    index=0,
    help="Select the type of analysis you want for the uploaded artifact.",
)

input_text = st.text_area(
    "Additional context (optional)",
    placeholder="E.g., 'Found in a temple in South India' or 'Family heirloom from the 1800s'",
    height=80,
    help="Add any extra details that might help the analysis.",
)

submit = st.button("🔄 Generate Description")

st.divider()

# Generate and display result
if submit:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Add GEMINI_API_KEY or GOOGLE_API_KEY to your .env file.")
    elif uploaded_file is None:
        st.error("Please upload an image first.")
    else:
        with st.spinner("Analyzing artifact..."):
            try:
                image_bytes = uploaded_file.getvalue()
                selected_prompt = PROMPT_OPTIONS[prompt_choice]
                response = get_gemini_response(
                    input_text or "", image_bytes, uploaded_file.type, selected_prompt
                )

                st.subheader(f"📜 Result: {prompt_choice}")
                st.markdown("---")
                st.markdown(response)
            except Exception as e:
                st.error(f"Error: {str(e)}")
