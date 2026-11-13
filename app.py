import asyncio
import base64
import edge_tts
import requests
import streamlit as st

GEMINI_API_KEY = "AQ.Ab8RN6IDI5_9qub-AQn_685wgpvWi3DhpgXUYAvsSDwGU7UkZA"
GROQ_API_KEY = "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"

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

def think(prompt, uploaded_file=None):
    try:
        parts = [{"text": prompt if prompt else "Is image ko analyze karo:"}]
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
        raise Exception("Gemini Fail")
    except:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            return f"Groq Error: {res.text}" 
        except Exception as e:
            return "Dono API fail ho gayi. Keys check karo."

async def generate_audio_async(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("response.mp3")

def generate_avatar(text):
    asyncio.run(generate_audio_async(text))
    return "response.mp3"

st.set_page_config(page_title="My AGI", layout="centered")

current_device = check_device()
st.title(f"AGI Interface - Live on {current_device} 🌐")

uploaded_file = st.file_uploader("Kavach ko koi photo/screenshot dikhayein (Optional):", type=["jpg", "jpeg", "png"])

user_command = st.text_input("Mujhe command do ya image ke baare me pucho (Jaise: 'tv par aao' ya 'is photo me kya hai'):")

if st.button("Execute") and (user_command or uploaded_file):
    prompt_text = user_command if user_command else "Is image ko analyze karke batao kya hai."
    
    if "tv par aao" in prompt_text.lower():
        set_device("TV")
        st.success("TV par switch ho raha hai...")
        st.stop()
        
    with st.spinner("Soch raha hoon aur dekh raha hoon..."):
        ai_thought = think(prompt_text, uploaded_file)
        
    sync_memory(prompt_text, ai_thought)
    
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
    
