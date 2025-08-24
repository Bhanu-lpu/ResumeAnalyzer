from openai import OpenAI
import os

# Load API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello, say hi!"}]
)

print(resp.choices[0].message.content)
