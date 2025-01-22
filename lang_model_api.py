from uploader import workflow
from openai import OpenAI
client = OpenAI()

with open('editor_prompt.txt', 'r', encoding='utf-8') as file:
    context = file.read()

if workflow == 'editor':
    editor_account = input("Account: ")
    user_input = input("Prompt: ")
else:
    pass


def gpt_runner():

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (f"{context} {user_input}")
            }
        ]
    )

    gpt_output = completion.choices[0].message.content

    gpt_output_dict = {}
    gpt_output_dict = eval(gpt_output)

    global gpt_master_config
    global gpt_a_config
    global gpt_b_config
    global gpt_c_config
    global gpt_d_config

    gpt_master_config = gpt_output_dict['master_config']
    gpt_a_config = gpt_output_dict['a_config']
    gpt_b_config = gpt_output_dict['b_config']
    gpt_c_config = gpt_output_dict['c_config']
    gpt_d_config = gpt_output_dict['d_config']

if workflow == "editor":
    gpt_runner()