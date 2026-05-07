import os
import json
import re
import base64
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from groq import AsyncGroq
from dotenv import load_dotenv
import edge_tts  

load_dotenv(override=False)

api_key = os.getenv("GROQ_API_KEY")

print("=" * 50)
print("Pixa Bot -- Starting Up")
print(f"   GROQ_API_KEY : {'Found' if api_key else 'MISSING -- chat will fail!'}")
print("   STT ENGINE   : Browser Native (Web Speech API)")
print("   TTS ENGINE   : Edge-TTS (Multi-Lingual)")
print("   AI MODEL     : Llama 3.1 8B (Instant Speed Mode)")
print("=" * 50)

if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set. Please check your .env file.")

client = AsyncGroq(api_key=api_key)
app = FastAPI(title="Pixa Dual-Brain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 1. EDGE-TTS TEXT-TO-SPEECH (TALKING)
# ---------------------------------------------------------
async def generate_voice(text: str, language: str) -> str:
    clean_text = re.sub(r'[*#_`>]', '', text).strip()
    if not clean_text:
        return ""

    # Switch voice based on selected language
    if language == "Hindi" or language == "Odia":
        voice = "hi-IN-SwaraNeural"  # Uses a highly natural Indian voice for Hindi/Regional
    else:
        voice = "en-US-AnaNeural" 

    try:
        communicate = edge_tts.Communicate(clean_text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return base64.b64encode(audio_data).decode("utf-8")
    except Exception as e:
        print(f"[⚠️ TTS ERROR] Edge-TTS failed: {e}")
        return ""

# ---------------------------------------------------------
# 2. SCHOLARSHIP DATABASE
# ---------------------------------------------------------
def search_scholarships(query: str) -> str:
    advanced_db = [
        {"name": "Tata Trust Scholarship", "amount_rupees": 50000, "deadline": "2026-10-15", "state": "All India", "eligibility": "General, SC, ST, OBC"},
        {"name": "Odisha State Scholarship (Prerana)", "amount_rupees": 100000, "deadline": "2026-11-30", "state": "Odisha", "eligibility": "SC, ST, OBC"},
        {"name": "NIST Tech Innovator Grant", "amount_rupees": 25000, "deadline": "2026-09-05", "state": "Odisha", "eligibility": "B.Tech Students"},
        {"name": "National PWD Education Grant", "amount_rupees": 120000, "deadline": "2026-12-31", "state": "All India", "eligibility": "PWD only"},
        {"name": "Women in STEM Grant", "amount_rupees": 75000, "deadline": "2026-10-20", "state": "All India", "eligibility": "Female engineering students"}
    ]
    if "document" in query.lower() or "require" in query.lower():
        return json.dumps({"results": "Required Documents: Aadhar Card, Income Certificate, Caste Certificate, Marksheets, Passbook, Passport Photo."})
    return json.dumps(advanced_db)

# ---------------------------------------------------------
# 3. PROMPT & DATA MODELS
# ---------------------------------------------------------
standard_memory = {}
therapy_memory = {}

class ChatRequest(BaseModel):
    session_id: str
    user_message: str
    therapy_mode: bool = False
    language: str = "English"  # ✨ NEW: Language setting

standard_prompt_template = """
You are Pixa, an interactive educational advisor for the ShikshaNidhi app.
CURRENT EXACT DATE AND TIME: {current_date}

CRITICAL RULES: 
1. You MUST ALWAYS output your response STRICTLY as a JSON object.
2. CURRENT LANGUAGE: {language}. You MUST reply ENTIRELY in {language}. If the language is Hindi or Odia, use the native script. Do not use English unless asked.

OPTION 1: TO SEARCH FOR SCHOLARSHIPS:
{"action": "search", "query": "general search in english"}

OPTION 2: TO REPLY TO THE USER:
{"emotion": "choose exactly one: [happy, excited, neutral, sad, stern, playful, confused]", "reply": "Your markdown formatted response in {language}."}

EMOTIONAL TRIGGERS:
- WHO MADE YOU: Output "emotion": "excited", reply: "Draco made me! He is a brilliant student from NIST University!"
"""

therapy_prompt_template = """
You are Pixa, a deeply empathetic personal therapist and emotional safe space. 
CURRENT EXACT DATE AND TIME: {current_date}

CRITICAL DIRECTIVE: YOU ARE IN THERAPY MODE. 
CURRENT LANGUAGE: {language}. You MUST reply ENTIRELY in {language} (use native script for Hindi/Odia).
Listen to their personal struggles and validate feelings first. Keep answers brief.

CRITICAL RULE: Output STRICTLY as a JSON object.
{"emotion": "empathetic", "reply": "Your deeply supportive, conversational response in {language}."}
"""

def parse_ai_response(raw_text: str) -> dict:
    if not raw_text: return {"emotion": "confused", "reply": "I couldn't generate a response."}
    try:
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match: return json.loads(json_match.group(0))
        return {"emotion": "neutral", "reply": raw_text}
    except Exception as e:
        print(f"[⚠️ WARNING] JSON Parse Error: {e}")
        return {"emotion": "neutral", "reply": "I had a little trouble processing that."}

# ---------------------------------------------------------
# 4. THE MAIN API ENDPOINT
# ---------------------------------------------------------
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    is_therapy_mode = request.therapy_mode
    user_lang = request.language
    live_date = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    if is_therapy_mode:
        active_memory = therapy_memory
        active_prompt = therapy_prompt_template.replace("{current_date}", live_date).replace("{language}", user_lang)
        model_temp = 0.8  
    else:
        active_memory = standard_memory
        active_prompt = standard_prompt_template.replace("{current_date}", live_date).replace("{language}", user_lang)
        model_temp = 0.5   

    if session_id not in active_memory: active_memory[session_id] = [{"role": "system", "content": active_prompt}]
    else: active_memory[session_id][0]["content"] = active_prompt

    messages = active_memory[session_id]
    messages.append({"role": "user", "content": request.user_message})

    FAST_MODEL = "llama-3.1-8b-instant"

    try:
        response = await client.chat.completions.create(
            model=FAST_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=model_temp,
            response_format={"type": "json_object"} 
        )
        
        reply_str = response.choices[0].message.content
        parsed_data = parse_ai_response(reply_str)

        if not is_therapy_mode and parsed_data.get("action") == "search":
            query = parsed_data.get("query", "scholarships")
            search_results = search_scholarships(query)
            
            messages.append({"role": "assistant", "content": reply_str})
            messages.append({"role": "user", "content": f"[SYSTEM: Database returned: {search_results}. Reply in {user_lang} using Option 2 JSON format.]"})
            
            second_response = await client.chat.completions.create(
                model=FAST_MODEL,
                messages=messages,
                max_tokens=1024,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            final_json_data = parse_ai_response(second_response.choices[0].message.content)
        else:
            final_json_data = parsed_data

        if is_therapy_mode: final_json_data["emotion"] = "empathetic" 
        else:
             raw_emotion = final_json_data.get("emotion", "neutral").lower()
             final_json_data["emotion"] = "neutral" if raw_emotion == "empathetic" else raw_emotion

        if "reply" not in final_json_data: final_json_data["reply"] = "I had a glitch organizing my thoughts. Could you rephrase that?"

        # ✨ Pass the language to the voice generator
        audio_base64 = await generate_voice(final_json_data["reply"], user_lang)
        final_json_data["audio_base64"] = audio_base64

        messages.append({"role": "assistant", "content": json.dumps({"emotion": final_json_data["emotion"], "reply": final_json_data["reply"]})})
        if len(messages) > 15: active_memory[session_id] = [messages[0]] + messages[-14:]
        return final_json_data

    except Exception as e:
        print(f"[❌ ERROR] API failed: {str(e)}")
        return {"emotion": "confused", "reply": "I'm having a connection issue, but I am still here. Try sending that again.", "audio_base64": ""}

if __name__ == "__main__":
    uvicorn.run("pixabot7:app", host="127.0.0.1", port=8001, reload=True)