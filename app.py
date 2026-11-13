import streamlit as st
import requests
import asyncio
import edge_tts
import base64

# --- SECURE CREDENTIALS (VIA STREAMLIT SECRETS) ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def sync_memory(user_text, ai_text):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    data = {"user_input": user_text, "ai_response": ai_text}
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/memory", headers=headers, json=data)
    except:
        pass 

def check_device():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/device_status?select=status&id=eq.1", headers=headers)
        if res.status_code == 200 and len(res.json()) > 0:
            return res.json()[0]['status']
    except:
        pass
    return "Mobile"

def set_device(device_name):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    data = {"status": device_name}
    try:
        requests.patch(f"{SUPABASE_URL}/rest/v1/device_status?id=eq.1", headers=headers, json=data)
    except:
        pass

def think(prompt, uploaded_file=None, mode="💬 General Intelligence"):
    try:
        # Mode-wise expert system instructions
        system_instruction = "You are Kavach, an advanced AGI assistant."
        if "Image Generation" in mode:
            system_instruction = "You are an expert AI visual artist and prompt engineer. Describe the requested image concept in vivid detail, specifying lighting, style, colors, and composition."
        elif "Code & Canvas" in mode:
            system_instruction = "You are an elite software architect and coder. Provide clean, well-commented, production-ready code snippets with clear instructions."
        elif "File Analysis" in mode:
            system_instruction = "You are a data forensics expert. Analyze the provided data, document, or image deeply and provide clear insights and bullet points."

        full_prompt = f"{system_instruction}\n\nUser Query: {prompt if prompt else 'Is data ko analyze karo.'}"

        parts = [{"text": full_prompt}]
        if uploaded_file is not None:
            image_bytes = uploaded_file.getvalue()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            mime_type = uploaded_file.type
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": encoded_image
                }
            })
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": parts}]}
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        
        url_groq = "https://api.groq.com/openai/v1/chat/completions"
        headers_groq = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload_groq = {
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": full_prompt}]
        }
        res_groq = requests.post(url_groq, headers=headers_groq, json=payload_groq)
        if res_groq.status_code == 200:
            return res_groq.json()['choices'][0]['message']['content']
        return f"Gemini Error: {res.text}"
    except Exception as e:
        return f"Error: {str(e)}"

async def generate_audio_async(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("response.mp3")

def generate_avatar(text):
    asyncio.run(generate_audio_async(text))
    return "response.mp3"

st.set_page_config(page_title="Kavach AGI", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #00ffcc;
    }
    .stTextInput input {
        background-color: #1a1c23;
        color: #ffffff;
        border: 1px solid #00ffcc;
        border-radius: 8px;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1a1c23;
        color: #ffffff;
        border: 1px solid #00ffcc;
        border-radius: 8px;
    }
    .stButton button {
        background: linear-gradient(45deg, #00ffcc, #0077ff);
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        width: 100%;
        padding: 0.5rem;
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.3);
    }
    .stButton button:hover {
        background: linear-gradient(45deg, #0077ff, #00ffcc);
        color: #ffffff;
    }
    .chat-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00ffcc;
        margin-top: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    h1 {
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);
    }
    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 204, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(0, 255, 204, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 204, 0); }
    }
    .ai-avatar {
        width: 70px;
        height: 70px;
        margin: 0 auto 15px auto;
        background: linear-gradient(135deg, #00ffcc, #0077ff);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        animation: pulse-ring 2s infinite;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
    }
</style>
""", unsafe_allow_html=True)

current_device = check_device()

st.markdown(f"<h1 style='text-align: center; color: #00ffcc;'>🛡️ KAVACH AGI</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #8b949e;'>Active Node: <b>{current_device}</b> | Status: <span style='color: #00ffcc;'>Online 🟢</span></p>", unsafe_allow_html=True)
st.markdown("---")

# --- FEATURE MODE SELECTOR ---
ai_mode = st.selectbox(
    "Kavach Capability Mode:",
    ["💬 General Intelligence", "🎨 Image Generation", "💻 Code & Canvas", "📁 File Analysis"],
    label_visibility="collapsed"
)

# --- COMPACT CHAT INPUT BAR ---
col_file, col_text = st.columns([1, 4])
with col_file:
    uploaded_file = st.file_uploader("📎", type=["jpg", "jpeg", "png", "pdf", "txt"], label_visibility="collapsed")
with col_text:
    user_command = st.text_input("💬", placeholder="Message Kavach...", label_visibility="collapsed")

if st.button("⚡ EXECUTE COMMAND") and (user_command or uploaded_file):
    prompt_text = user_command if user_command else "Is data ko analyze karke batao kya hai."
    
    if "tv par aao" in prompt_text.lower():
        set_device("TV")
        st.success("🔄 Switching active stream to TV node...")
        st.stop()
        
    with st.spinner("🧠 Processing via Multi-Brain Neural Network..."):
        ai_thought = think(prompt_text, uploaded_file, ai_mode)
        
    sync_memory(prompt_text, ai_thought)
    
    with st.spinner("🎙️ Synthesizing Voice Response..."):
        try:
            audio_file = generate_avatar(ai_thought)
            st.markdown(f"""
            <div class="chat-card" style="text-align: center;">
                <div class="ai-avatar">🛡️</div>
                <p style="color: #8b949e; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;"><b>Kavach Neural Voice Node ({ai_mode})</b></p>
                <p style="font-size: 1.2em; color: #ffffff; text-align: left; margin-top: 15px;">{ai_thought}</p>
            </div>
            """, unsafe_allow_html=True)
            st.audio(audio_file, format="audio/mp3", autoplay=True)
        except:
            st.markdown(f"""
            <div class="chat-card" style="text-align: center;">
                <div class="ai-avatar">🛡️</div>
                <p style="color: #8b949e; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;"><b>Kavach Neural Voice Node ({ai_mode})</b></p>
                <p style="font-size: 1.2em; color: #ffffff; text-align: left; margin-top: 15px;">{ai_thought}</p>
            </div>
            """, unsafe_allow_html=True)
            st.warning("Audio generation encountered an issue, text output displayed successfully.")
