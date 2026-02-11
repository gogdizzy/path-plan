import os
import dashscope
from dashscope import Generation

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
dashscope.base_url = os.getenv("DASHSCOPE_BASE_URL")

def chat_example():
    messages = [
        {'role': 'system', 'content': '你是一个资深C++工程师，擅长解答各种技术问题。'},
        {'role': 'user', 'content': '''
Which function would the compiler select when resolving `blast(ast, 100)` if two options exist: a non-template `galaxy::blast(Asteroid&, int)` and a template `template<typename T> void blast(T, int)`? Why?

## additional_instructions:
Generate extremely difficult multiple-choice questions that challenge even experienced C++ developers.

## choices:

(A) The template function, as integer arguments match better
(B) Compilation fails with ambiguous overload
(C) The non-template, due to tiebreaker between non-template and template
(D) The template function, because templates get priority in ADL

别的不用说，只回答选项就可以'''}
    ]

    response = Generation.call(
        model='deepseek-v3',
        messages=messages,  # 使用messages而不是prompt
        parameters={
            'temperature': 0.7,
            'top_p': 0.8,
            'max_tokens': 800,
            'presence_penalty': 0.1,
            'frequency_penalty': 0.1,
        }
    )

    if response.status_code == 200:
        print("对话结果:")
        # print(response.output.choices[0]['message']['content'])
        print(response)


chat_example()