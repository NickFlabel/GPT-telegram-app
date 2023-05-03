import aiohttp
import dotenv
import os

dotenv.load_dotenv()

DB_API_URL = os.getenv('DB_API_URL')


async def save_prompt(prompt: str, user_id: int):
    async with aiohttp.ClientSession(base_url=DB_API_URL) as session:
        async with session.post('/dialogs', json={
            'user_id': user_id,
            'content': prompt,
            'role': 'user'
        }) as resp:
            await resp.read()
            if resp.status == 201:
                return True
            else:
                return False
            

async def save_response(response: str, user_id: int):
    async with aiohttp.ClientSession(base_url=DB_API_URL) as session:
        async with session.post('/dialogs', json={
            'user_id': user_id,
            'content': response,
            'role': 'assistant'
        }) as resp:
            await resp.read()
            if resp.status == 201:
                return True
            else:
                return False
            

async def get_dialog(user_id: int):
    async with aiohttp.ClientSession(base_url=DB_API_URL) as session:
        async with session.get(f'/dialogs?user_id={user_id}') as resp:
            data = await resp.text()
            if resp.status == 200:
                return data
            else:
                return False
            

async def get_or_create_user(user_id: int, first_name: str, last_name: str, username: str):
    async with aiohttp.ClientSession(base_url=DB_API_URL) as session:
        async with session.get(f'/users/{user_id}') as resp:
            if resp.status == 404:
                payload = {
                    'id': user_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username
                }
                async with session.post('/users', json=payload) as res:
                    data = await res.text()
            else:
                data = await resp.text()
    return data
            