from hugchat import hugchat
from hugchat.login import Login


email = "mihorag447@vikinoko.com"
passwd = "IamstewpedW!23@"
# Log in to huggingface and grant authorization to huggingchat
sign = Login(email, passwd)
cookies = sign.login()

# # Save cookies to the local directory
cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)

# Load cookies when you restart your program:
# sign = login(email, None)
cookies = sign.loadCookiesFromDir(cookie_path_dir)


# Create a ChatBot
chatbot = hugchat.ChatBot(
    cookies=cookies.get_dict(),
    system_prompt="You are an amazing youtuber. A true creative master genius",
)

model_index = 0
models = chatbot.get_available_llm_models()
print(chatbot.active_model)
if not chatbot.active_model.name == "CohereForAI/c4ai-command-r-plus":
    for model in models:
        print(model.name, "switching..")
        if model.name == "CohereForAI/c4ai-command-r-plus":
            model_index = models.index(model)
            break
print(chatbot.current_conversation.system_prompt)
chatbot.switch_llm(model_index)
