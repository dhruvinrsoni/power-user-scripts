import os
import sys
import requests
import warnings
import re
from datetime import datetime

# --- Configuration: Suppress Security Warning ---
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# --- Configuration: API Key ---
try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("\n🚨 Error: GOOGLE_API_KEY environment variable not set.")
    sys.exit(1)

def get_gemini_response(prompt_text):
    """Sends the user's prompt to the Gemini REST API and returns the response."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = { 'Content-Type': 'application/json', 'X-goog-api-key': API_KEY }
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
        response.raise_for_status()
        json_response = response.json()
        
        if 'candidates' in json_response and json_response['candidates']:
            return json_response['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return "🚨 API Error: No content candidates found."
    except requests.exceptions.RequestException as e:
        return f"🚨 Network or request error: {e}"
    except (KeyError, IndexError):
        return "🚨 Error parsing API response."

def save_transcript(transcript_log):
    """Saves the conversation to a descriptively named markdown file."""
    if not transcript_log:
        return
        
    # Use a hidden folder in the user's home directory for clean organization
    chat_dir = os.path.join(os.path.expanduser("~"), ".gemini_chats")
    os.makedirs(chat_dir, exist_ok=True)
        
    # Generate a descriptive filename from the first user prompt
    first_prompt = transcript_log[0]['content']
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', first_prompt.split('\n')[0]).strip()
    slug = re.sub(r'\s+', '-', slug).lower()[:40]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(chat_dir, f"{timestamp}_{slug}.md")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in transcript_log:
                if entry['role'] == 'user':
                    f.write(f"**👤 You:**\n\n```text\n{entry['content']}\n```\n\n---\n\n")
                else:
                    f.write(f"**🤖 Gemini:**\n\n{entry['content']}\n\n---\n\n")
        print(f"\n✅ Transcript saved to: {filename}")
    except IOError as e:
        print(f"\n🚨 Error saving transcript: {e}")

def get_multiline_input():
    """Gathers multi-line input from the user until an empty line is entered."""
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except EOFError: # Handles Ctrl+D on Linux/macOS
            break
    return "\n".join(lines)

def main():
    """The main chat loop with a clean, no-dependency UX."""
    transcript = []
    
    print("\n--- Terminal Chatbot with Gemini ---")
    print("Type your message. Press [Enter] on an empty line to send.")
    print("Type 'exit' or 'quit' on a new line and send to end the chat.\n")

    while True:
        print("👤 You:")
        user_input = get_multiline_input()

        if user_input.lower().strip() in ['exit', 'quit']:
            break
        if not user_input.strip():
            continue

        transcript.append({"role": "user", "content": user_input})
        
        print("\n🤖 Gemini is thinking...", end='\r')
        ai_response = get_gemini_response(user_input)
        print(" " * 25, end='\r')
        
        print(f"🤖 Gemini:\n{ai_response}\n")
        transcript.append({"role": "assistant", "content": ai_response})

    save_transcript(transcript)
    print("\n👋 Goodbye!")

# --- Script Execution ---
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: # Handles Ctrl+C
        print("\n\n👋 Chat interrupted. Goodbye!")
        sys.exit(0)

