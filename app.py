import streamlit as st
import openai
import json

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

system_msg = [{'role': 'system', 'content': """
You are a meeting minute taker. You accept meeting minutes in the following format:

<Start Time> --> <Stop Time> <v Person's name>Things they say</v>

You will answer the following questions:

1. What are the biggest pain points for Adam and Kevin? If there are none, respond with 'NA'.
2. What features did Adam and Kevin request or want? List all of them in detail. If there are none, respond with 'NA'.
3. What are the action items for each person in the meeting? If there are none, respond with 'NA'.

Use the following format:
{"Q1": "<Answer>", "Q2": "<Answer>", "Q3": "<Answer>"}
"""}]



def read_vtt_file(file):
    content = file.read().decode("utf-8")
    return content.strip()

def split_into_entries(content):
    entries = content.split('</v>')
    entries = [entry.strip() + '</v>' for entry in entries[:-1]]
    return entries

def split_into_chunks(entries, max_tokens=4096):
    chunks = []
    current_chunk = []
    current_tokens = 0

    for entry in entries:
        tokens = len(entry)
        if current_tokens + tokens > max_tokens:
            chunks.append("\n".join(current_chunk))
            current_chunk = [entry]
            current_tokens = tokens
        else:
            current_chunk.append(entry)
            current_tokens += tokens

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


st.title("ChatGPT VTT File Processor")
st.write("Upload a .vtt file and get a ChatGPT response.")

uploaded_file = st.file_uploader("Choose a .vtt file", type="vtt")

if uploaded_file is not None:
    vtt_content = read_vtt_file(uploaded_file)
    st.write("VTT content extracted.")

    st.write("Splitting content into entries...")
    entries = split_into_entries(vtt_content)
    st.write("Entries : ", len(entries))
    # st.write(entries[1])
    # st.write('--')
    # st.write(entries[2])
    # st.write('--')
    # st.write(entries[3])

    st.write("Splitting entries into chunks...")
    chunks = split_into_chunks(entries[1:])
    st.write("Chunks : ", len(chunks))

    st.write("Generating ChatGPT response...")
    chatgpt_responses = []
    chatgpt_resp_dicts = []

    # cnt = 0
    # for chunk in chunks:
    #     cnt += 1
    #     messages = [{'role': 'user', 'content': chunk}]
    #     response = get_completion_from_messages(system_msg + messages)
    #     chatgpt_responses.append(response)
    #     st.write('Chunk: ', cnt, ' of ', len(chunks))
    #     st.write(response)
    #     chatgpt_resp_dicts.append(json.loads(response))
    
    chatgpt_resp_dicts = [
        {"Q1": "Adam's biggest pain points are the lack of communication from CMIC when there are issues and the limited options for aesthetics in financial statements. Kevin's pain point is not mentioned in the given meeting minutes.", "Q2": "Adam and Kevin requested or wanted the following features: \n- Clear communication from CMIC when there are issues and workarounds\n- More options for aesthetics in financial statements, such as separate columns, font size changes, and color additions", "Q3": "There are no action items mentioned in the given meeting minutes."},
        {"Q1": "The biggest pain points for Adam and Kevin are the lack of communication and the slow printing process.", "Q2": "Adam and Kevin requested or wanted a fix for the slow printing process, better communication regarding updates and fixes, and a dashboard or table with formatting and coloring options for CMIC analytics.", "Q3": "Action items for each person in the meeting are not clear from the given transcript."},
        {"Q1": "The biggest pain points for Adam and Kevin are missing important emails and the lack of flexibility in formatting financial statements.", "Q2": "Adam and Kevin requested or wanted the following features: 1) Ability to receive important emails, 2) More flexibility in formatting financial statements, including different fonts, bolding, and colors, 3) BI functionality to display data in charts and do calculations.", "Q3": "Action items for each person: Adam wants to receive important emails and is looking for more flexibility in formatting financial statements. Kevin will ensure that Adam is added to the email list and will look into finding the missing email. Yahia Kala will explore BI functionality and note Adam's request for bolding and italics."},
        {"Q1": "Adam's pain points are having limited font options and the inability to modify financial statements easily. Kevin's pain point is not being able to easily compare financial statements from different periods.", "Q2": "Adam and Kevin want bold and italic font options, different font options, and the ability to modify financial statements more easily. They also want the ability to compare financial statements from different periods more easily.", "Q3": "Adam's action item is to provide more specific details on the modifications he wants for financial statements. Kevin's action item is to provide more specific details on the features he wants for comparing financial statements from different periods."},
        {"Q1": "Adam's biggest pain point is having to manually choose the consolidation code for each financial document, while Kevin's biggest pain point is not knowing how to import the data into BI or create a new dashboard query.", "Q2": "Adam and Kevin both requested the ability to choose the consolidation code at runtime, and for the BI integration to have better functionality in a future patch. Adam also asked for training on how to use the BI functionality.", "Q3": "Adam's action item is to provide a list of the 25 different consolidation codes needed, while Kevin's action item is to explore the manual process of bringing the data into BI until better functionality is available in a future patch."},
        {"Q1": "The biggest pain points for Adam and Kevin are not being able to automate the process and having to manually add tables to the General Ledger folder.", "Q2": "The features that Adam and Kevin requested or wanted are not explicitly stated in the given meeting minutes.", "Q3": "There are no action items for each person in the meeting explicitly stated in the given meeting minutes."},
        {"Q1": "There is no clear indication of pain points for Adam and Kevin in this meeting.", "Q2": "Adam and Kevin did not request any features in this meeting.", "Q3": "There are no clear action items for Adam and Kevin in this meeting."},
        {"Q1": "Adam's biggest pain point is the inability to indent columns right. There is no clear pain point mentioned for Kevin.", "Q2": "Adam wants the ability to indent columns right. Kevin requests for help with linking a table view and asks about new features in BI, including improved dashboards and more types of charts.", "Q3": "Action items for Adam: Send Yahia Kala a visual example of the indentation piece. \nAction items for Kevin: Link the table view correctly and explore new features in BI, including improved dashboards and more types of charts."},
        {"Q1": "There is no clear indication of pain points for Adam and Kevin in this meeting.", "Q2": "Adam and Kevin did not request any features in this meeting.", "Q3": "There are no clear action items for Adam and Kevin in this meeting."},
        {"Q1": "The biggest pain points for Adam and Kevin are understanding the structure of the financial document and how to match the columns in the BI query to the correct data in the financial document.", "Q2": "Adam and Kevin requested or wanted the following features: a way to manually check which columns in the financial document correspond to the columns in the BI query, a page filter to select a specific document code and fiscal year/fiscal period, and a way to break down the data by department.", "Q3": "The action items for Adam and Kevin are to manually check the columns in the financial document to match them to the BI query, implement a page filter to select a specific document code and fiscal year/fiscal period, and figure out how to break down the data by department."},
        {"Q1": "The biggest pain points for Adam and Kevin are understanding how the consolidation code works and how to filter data in BI based on specific criteria.", "Q2": "Features requested or wanted include the ability to filter data in BI based on consolidation code and other criteria, a quick rundown of what the sequence number means, and the ability to change consolidation codes in BI.", "Q3": "Action items for Adam and Kevin are not specified in the given meeting minutes."},
        {"Q1": "The biggest pain points for Adam and Kevin are the manual creation of BI queries for each financial document and the difficulty in joining tables to get the department code.", "Q2": "The features that Adam and Kevin requested or wanted are: automation between financial documents and BI, the ability to do a join where they can just say, give me a department code, separate BI queries for each financial document, and the ability to add colors and make the presentation of the data more presentable.", "Q3": "The action items for each person in the meeting are not explicitly stated in the given meeting minutes."},
        {"Q1": "Adam and Kevin's pain points are not explicitly stated in the meeting minutes.", "Q2": "Kevin requested a project health dashboard that shows where his project stands on a daily basis. He also wants a collaborative dashboard with two versions - an owner version and a GCC version. Adam did not request any features.", "Q3": "Action items for Kevin: provide feedback on CBI, test CBI, and continue to use CBI. Action items for Yahia Kala: work on collaboration functionality using Project Gateway and P type users, increase adoption of BI in those contexts, and implement a project health dashboard in Patch 17."},
        {"Q1": "Adam and Kevin's biggest pain points are related to project health and profitability tracking. They want to be able to see real-time data and have access to dashboards that are customizable to their needs.", "Q2": "Adam and Kevin requested or want the following features: \n- Out-of-the-box dashboards related to owners and subcontractors\n- Generic project health dashboard with the ability to add or remove information\n- Real-time data tracking for profitability and project health\n- Customizable dashboards for different levels of the organization (project, business unit, enterprise)\n- Interactive CEO dashboard with period-to-period basis tracking of profitability\n", "Q3": "Action items for each person in the meeting are not specified in the given meeting minutes."},
        {"Q1": "It is not clear from the conversation what the pain points for Adam and Kevin are.", "Q2": "Kevin wants a feature called 'owners app' that allows for collaboration and messaging through the app. He also wants BI to work on the app and for it to be real-time. Adam did not request any specific features.", "Q3": "Action items for Yahia Kala: Send Kevin an invite to the meeting schedule and provide him with Adam's email. Action items for Kevin: None mentioned in the conversation. Action items for Adam: None mentioned in the conversation."},
        {"Q1": "The biggest pain points for Adam and Kevin are not having an internal chat communication system and struggling with creating new calculations and columns in CBI.", "Q2": "The features that Adam and Kevin requested or wanted are:\n- An internal chat communication system\n- An issue or task creation feature\n- A way to easily track assigned tasks\n- More powerful features\n- Help with creating new calculations and columns in CBI", "Q3": "The action items for each person in the meeting are not explicitly stated in the given meeting minutes."},
        {"Q1": "There is no mention of pain points for Adam and Kevin in these meeting minutes.", "Q2": "There is no mention of any specific features that Adam and Kevin requested or wanted.", "Q3": "There are no action items mentioned in these meeting minutes."}
    ]

    qstr = ['What are the biggest pain points for Adam and Kevin?',
            'What features did Adam and Kevin request or want? List all of them in detail.',
            'What are the action items for each person in the meeting?']
    
    final_resp_txt = ''
    for i, j in zip(['Q1', 'Q2', 'Q3'], qstr):
        final_resp_txt += '\n\nQuestion: ' + j + '\n\n'
        for resp in chatgpt_resp_dicts:
            final_resp_txt += '\n' + resp[i]

    # st.write(final_resp_txt)
    responses_msg = [{'role': 'user', 'content': final_resp_txt}]
    
    prompt = """
    Your task is to summarize answers to questions compiled from multiple people.
    
    Summarize the answers to the three questions in the provided text at the bottom.

    Use at most 100 words for each answer.

    Use the following format:
    Question
    <Answer>

    Question
    <Answer>

    Question
    <Answer>

    Provided Text:
    """ + final_resp_txt
    
    compiling_msg = [{'role': 'user', 'content': prompt}]
    
    st.write('ChatGPT Final Response:')
    st.write(prompt)
    # resp_final = get_completion_from_messages(compiling_msg)
    # st.write(resp_final)


