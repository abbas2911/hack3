from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

SCRIPT = ""
URL = ""

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

def generate_video(topic, keywords):
    import requests
    import time
    import json

    # Define your credentials and constants
    USER_ID = 'MYCO'
    ACCESS_TOKEN = 'eyJraWQiOiJPc0pnWUtUS0tlQkN5eDFKdkVyUGdTZHRpNWRmSzc2aksrTm5mVVI5aVJvPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI1aWdpODJkYjMzOTFoZ3NsMDF1Z29zMGlsZCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoicGljdG9yeWFwaXNcL3BpY3RvcnlhcGlzLnJlYWQgcGljdG9yeWFwaXNcL3BpY3RvcnlhcGlzLndyaXRlIiwiYXV0aF90aW1lIjoxNzE3ODQ0MjQyLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0yLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMl9zbFRDOURZcHoiLCJleHAiOjE3MTc4NDc4NDIsImlhdCI6MTcxNzg0NDI0MiwidmVyc2lvbiI6MiwianRpIjoiMTYzNjdlNzQtYTY3Yi00MTcwLTk0MzMtZjk5MDI2MGM3YTE1IiwiY2xpZW50X2lkIjoiNWlnaTgyZGIzMzkxaGdzbDAxdWdvczBpbGQifQ.WazqBr8FsUMqHw1m6zMINDw4zrqVT6evGzvMNUahpjj7Dj9PdYX3c4Vns-jHOeiqje1mwi_ezaHAxNqW54fU01uBpD5lxlozgStLuU9RSJoNzaterKSviwNVz4j5EIXasa77hJnt2OvEEginfLVN8NJJq_6SYiZquwZ1pKX-fqwovpCgNdIzvN34N7AwE6T2hq7BPQBekbVHyZlMyUDNZVHblneTQtQU2agQfLaaHSibYHAxij67bea0FCHDTWil6ODoqatUJYufbcbES5uhUZglWtQru-HljP0Tz4RTeidA0k23psLkFGfgnUUnjwO2URaN6fq8m831hYxSlecaQQ'

    # Function to initiate video preview request
    def initiate_video_preview():
        url = "https://api.pictory.ai/pictoryapis/v1/video/storyboard"
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'X-Pictory-User-Id': USER_ID
        }
        data = {
            "audio": {
                "aiVoiceOver": {
                    "speaker": "Arthur",
                    "speed": "100",
                    "amplifyLevel": "1"
                },
                "autoBackgroundMusic": True,
                "backGroundMusicVolume": 0.5
            },
            "brandLogo": {
                "url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg",
                "verticalAlignment": "top",
                "horizontalAlignment": "right"
            },
            "videoName": topic,
            "videoDescription": keywords,
            "language": "en",
            "videoWidth": "1080",
            "videoHeight": "1920",
            "scenes": [
                {
                    "text": SCRIPT,
                    "voiceOver": True,
                    "splitTextOnNewLine": True,
                    "splitTextOnPeriod": True
                }
            ],
            "webhook": "https://webhook.site/b88330d8-43f6-4eb6-b8e2-232f515016b1"
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to initiate video preview request")
            print(response.text)
            return None

    # Function to monitor job status
    def monitor_job_status(job_id):
        url = f"https://api.pictory.ai/pictoryapis/v1/jobs/{job_id}"
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'X-Pictory-User-Id': USER_ID,
            'accept': 'application/json'
        }
    # Initial delay to avoid immediate rate limiting
        time.sleep(2)
        

        while True:
            response = requests.get(url, headers=headers)
            

            if response.status_code == 200:
                job_status = response.json()
                print(f"Job Status Response: {job_status}")  # Debug: Print the entire response for inspection
                
                if 'status' in job_status['data'] and job_status['data']['status'] == 'in-progress':
                    print("Job is still in progress...")
                    time.sleep(3)  # Wait for 10 seconds before checking again
                else:
                    return job_status
                        
                        
                
                    
            else:
                print("Failed to get job status")
                print(response.text)
                return None

    # Function to initiate final video rendering
    def initiate_video_render(render_params):
        url = "https://api.pictory.ai/pictoryapis/v1/video/render"
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'X-Pictory-User-Id': USER_ID
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(render_params))
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to initiate video rendering")
            print(response.text)
            return None

    # Initiate video preview request
    preview_response = initiate_video_preview()
    if preview_response:
        job_id = preview_response['data']['job_id']
        print(f"Job ID: {job_id}")
        
        # Monitor job status
        job_status = monitor_job_status(job_id)
        print(job_status)
        if job_status:
            if 'data' in job_status and 'preview' in job_status['data'] and 'renderParams' in job_status['data']:
                preview_url = job_status['data']['preview']
                render_params = job_status['data']['renderParams']
                print(f"Preview URL: {preview_url}")
                URL = preview_url
                
                # Initiate final video rendering
                # render_response = initiate_video_render(render_params)
                # if render_response:
                #     final_job_id = render_response['data']['job_id']
                #     print(f"Final Job ID: {final_job_id}")
                    
                #     # Monitor final rendering job status
                #     # final_job_status = monitor_job_status(final_job_id)
                #     # if final_job_status and 'data' in final_job_status and 'videoURL' in final_job_status['data']:
                #     #     final_video_url = final_job_status['data']['videoURL']
                #     #     print(f"Final Video URL: {final_video_url}")
                #     # else:
                #     #     print("Failed to monitor final job status")
                # else:
                #     print("Failed to initiate final video rendering")
            else:
                print("Unexpected response structure for job status:", job_status)
        else:
            print("Failed to monitor job status")
    else:
        print("Failed to initiate video preview request")

    return URL

def generate_gemini_response(question, input_prompt):
    prompt_parts = [input_prompt, question]
    response = model.generate_content(prompt_parts)
    output = response.text

    response_parts = output.split("*Overall Tone:*")
    keywords_part = response_parts[0].replace("*Keywords:*", "").strip()
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
            SCRIPT = generate_script(topic, keywords, overall_tone, PROMPT_PARTS_2)
            return jsonify(script=SCRIPT)
        
        elif action == 'generate_video':
            # Implement your video generation logic here
            topic = data.get('topic')
            keywords = data.get('keywords')
            video_url = generate_video(topic, keywords)
            return jsonify(video_url=video_url)
            


        return render_template('index.html')

if __name__ == "_main_":
    app.run(debug=True)