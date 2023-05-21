import feedparser
import re
from bs4 import BeautifulSoup
import openai
import gradio as gr
from urllib.parse import quote

openai.api_key = "APIkey"


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def get_urls(cleaned_text):
    url_pattern = re.compile(r'https?://\S+')
    urls = url_pattern.findall(cleaned_text)
    return urls

def ask_gpt_3_5_turbo(url, target_audience, cached_content):
    messages = [
        {"role": "system", "content": "You are Luna a Stoner AI Assistant, we live in Canada Toronto its 2023, you are part of Sesh Team, a community focus on teach AI to proffessionals and connect them with AI developers. You are so amazing good and you love working with the whole sesh community"},
        {"role": "user", "content": f"Yo yo luna Write a post about this URL: {url}"},
        {"role": "user", "content": f" but focus on this target audience: {target_audience}"},
        {"role": "assistant", "content": f" use this Cached content as context: {cached_content}"},
        {"role": "assistant", "content": f" Add a tittle to each one of the URL/Story/Posts  that you write"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    return response.choices[0].message['content']

def generate_posts(query, target_audience):
    encoded_query = quote(query)
    google_rss_url = f"https://news.google.com/rss/search?q={encoded_query}"
    feed = feedparser.parse(google_rss_url)
    
    post_text = ""
    search_term_lower = query.lower()
    for entry in feed.entries[-5:]:
        title = entry.title
        link = entry.link
        summary = entry.summary
        cleaned_title = clean_html(title)

        if search_term_lower not in cleaned_title.lower():
            continue

        cleaned_link = clean_html(link)
        urls = get_urls(cleaned_title + " " + cleaned_link)

        for url in urls:
            cached_content = clean_html(summary)
            post = ask_gpt_3_5_turbo(url, target_audience, cached_content)
            post_text += f"{post}\n"

    return post_text.strip()

input_query = gr.inputs.Textbox(placeholder="Enter your query (e.g., AI)")
input_target_audience = gr.inputs.Textbox(placeholder="Enter your target audience (e.g., Developers)")

output_posts = gr.outputs.Textbox()

interface = gr.Interface(
    fn=generate_posts,
    inputs=[input_query, input_target_audience],
    outputs=output_posts,
    title="AI News Post Generator",
    description="Enter a query to search for news articles and specify a target audience, then generate a post for each URL using GPT-3.5 Turbo. The cached content of the search results will be sent as additional context.",
    examples=[["AI", "Developers"], ["Machine Learning", "Data Scientists"]]
)

interface.launch(share=True)