# MS Teams Call Summarizer

This application uses Streamlit and GPT-3.5-turbo to summarize meeting transcripts in Microsoft Teams .vtt format.
It provides a summarized version of the conversation and a list of action items.

## Prerequisites

To run the application, you need:

- Python 3.6 or higher
- streamlit
- openai
- tiktoken

## Installation

1. Clone this repository:

git clone https://github.com/yahiakala/meeting-summarizer.git

cd meeting-summarizer


2. Install the required packages:

pip install -r requirements.txt


3. Create a `.streamlit` folder in the root directory of the project:
4. Create a `secrets.toml` file inside the `.streamlit` folder:

5. Add your OpenAI API key to the `secrets.toml` file:

[secrets]

OPENAI_API_KEY = "your_openai_api_key"

6. To ensure that the `.streamlit` folder is not added to version control, add the following line to your `.gitignore` file:

.streamlit/


## Running the Application

To run the application, use the following command:

streamlit run app.py

The application will start, and you can access it by navigating to the provided URL (usually `http://localhost:8501`).

Upload a Microsoft Teams .vtt transcript file, and the app will generate a meeting summary and a list of action items.

## License

This project is licensed under the MIT License.




