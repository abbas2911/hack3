from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

SCRIPT = ""

API_KEY = 'AIzaSyCGb1skZSqm7Z7BkNg8lj6OBq33lGjYY2s'
genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

model = genai.GenerativeModel(model_name='gemini-1.0-pro', generation_config=generation_config, safety_settings=safety_settings)

PROMPT_PARTS_1 = '''
Act as if you are a feature film promoter. Your job is to take user topic 
and generate keywords and the overall tone based on the given topic. This will
be used to create a script for a short video. You are only to generate the 
keywords and the overall tone that you identify from the topic and find 
appropriate. 

For example, given the topic: 
A horror feature film that has a wendigo-like figure chasing a dog as it took a poop in the creature's backyard. 

Your keyword output should resemble the following:
Wendigo, Canine, Backyard, Foggy Night, Ancient Evil, Forbidden Ground, Desperate Dash, Nature's Call, Nightmare's Chase, Unseen Terror, Sounds of the Hunt, Desperation

Your overall tone output should resemble the following:
Eerie and suspenseful, Fast-paced and thrilling
'''

PROMPT_PARTS_2 = '''
You are a professional script writer for advertisements. Your job is to 
take the given topic, keywords and the overall tone. And using this 
information, generate a script for a video that is around 20 seconds 
long.

For example, given the topic: A horror feature film that has a wendigo-like 
figure chasing a dog as it took a poop in the creature's backyard.

Keywords: Wendigo, Canine, Backyard, Foggy Night, Ancient Evil, 
Forbidden Ground, Desperate Dash, Nature's Call, Nightmare's Chase, 
Unseen Terror, Sounds of the Hunt, Desperation

Overall Tone: Eerie and suspenseful, Fast-paced and thrilling 

Your script should resemble the following: 
On a foggy night, deep in forbidden ground, a desperate dog succumbs to 
natures call. Unbeknownst, ancient evil stirs. The Wendigo awakens, unseen 
terror lurking. Sounds of the hunt pierce the night. In a desperate dash, 
the canine flees, but the nightmare's chase has begun
'''

app = Flask(__name__)

def generate_gemini_response(question, input_prompt):
    prompt_parts = [input_prompt, question]
    response = model.generate_content(prompt_parts)
    output = response.text

    response_parts = output.split("**Overall Tone:**")
    keywords_part = response_parts[0].replace("**Keywords:**", "").strip()
    tone_part = response_parts[1].strip() if len(response_parts) > 1 else ""

    keywords = [keyword.strip() for keyword in keywords_part.split('*') if keyword.strip()]
    overall_tone = [tone.strip() for tone in tone_part.split('*') if tone.strip()]

    return keywords, overall_tone

def generate_script(topic, keywords, overall_tone, input_prompt):
    script_prompt = f'''
    Topic: {topic}
    Keywords: {", ".join(keywords)}
    Overall Tone: {", ".join(overall_tone)}
    '''
    
    prompt_parts = [input_prompt, script_prompt]
    response = model.generate_content(prompt_parts)
    return response.text.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        action = data.get('action')
        
        if action == 'generate_keywords_tone':
            topic = data.get('topic')
            keywords, overall_tone = generate_gemini_response(f"User Topic: {topic}", PROMPT_PARTS_1)
            return jsonify(keywords=keywords, overall_tone=overall_tone)
        
        elif action == 'generate_script':
            topic = data.get('topic')
            keywords = data.get('keywords')
            overall_tone = data.get('overall_tone')
            script = generate_script(topic, keywords, overall_tone, PROMPT_PARTS_2)
            return jsonify(script=script)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)