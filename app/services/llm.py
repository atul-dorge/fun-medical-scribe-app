from openai import AsyncOpenAI

class ChatGPT():

    def __init__(self, api_key, key="gpt-3.5-turbo"):
        self.aclient = AsyncOpenAI(api_key=api_key)
        self.key = key

    async def get_llm_response(self, prompt, **kwargs):
        if 'model' in kwargs:
            model = kwargs['model']
        else:
            model = self.key

        if 'messages' in kwargs:
            messages = kwargs['messages']
        else:
            messages = [{"role": "user", "content": prompt}]

        if 'temperature' in kwargs:
            temperature = kwargs['temperature']
        else:
            temperature = 0

        response = await self._get_llm_response(model, messages, temperature)
        return response.choices[0].message.content, response.usage.total_tokens
        # return response.choices[0].message.content, response.usage.prompt_tokens, response.usage.completion_tokens

    async def _get_llm_response(self, model, messages, temperature):
        return await self.aclient.chat.completions.create(model=model,
        messages=messages,
        temperature=temperature)