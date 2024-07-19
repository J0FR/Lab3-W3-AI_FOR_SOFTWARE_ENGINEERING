import os
from newsapi import NewsApiClient

news_key = os.getenv("API_KEY_NEWS")

newsapi = NewsApiClient(api_key=news_key)

articles_response = newsapi.get_everything(q='Artificial Intelligence', language='en')

articles = articles_response['articles']

article_summaries = []
for article in articles:
    title = article['title']
    description = article['description']
    content = article['content']
    
    summary = f"Title: {title}\nDescription: {description}\nContent: {content}\n"
    article_summaries.append(summary)

article_content = "\n".join(article_summaries)

from autogen import UserProxyAgent, ConversableAgent, GroupChat, GroupChatManager

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
    system_message="Plan the overall structure of the article and based on the feedback received tell the writer which changes to make.",
    description="Planner. Given a article, determine what information is needed to complete the task. After each step is done by others, check the progress and instruct the remaining steps",
    llm_config=llm_config,
)

writer = ConversableAgent(
    name="Writer",
    llm_config=llm_config,
    system_message="You are a writer. You write engaging and concise "
        "article on given topics. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments."
        "This is the articles information: " + article_content,
    description="Writer. Write an article based on the information provided and take feedback from the admin to refine the article."
)

critic = ConversableAgent(
    name="Critic",
    llm_config=llm_config,
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive "
                "feedback to help improve the quality of the content.",
    description="Critic. Review the written content and provide constructive feedback for improvement."
)

groupchat = GroupChat(
    agents=[user_proxy, planner, writer, critic],
    messages=[],
    max_round=10,
    allowed_or_disallowed_speaker_transitions={
        user_proxy: [planner],
        planner: [writer],
        writer: [critic],
        critic: [planner],
    },
    speaker_transitions_type="allowed",
)

manager = GroupChatManager(
    groupchat=groupchat, llm_config=llm_config
)

# Initialize the chat with the task
task = f"Summarize the following AI related news articles into a cohesive article based on the following news: " + article_content 
groupchat_result = user_proxy.initiate_chat(
    manager,
    message=task,
)

# Print the result
print(groupchat_result)
