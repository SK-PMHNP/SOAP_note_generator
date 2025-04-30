#import packages
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import re


#Define a function for splitting note by section for analysis
def split_sections(full_response, sections):
    """
    Splits full clinical note into specified note sections.

    :param full_response: variable containing full text of AI's generated note
    :param sections: list containing strings of section header names
    :return: dictionary with section headers as keys and section content as values
    """
    # Define regex pattern for separating sections
    pattern = r'\b(?:' + '|'.join(re.escape(section) for section in sections) + r')\b'

    # Find match objects in text
    matches = list(re.finditer(pattern, full_response))

    # loop through match objects and decare end to be start of next match object, add text of each section to dictionary
    separated_sections = {}
    for i in range(len(matches)):
        start = matches[i].end()
        header = matches[i].group(0).strip().title()
        if i + 1 < len(matches):
            end = matches[i+1].start()
        else:
            end = len(full_response)
        # remove decorative formatting symbols
        content = re.sub(r'^[\s*\-]+', '', full_response[start:end].strip(':*'))
        separated_sections[header] = content
    return separated_sections


def get_word_counts(sections_dict):
    """
    Counts the number of words in each section of the SOAP note.

    :param sections_dict: dictionary containing section names as keys and section text as values
    :return: dictionary with section header as key and word count as value
    """
    word_counts = {}
    for key, val in sections_dict.items():
        word_counts[key] = len(val.split())
    total_word_count = sum(word_counts.values())
    word_counts['Total'] = total_word_count
    return word_counts


def word_count_percentages(word_count_dict):
    """
    Calculates the percentage of total word count represented by each section

    :param word_count_dict: dictionary containing section header as key and word count as value
    :return: dictionary with section header as key and percent of total word count as value
    """
    total_word_count = word_count_dict['Total']
    word_count_percentages = {}
    for key, val in word_count_dict.items():
        if key != 'Total':
            word_count_percentages[key] = round(100*(word_count_dict[key] / total_word_count), 1)
    return word_count_percentages


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

    for key, value in text_sections.items():
        print(f'{key}: {value}')

    # call function to get word count of each section and save to dictionary
    word_counts = get_word_counts(text_sections)

    percentages = word_count_percentages(word_counts)

    with open('prompt1_evaluation.txt', mode='w') as file2:
        file2.write("Word Count per Section:\n")
        for key, value in word_counts.items():
            file2.write(f'{key}: {value}\n')
        file2.write("\n")
        file2.write("Percent of Total Word Count:\n")
        for key, value in percentages.items():
            file2.write(f'{key}: {value}%\n')




if __name__ == '__main__':
    main()
