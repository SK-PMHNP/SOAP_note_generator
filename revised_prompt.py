#import packages
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

from original_prompt import split_sections, get_word_counts, word_count_percentages, average_sentence_length


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
                                'Sections should include "Subjective", "Objective", "Assessment", "Plan", "Mental Status Examination", and "Risk Assessment" using these headings.'
                                'Each section should include content following the associated guidelines, but may vary based on the contents of the video session.'
                                ''
                                'Header: Subjective'
                                'Content: Symptoms and related factors as described by patient.' 
                                'Include presenting problem, or Chief Complaint if patient provides a clear quote stating primary reason for visit. If visit is noted as a follow up from a prior appointment, state this.'
                                'Include brief notes about relevant history and present circumstances contributing to present primary symptoms.'
                                'Include 2 to 3 relevant direct quotes by the patient; relevant quotes may include strong emotion words or \'I feel\' statements.'
                                ''
                                'Header: Objective'
                                'Content: Objective signs and symptoms observable by clinician, such as body language, appearance, and emotional displays (e.g., tearfulness).'
                                ''
                                'Header: Assessment'
                                'Content: Clinician\'s assessment of presenting problem and possible causes based on review of both subjective and objective data.'
                                'If appropriate, include differential diagnoses with a brief description of rationale supporting these diagnoses.'
                                ''
                                'Header: Plan'
                                'Content: Plan for future evaluation and/or treatment for each presenting problem.' 
                                'Must include plan for follow up schedule (either ongoing, e.g. "weekly", or for next visit, e.g., "in one week".'
                                'Specifically note any topics that therapist states will be discussed in a future appointment.'
                                'Include any applicable recommendations for diagnostic tests or referrals to other providers.'
                                'May include plans for therapeutic approaches to use in follow up visits.'
                                ''
                                'Header: Mental Status Examination'
                                'Content: Review of client\'s current presentation according to standard Mental Status Examination components: Appearance, Behavior, Motor Activity, Speech, Mood, Affect, Thought Process, Thought Content, Perceptions, Cognition, Insight, and Judgment.'
                                'Provide only a brief statement for each criterion that is within normal limits. Statement may be slightly longer for criteria in which abnormalities are noted.'
                                ''
                                'Header: Risk Assessment'
                                'Content: Brief evaluation of any indications that patient may be a risk to self or others, including mentions of suicidal thoughts or self-harming behaviors. Specifically note if no risks indicated at this time.'
                                'If no risks are noted at this time, this section should be very brief and requires no speculation about future changes.'
                                'If risks are noted, include brief discussion of safety interventions performed or offered.'
                                ''
                                'Do not include any text such as disclaimers or therapist signatures following the end of the listed sections.'
                           )
            ]
        )
    )

    #Output note contents to a file for easier saving/copying
    with open('prompt2_response.txt', mode='w') as file:
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
    with open('prompt2_statistics.txt', mode='w') as file2:
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