from openai import OpenAI
client = OpenAI(api_key='TODO')
def request_gpt4o(prompt, max_tokens, temperature=1.0):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )
    return completion.choices[0].message.content
