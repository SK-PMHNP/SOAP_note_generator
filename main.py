#import packages
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import re


#Define a function for splitting note by section for analysis
def split_sections(full_response, sections):
    # Define regex pattern for separating sections
    pattern = r'\b(?:' + '|'.join(re.escape(section) for section in sections) + r')\b'

    # Find match objects in text
    matches = list(re.finditer(pattern, full_response))

    # loop through match objects and decare end to be start of next match object, add text of each section to dictionary
    separated_sections = {}
    for i in range(len(matches)):
        start = matches[i].end()
        header = matches[i].group(0).strip().title()
        if (i + 1 < len(matches)):
            end = matches[i+1].start()
        else:
            end = len(full_response)
        content = re.sub(r'^[\s*\-]+', '', full_response[start:end].strip(':*'))
        separated_sections[header] = content
    return separated_sections


# Define a function for calculating word counts per section
def get_word_counts(sections_dict):
    word_counts = {}
    for key, val in sections_dict.items():
        word_counts[key] = len(val.split())
    return word_counts


def main():
    # load API key from environment variables
    load_dotenv()

    # pass API key to initialize API client
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    # prompt Gemini and save Gemini's response to variable
    response = client.models.generate_content(
        # specifies model version to use - currently using older model due to timeouts with 2.0 version
        model = 'gemini-1.5-flash',
        contents = types.Content(
            parts = [
                types.Part(
                    # uses YouTube URL directly as per Gemini API documentation
                    file_data=types.FileData(file_uri='https://www.youtube.com/watch?v=Md3rdQssxxE')
                ),
                # passes prompt to Gemini for note generation
                types.Part(text='Generate a SOAP style psychotherapy note based on the contents of the video. Include a Mental Status Examination and Risk Assessment.'
                                'Use these headings:'
                                'Subjective: '
                                'Objective: '
                                'Assessment: '
                                'Plan: '
                                'Mental Status Examination: '
                                'Risk Assessment: '
                                ''
                                'Do not include any text such as disclaimers or therapist signatures following the end of the listed sections.'
                           )
            ]
        )
    )

    # #Print response to console
    # print(response.text)

    #Output note contents to a file for easier saving/copying
    with open('prompt1_response.txt', mode='w') as file:
        file.write(response.text)

    #Define sections expected to be found in note
    expected_sections = [
        "Subjective",
        "Objective",
        "Assessment",
        "Plan",
        "Mental Status Examination",
        "Risk Assessment"
    ]

    # Call function to separate section texts and save to variable
    text_sections = split_sections(response.text, expected_sections)

    print(f'Subjective: {text_sections['Subjective']}\n')
    print(f'Objective: {text_sections["Objective"]}\n')
    print(f'Assessment: {text_sections["Assessment"]}\n')
    print(f'Plan: {text_sections["Plan"]}\n')
    print(f'MSE: {text_sections["Mental Status Examination"]}\n')
    print(f'Risk Assessment: {text_sections["Risk Assessment"]}')

    # call function to get word count of each section and save to dictionary
    word_counts = get_word_counts(text_sections)
    print(f"Word Counts: {word_counts}\n")

if __name__ == '__main__':
    main()
