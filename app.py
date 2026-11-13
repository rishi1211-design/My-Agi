import streamlit as st
import requests
import asyncio
import edge_tts

# --- APNI API KEYS YAHAN DAALEIN ---
GEMINI_API_KEY = "AQ.Ab8RN6IDI5_9qub-AQn_685wgpvWi3DhpgXUYAvsSDwGU7UkZA"
GROQ_API_KEY = "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"

# --- CLOUD MEMORY (SUPABASE) ---
SUPABASE_URL = "https://oeamiykxvmmdkbrplqwr.supabase.co"
SUPABASE_KEY = "Sb_publishable_jlilReMVuIpS9SCULlKGtw_wK9R0xqE"

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

# --- MULTI-BRAIN (GEMINI + GROQ) ---
def think(prompt):
    try:
        # Pehla Dimaag: Gemini 3.8 Flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        raise Exception("Gemini Fail")
    except:
        try:
            # Dusra Dimaag (Fallback): Groq ka purana aur sahi model
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",  # Yahan sahi model wapas daal diya hai
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            return f"Groq Error: {res.text}" 
        except Exception as e:
            return "Dono API fail ho gayi. Keys check karo."

# --- VOICE GENERATION (FREE UNLIMITED) ---
async def generate_audio_async(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("response.mp3")

def generate_avatar(text):
    asyncio.run(generate_audio_async(text))
    return "response.mp3"

# --- MAIN APP UI ---
st.set_page_config(page_title="My AGI", layout="centered")

current_device = check_device()
st.title(f"AGI Interface - Live on {current_device} 🌐")

user_command = st.text_input("Mujhe command do (Jaise: 'tv par aao' ya koi sawal):")

if st.button("Execute") and user_command:
    
    # Device switch ke liye exact match
    if "tv par aao" in user_command.lower():
        set_device("TV")
        st.success("TV par switch ho raha hai...")
        st.stop()
        
    with st.spinner("Soch raha hoon..."):
        ai_thought = think(user_command)
        
    sync_memory(user_command, ai_thought)
    
    with st.spinner("Aawaz generate kar raha hoon..."):
        try:
            audio_file = generate_avatar(ai_thought)
            st.write("---")
            st.write(f"**AGI:** {ai_thought}")
            st.audio(audio_file, format="audio/mp3", autoplay=True)
        except:
            st.write("---")
            st.write(f"**AGI:** {ai_thought}")
            st.warning("Aawaz me dikkat aayi, par text aa gaya hai.")
            
