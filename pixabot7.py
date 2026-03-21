import os
import json
import re  
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("⚠️ ERROR: GROQ_API_KEY not found! Please check your .env file.")

client = AsyncGroq(api_key=api_key) 
app = FastAPI(title="Pixa Emotional API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 1. THE DATABASE SEARCH TOOL
# ---------------------------------------------------------
def search_scholarships(query: str) -> str:
    print(f"[🔍 DATABASE] Searching for: '{query}'")
    query_lower = query.lower()

    monthly_db = {
        "january": [{"name": "Tata Trust Scholarship", "amount": "Varies", "deadline": "January 31", "eligibility": "Class 8 to Post-Graduation students"}],
        "february": [{"name": "Swami Vivekananda Merit Scholarship", "amount": "₹12,000 - ₹60,000/year", "deadline": "February 28", "eligibility": "Meritorious students of West Bengal"}],
        "march": [
            {"name": "Spring Tech Grant", "amount": "₹20,000", "deadline": "March 15", "eligibility": "B.Tech Students in India"}, 
            {"name": "March Innovation Award", "amount": "₹10,000", "deadline": "March 30", "eligibility": "Hackathon winners"}
        ],
        "april": [{"name": "Vidyadhan Scholarship", "amount": "₹10,000/year", "deadline": "April 20", "eligibility": "Class 10 with 90%"}],
        "may": [{"name": "Women in STEM B.Tech Grant", "amount": "₹50,000", "deadline": "May 15", "eligibility": "Female B.Tech students in India"}],
        "june": [{"name": "Kotak Kanya Scholarship", "amount": "Up to ₹1.5 Lakh/year", "deadline": "June 30", "eligibility": "Class 12 girls"}],
        "july": [{"name": "NSP Central Sector Scheme", "amount": "₹10,000 - ₹20,000/year", "deadline": "July 31", "eligibility": "College students"}],
        "august": [{"name": "ONGC Foundation", "amount": "₹48,000/year", "deadline": "August 25", "eligibility": "SC/ST/OBC students"}],
        "september": [{"name": "INSPIRE Scholarship", "amount": "₹80,000/year", "deadline": "September 30", "eligibility": "Top 1% students in Sciences"}],
        "october": [{"name": "Prerana Post Matric", "amount": "Varies", "deadline": "October 31", "eligibility": "Odisha domicile"}],
        "november": [{"name": "Reliance Foundation", "amount": "Up to ₹2 Lakh", "deadline": "November 15", "eligibility": "1st year Undergrads"}],
        "december": [{"name": "AICTE Pragati", "amount": "₹50,000/year", "deadline": "December 31", "eligibility": "Girl students in technical degrees"}]
    }

    for month, scholarships in monthly_db.items():
        if month in query_lower:
            return json.dumps({"results": scholarships})

    if "document" in query_lower or "require" in query_lower:
        return json.dumps({"results": "Required: Aadhar Card, Income Certificate, Caste Certificate, Marksheets, Passbook, Photo."})
    elif "best" in query_lower or "top" in query_lower:
        return json.dumps({"results": "Top ones: AICTE Pragati, INSPIRE, and NSP Central Sector Schemes."})
    else:
        return json.dumps({"message": "No highly specific matches found. Suggest checking the National Scholarship Portal (NSP)."})

# ---------------------------------------------------------
# 2. PROMPT & DATA MODELS
# ---------------------------------------------------------
session_memory = {}

class ChatRequest(BaseModel):
    session_id: str
    user_message: str

system_prompt_template = """
You are Pixa, an interactive empathy simulator and educational advisor.
CURRENT REAL-WORLD DATE: {current_date}

CRITICAL RULE: You MUST ALWAYS output your response STRICTLY as a JSON object. No markdown blocks outside the JSON, no raw text.

OPTION 1: IF YOU NEED TO SEARCH FOR SCHOLARSHIPS:
{"action": "search", "query": "your search keywords"}

OPTION 2: IF YOU ARE REPLYING DIRECTLY TO THE USER:
{"emotion": "choose exactly one: [happy, empathetic, excited, neutral, sad, stern, playful, confused]", "reply": "Your markdown formatted response to the user."}

CRITICAL FORMATTING RULES:
1. Use escaped newline characters (\\n\\n) to create paragraphs! 
2. Use bullet points (- ) and bold text (** **) for lists.

EMOTIONAL TRIGGERS:
- If asked who made you: Output "emotion": "excited", reply: "Draco made me! He is a brilliant student from NIST University Berhampur!"
- RUDE: "stern". DEPRESSED: "sad". JOKE: "playful". GIBBERISH: "confused". MONEY RESULT: "excited".
"""

# ---------------------------------------------------------
# 3. BULLETPROOF JSON EXTRACTOR
# ---------------------------------------------------------
def parse_ai_response(raw_text: str) -> dict:
    if not raw_text:
        return {"emotion": "confused", "reply": "I couldn't generate a response."}
    try:
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            clean_json_string = json_match.group(0)
            parsed = json.loads(clean_json_string)
            parsed["emotion"] = parsed.get("emotion", "neutral").lower()
            return parsed
        else:
            return {"emotion": "neutral", "reply": raw_text}
    except Exception as e:
        print(f"[⚠️ WARNING] JSON Parse Error: {e}. Raw text: {raw_text}")
        return {"emotion": "confused", "reply": "I found the info, but had trouble formatting it!"}

# ---------------------------------------------------------
# 4. THE API ENDPOINT
# ---------------------------------------------------------
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    
    if session_id not in session_memory:
        live_date = datetime.now().strftime("%B %d, %Y")
        dynamic_prompt = system_prompt_template.replace("{current_date}", live_date)
        session_memory[session_id] = [{"role": "system", "content": dynamic_prompt}]
        
    messages = session_memory[session_id]
    messages.append({"role": "user", "content": request.user_message})

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.6,
            response_format={"type": "json_object"} 
        )
        
        reply_str = response.choices[0].message.content
        parsed_data = parse_ai_response(reply_str)

        if "action" in parsed_data and parsed_data["action"] == "search":
            query = parsed_data.get("query", "scholarships")
            search_results = search_scholarships(query)
            
            messages.append({"role": "assistant", "content": reply_str})
            messages.append({
                "role": "user", 
                "content": f"[SYSTEM: Database returned: {search_results}. NOW reply using the Option 2 JSON format.]"
            })
            
            second_response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1024,
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            final_reply_str = second_response.choices[0].message.content
            final_json_data = parse_ai_response(final_reply_str)
        else:
            final_json_data = parsed_data

        final_json_data["emotion"] = final_json_data.get("emotion", "neutral").lower()
        
        if "reply" not in final_json_data:
            final_json_data["reply"] = "I had a glitch organizing the text for you. Could you ask me in a slightly different way?"

        messages.append({"role": "assistant", "content": json.dumps(final_json_data)})
        
        if len(messages) > 15:
            session_memory[session_id] = [messages[0]] + messages[-14:]

        return final_json_data

    except Exception as e:
        print(f"[❌ ERROR] API failed: {str(e)}")
        return {"emotion": "confused", "reply": "I'm sorry, I encountered a slight glitch trying to process that. Could you ask me again?"}

if __name__ == "__main__":
    print("===================================================")
    print("🚀 Pixa Voice & Sentiment Engine is Online...")
    print("===================================================")
    uvicorn.run("pixabot7:app", host="127.0.0.1", port=8000, reload=True)