import streamlit as st
import openai
import tiktoken

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# openai.api_key = OPENAI_API_KEY

summary_msg = [{'role': 'system', 'content': """
Summarize the text in 500 words.
"""}]

action_item_msg = [{'role': 'system', 'content': """
Summarize the action items in the provided text in a bulleted list.
"""}]


def num_tokens(text: str, model: str = 'gpt-3.5-turbo') -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


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
        tokens = num_tokens(entry)
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


st.title("MS Teams Call Summarizer")
st.write("Upload a .vtt file (Teams Transcript file).")

uploaded_file = st.file_uploader("Choose a .vtt file", type="vtt")

if uploaded_file is not None:
    vtt_content = read_vtt_file(uploaded_file)
    st.write("VTT content extracted.")

    st.write("Splitting content into entries...")
    entries = split_into_entries(vtt_content)
    st.write("Entries : ", len(entries))
    st.write("Combining entries into chunks...")
    
    max_tokens = 3900
    chunks = split_into_chunks(entries[1:], max_tokens)
    num_words = int(max_tokens / len(chunks))
    # st.write(f'Chunks will be summarized into {num_words} words')

    chunking_msg = [{'role': 'system', 'content': f"""
    You are a meeting minute summarizer. You accept meeting minutes in the following format:

    <Start Time> --> <Stop Time> <v Person's name>Things they say</v>

    Summarize the text, focusing on action items. Use at most {num_words} words.
    """}]
    print(chunking_msg)

    
    st.write("Chunks : ", len(chunks))

    st.write("Generating Summary and Action Items...")
    chatgpt_responses = []

    cnt = 0
    for chunk in chunks:
        cnt += 1
        messages = [{'role': 'user', 'content': chunk}]
        response = get_completion_from_messages(chunking_msg + messages)
        chatgpt_responses.append(response)
        st.write('Chunk: ', cnt, ' of ', len(chunks))
        # st.write(response)
    
    chatgpt_responses_txt = '\n\n'.join(chatgpt_responses)

    # chatgpt_responses_txt = """
    # The team discussed the use of GPT for documentation and the progress made on financial tasks. They agreed on two phases, with phase one including tasks such as the print button and populating beyond I. The team also discussed the train structure and the need for UI runtime to dynamically launch BI queries or dashboards. They targeted patch 20 for completion of phase one and acknowledged that phase two may not be completed before Connect. The team agreed to continue working on phase two regardless.

    # During the meeting, the team discussed various topics related to the FDF BI integration project. They talked about identifying row types and building logic around conditional formatting of any row that says total on it. They also discussed the redesigning of some things and consolidation code, as well as new views for cash flow and job cost. The team also talked about the deprecation of the printing functionality and the addition of a new option for processing without print. They also discussed the sending of reports to BI and the limitations of the Excel renderer. The team agreed that they need to have separate options for printing and processing reports.

    # The team discussed the need for a print button and a process button for analytics. They also talked about the different print options available and how they don't all have overlapping functionality. Customers want formatting options like single and double underlines, but these don't make sense in BI. The team plans to consolidate all print options into one tool and replace the spiria output with a drilling function. They also plan to improve the output and allow for font and header/footer changes. The view button for MIP may be left in place if customers need it.

    # During the meeting, Yahia Kala provided updates on various projects. Gord Rawlins discussed the first phase of a project and assured Yahia that nothing was going away. Yahia also mentioned that a customer was interested in BI and drill downs. Justin Pham provided an update on the analytics for construct apps and mentioned that the Flutter team was finalizing some outstanding items. Yahia also discussed the FDF project and asked Justin about the progress. Justin explained that he was building a web service to generate a BI query and replace it if it already existed. Gord raised concerns about losing customized BI queries, but Justin suggested updating the query instead of

    # The team discussed the issue of updating analytics and potentially losing user-defined fields and calculated columns. They talked about the possibility of renaming columns instead of deleting and recreating them, but ultimately decided that it would be best to prompt users to save a copy of their customizations before updating analytics. They also discussed the fact that not all changes affect BI and that only changes to dependent data should result in the loss of calculated columns. The team also reviewed a script for creating calculated columns and discussed the power of being able to make calculations based on subtotals. Finally, they talked about the importance of keeping the names of columns consistent to avoid losing calculated columns.

    # During the meeting, the team discussed changes to the OR and calculated columns. They debated whether or not to erase existing data and how to warn users of potential data loss. They also discussed the various customization options available to users, including creating new calculated fields and adding descriptions to columns. The team ultimately decided to add a warning message when updating analytics and only erase data if the user confirms. They acknowledged that the warning message would appear every time the user updates analytics, but felt it was necessary to prevent accidental data loss.

    # During the meeting, the team discussed the issue of preserving financial document format (FDF) code when making changes to the document. They agreed that if someone does a "save as" of the document, it should break the link to the original FDF code. The team also discussed how to identify if a business intelligence (BI) query belongs to a specific FDF document, and they decided to use an additional attribute called FDF code. They also discussed the possibility of linking multiple BI queries to the same FDF document to create a dashboard. However, the team did not agree on this approach, as it would make the process more complicated. They also discussed the

    # During the meeting, the team discussed the auto-creation of documents and the use of FDF document codes. Rastislav suggested that the document code was not enough and that they would need to expose the link and present all the queries linked with that document type. However, Gord thought that this was overkill and that they only needed to be able to render documents. Yahia suggested an idea that would not require overcomplicating things and still allow them to achieve the functionality they needed in the future. They would keep the current attribute of FDF, document code, for each BI report, and the auto-creation

    # During the meeting, Justin Pham brought up an issue with the app's search function. He explained that when searching for a dashboard, they currently only have a document code and cannot determine if a dashboard exists. He suggested that they need to have the folder ID that the dashboard is using to ensure they can find it. Gord Rawlins clarified that they only have one dashboard, but Yahia Kala mentioned that it's possible to have multiple dashboards due to changes or configuration. They agreed to keep the search function as is for now and figure out a solution offline.
    # """

    task1 = summary_msg + [{'role': 'user', 'content': chatgpt_responses_txt}]
    task2 = action_item_msg + [{'role': 'user', 'content': chatgpt_responses_txt}]

    st.write("# Meeting Summary")
    resp1 = get_completion_from_messages(task1)
    st.write(resp1)
    st.write("# Action Items")
    resp2 = get_completion_from_messages(task2)
    st.write(resp2)


