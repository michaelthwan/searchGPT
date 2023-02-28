import openai

# openai.organization = ""
openai.api_key = ""
# print(openai.Model.list())

# GPT-3
# text-davinci-003  $0.0200  /1K tokens
# text-curie-001    $0.0020  /1K tokens
# text-babbage-001  $0.0005  /1K tokens
# text-ada-001      $0.0004  /1K tokens

# Codex
# code-davinci-002
# code-cushman-001

response = openai.Completion.create(
    # model="text-curie-001",
    model="text-babbage-001",
    prompt="Say this is a test",
    max_tokens=16,
    temperature=0 # default=1
)

for r in response.choices:
    print(r.text)
