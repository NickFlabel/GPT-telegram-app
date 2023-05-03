import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()

api_key = os.getenv('OPEN_AI_KEY')


async def get_answer_from_gpt_3_5(prompt, messages):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    messages.append({'role': 'user', 'content': prompt})
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': messages
    }
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post('https://api.openai.com/v1/chat/completions',
                                headers=headers,
                                json=payload) as resp:
            if resp.status == 200:
                answer = await resp.text()
                answer = json.loads(answer)
                answer = answer['choices'][0]['message']['content']
            else:
                answer = 'Произошла ошибка'
                print(await resp.text())

    return answer


async def get_dalle_image(prompt):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'prompt': prompt,
        'n': 1,
        'size': '1024x1024'
    }
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post('https://api.openai.com/v1/images/generations',
                                headers=headers,
                                json=payload) as resp:
            if resp.status == 200:
                answer = await resp.text()
                answer = json.loads(answer)
                answer = answer['data'][0]['url']
            else:
                answer = 'Произошла ошибка'

    return answer