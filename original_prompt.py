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

def average_sentence_length(sections_dict, word_count_dict):
    """
    Calculates the average sentence length in the full note.

    :param sections_dict: dictionary containing section names as keys and section text as values
    :param word_count_dict: dictionary containing section header as key and word count as value
    :return: average number of words per sentence (in full note)
    """
    full_text = " ".join(sections_dict.values())
    sentences = re.split(r'[.!?]', full_text)
    sentences = [s.strip() for s in sentences]
    total_words = word_count_dict['Total']
    total_sentences = len(sentences)
    return round(total_words / total_sentences, 0)


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
                                ''
                                'Use the following headings and write content according to the associated guidelines for each section:'
                                'Subjective: Symptoms and related factors as described by patient. Include Chief Complaint or presenting problem.'
                                'Objective: Objective signs and symptoms observable by clinician, such as body language, affect, appearance, and speech rate and tone.'
                                'Assessment: Clinician\'s assessment of presenting problem and possible causes based on review of both subjective and objective data.'
                                'Plan: Plan for future evaluation and/or treatment for each presenting problem, including any recommendations for diagnostic tests, referrals to other providers, and recommendation for follow up with current provider.'
                                'Mental Status Examination: Review of client\'s current presentation according to standard Mental Status Examination components: Appearance, Behavior, Motor Activity, Speech, Mood, Affect, Thought Process, Thought Content, Perceptions, Cognition, Insight, and Judgment.'
                                'Risk Assessment: Brief evaluation of any indications that patient may be a risk to self or others, including mentions of suicidal thoughts or self-harming behaviors. Specifically note if no risks indicated at this time.'
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

    # Print sections to console for easy reference
    for key, value in text_sections.items():
        print(f'{key}:\n{value}')

    # Call functions to evaluate descriptive statistics
    word_counts = get_word_counts(text_sections)
    percentages = word_count_percentages(word_counts)
    avg_sent_length = average_sentence_length(text_sections, word_counts)

    # Print descriptive statistics to a file
    with open('prompt1_statistics.txt', mode='w') as file2:
        file2.write("Word Count per Section:\n")
        for key, value in word_counts.items():
            file2.write(f'{key}: {value}\n')
        file2.write("\n")
        file2.write("Percent of Total Word Count:\n")
        for key, value in percentages.items():
            file2.write(f'{key}: {value}%\n')
        file2.write("\n")
        file2.write(f"Average Number of Words per Sentence (in full text): {avg_sent_length}\n")


if __name__ == '__main__':
    main()
