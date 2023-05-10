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

    task1 = summary_msg + [{'role': 'user', 'content': chatgpt_responses_txt}]
    task2 = action_item_msg + [{'role': 'user', 'content': chatgpt_responses_txt}]

    st.write("# Meeting Summary")
    resp1 = get_completion_from_messages(task1)
    st.write(resp1)
    st.write("# Action Items")
    resp2 = get_completion_from_messages(task2)
    st.write(resp2)


