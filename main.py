#import Google's genai package for interacting with API
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

# passes API key to initialize API client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# saves Gemini's response to prompt to variable
response = client.models.generate_content(
    # specifies model version to use
    model = 'gemini-2.0-flash',
    contents = types.Content(
        parts = [
            types.Part(
                # uses YouTube URL directly as per Gemini API documentation
                file_data=types.FileData(file_uri='https://www.youtube.com/watch?v=Md3rdQssxxE')
            ),
            # passes prompt to Gemini for note generation
            types.Part(text='Generate a SOAP style psychotherapy note based on the contents of the video.'
               'Include a Mental Status Examination and Risk Assessment.')
        ]
    )
)

print(response.text)