from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=key)

try:
    resp = client.chat.completions.create(
        model='groq/compound-mini',
        messages=[
            {'role': 'system', 'content': 'Reply only in valid JSON like {"emotion":"happy","reply":"hello"}'},
            {'role': 'user', 'content': 'hi'}
        ],
        max_tokens=100,
        temperature=0.5,
        response_format={'type': 'json_object'}
    )
    print('SUCCESS:', resp.choices[0].message.content)
except Exception as e:
    print('ERROR:', type(e).__name__, str(e))
