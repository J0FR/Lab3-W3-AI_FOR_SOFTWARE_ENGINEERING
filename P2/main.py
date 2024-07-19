import os
from newsapi import NewsApiClient
from autogen import UserProxyAgent, ConversableAgent, GroupChat, GroupChatManager

# Define News API key
news_key = os.getenv("API_KEY_NEWS")

# Initialize NewsApiClient with your API key
newsapi = NewsApiClient(api_key=news_key)

# Fetch articles related to Artificial Intelligence
articles_response = newsapi.get_everything(q='Artificial Intelligence', language='en')

# Extract articles from the response
articles = articles_response['articles']

# Collecting relevant information from articles
article_summaries = []
for article in articles:
    title = article['title']
    description = article['description']
    content = article['content']
    
    # Simulate summarization (you may use NLP techniques for actual summarization)
    summary = f"Title: {title}\nDescription: {description}\nContent: {content}\n"
    article_summaries.append(summary)

# Ask the GroupChat to collaborate on writing an article
article_title = "Summary of AI Related News"
article_content = "\n".join(article_summaries)

# Initialize the agents
gemini_api_key = os.getenv("API_KEY")
llm_config = {
  "model": "gemini-1.5-flash-latest",
  "api_key": gemini_api_key,
  "api_type": "google"
}

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="Give the task, and send instructions to writer to refine the article.",
    code_execution_config=False,
    llm_config=llm_config,
    human_input_mode="ALWAYS",
)

planner = ConversableAgent(
    name="Planner",
    system_message="Given a task, please determine what information is needed to complete the task. After each step is done by others, check the progress and instruct the remaining steps. If a step fails, try to workaround.",
    description="Planner. Given a task, determine what information is needed to complete the task. After each step is done by others, check the progress and instruct the remaining steps",
    llm_config=llm_config,
)

writer = ConversableAgent(
    name="Writer",
    llm_config=llm_config,
    system_message="You are a writer. You write engaging and concise "
        "blogpost (with title) on given topics. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments.",
    description="Writer. Write articles based on the information provided and take feedback from the admin to refine the article."
)

critic = ConversableAgent(
    name="Critic",
    llm_config=llm_config,
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive "
                "feedback to help improve the quality of the content.",
    description="Critic. Review the written content and provide constructive feedback for improvement."
)

# Define the group chat structure
groupchat = GroupChat(
    agents=[user_proxy, planner, writer, critic],
    messages=[],
    max_round=10,
    allowed_or_disallowed_speaker_transitions={
        user_proxy: [planner],
        planner: [writer, critic],
        writer: [critic, planner],
        critic: [planner, writer],
    },
    speaker_transitions_type="allowed",
)

manager = GroupChatManager(
    groupchat=groupchat, llm_config=llm_config
)

# Initialize the chat with the task
task = f"Write an article summarizing the following AI related news (an article around all the joining all the summaries):\n{article_content}"
groupchat_result = user_proxy.initiate_chat(
    manager,
    message=task,
)

# Print the result
print(groupchat_result)
