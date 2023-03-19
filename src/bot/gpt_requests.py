import os
import requests
import json


def send_prompt(api_key: str, system_message: str, prompt_message: str) -> tuple:

    headers = {
        'Authorization': 'Bearer ' + api_key,
        'Content-Type': 'application/json',
    }

    json_data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'system',
                'content': system_message
            },
            {
                'role': 'user',
                'content': prompt_message
            }
        ]
    }
    response_data = json.loads(requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data).text)
    tokens_used = int(response_data['usage']['total_tokens'])
    ai_response = [str(response_data['choices'][0]['message']['content']).replace('\n\n', '')]

    if len(ai_response[0]) > 2000:
        ai_response_list = []
        split_iter = 0
        splits = int(len(ai_response[0]) / 2001)

        for x in range(splits):
            ai_response_list.append(ai_response[0][split_iter: split_iter + 2000])
            split_iter += 2000
        ai_response = ai_response_list

    return tokens_used, ai_response
