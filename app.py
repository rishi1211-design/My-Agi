import streamlit as st
import requests
import base64

# --- SECURE CREDENTIALS (VIA STREAMLIT SECRETS) ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ELEVENLABS_API_KEY = st.secrets.get("ELEVENLABS_API_KEY", "").strip()

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
            return res.json()['status']
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

def think(prompt, uploaded_file=None, audio_file_obj=None, mode="💬 General Intelligence"):
    try:
        system_instruction = "You are Kavach, an advanced AGI assistant."
        if "Image Generation" in mode:
            system_instruction = "You are an expert AI visual artist and prompt engineer. Describe the requested image concept in vivid detail, specifying lighting, style, colors, and composition."
        elif "Code & Canvas" in mode:
            system_instruction = "You are an elite software architect and coder. Provide clean, well-commented, production-ready code snippets with clear instructions."
        elif "File Analysis" in mode:
            system_instruction = "You are a data forensics expert. Analyze the provided data, document, or image deeply and provide clear insights and bullet points."

        full_prompt = f"{system_instruction}\n\nUser Query: {prompt if prompt else 'Is audio ya data ko analyze karo.'}"

        parts = [{"text": full_prompt}]
        
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            encoded_file = base64.b64encode(file_bytes).decode('utf-8')
            mime_type = uploaded_file.type
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": encoded_file
                }
            })

        if audio_file_obj is not None:
            audio_bytes = audio_file_obj.getvalue()
            encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": "audio/webm",
                    "data": encoded_audio
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

# --- ELEVENLABS AI VOICE ENGINE (ROBUST & CLEAN) ---
def generate_elevenlabs_audio(text, filename="response.mp3"):
    if not ELEVENLABS_API_KEY:
        return None
    
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Adam Voice ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except:
        pass
    return None

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
    @keyframes boot-fade {
        0% { opacity: 0; transform: scale(0.9); }
        100% { opacity: 1; transform: scale(1); }
    }
    .boot-container {
        animation: boot-fade 1.5s ease-in-out;
        text-align: center;
    }
    h1 {
        text-shadow: 0 0 15px rgba(0, 255, 204, 0.7);
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

# --- BOOT ANIMATION & GREETING ON FIRST LOAD ---
if 'booted' not in st.session_state:
    st.session_state.booted = True
    try:
        boot_audio = generate_elevenlabs_audio("Kavach AI assistant online. All neural security protocols activated.", "boot.mp3")
        if boot_audio:
            st.audio(boot_audio, format="audio/mp3", autoplay=True)
    except:
        pass

current_device = check_device()

st.markdown("""
<div class="boot-container">
    <h1 style='color: #00ffcc;'>🛡️ KAVACH AGI</h1>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: center; color: #8b949e;'>Active Node: <b>{current_device}</b> | Status: <span style='color: #00ffcc;'>Online 🟢</span></p>", unsafe_allow_html=True)
st.markdown("---")

# --- FEATURE MODE SELECTOR ---
ai_mode = st.selectbox(
    "Kavach Capability Mode:",
    ["💬 General Intelligence", "🎨 Image Generation", "💻 Code & Canvas", "📁 File Analysis"],
    label_visibility="collapsed"
)

# --- PROFESSIONAL VOICE & CHAT INPUT BAR ---
col_file, col_text = st.columns([1, 4])
with col_file:
    uploaded_file = st.file_uploader("📎", type=["jpg", "jpeg", "png", "pdf", "txt"], label_visibility="collapsed")
with col_text:
    user_command = st.text_input("💬", placeholder="Message Kavach...", label_visibility="collapsed")

# --- NATIVE VOICE ASSISTANT MIC RECORDER ---
st.markdown("<p style='color: #00ffcc; font-size: 0.9em; margin-bottom: 2px;'>🎙️ Professional Voice Assistant Mic:</p>", unsafe_allow_html=True)
voice_input = st.audio_input("Speak to Kavach", label_visibility="collapsed")

if st.button("⚡ EXECUTE COMMAND") or voice_input is not None:
    prompt_text = user_command if user_command else "Voice command received. Analyze this audio."
    
    if "tv par aao" in prompt_text.lower():
        set_device("TV")
        st.success("🔄 Switching active stream to TV node...")
        st.stop()
        
    with st.spinner("🧠 Processing Voice & Multi-Brain Neural Network..."):
        ai_thought = think(prompt_text, uploaded_file, voice_input, ai_mode)
        
    sync_memory(prompt_text, ai_thought)
    
    with st.spinner("🎙️ Synthesizing Neural Voice Response..."):
        try:
            audio_file = generate_elevenlabs_audio(ai_thought, "response.mp3")
            st.markdown(f"""
            <div class="chat-card" style="text-align: center;">
                <div class="ai-agent">🛡️</div>
                <div class="ai-avatar">🛡️</div>
                <p style="color: #8b949e; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;"><b>Kavach Neural Voice Node ({ai_mode})</b></p>
                <p style="font-size: 1.2em; color: #ffffff; text-align: left; margin-top: 15px;">{ai_thought}</p>
            </div>
            """, unsafe_allow_html=True)
            if audio_file:
                st.audio(audio_file, format="audio/mp3", autoplay=True)
        except:
            st.markdown(f"""
            <div class="chat-card" style="text-align: center;">
                <div class="ai-avatar">🛡️</div>
                <p style="color: #8b949e; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;"><b>Kavach Neural Voice Node ({ai_mode})</b></p>
                <p style="font-size: 1.2em; color: #ffffff; text-align: left; margin-top: 15px;">{ai_thought}</p>
            </div>
            """, unsafe_allow_html=True)
            st.warning("Text output displayed successfully.")
