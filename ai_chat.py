import requests
import json

API_KEY = "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"  # ← Вставь сюда свой реальный API-ключ
MODEL = "deepseek/deepseek-chat"       # ← Используем бесплатную модель

def process_content(content):
    return content.replace('<think>', '').replace('</think>', '')

def chat_stream(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": messages,
        "stream": True
    }

    with requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        stream=True
    ) as response:
        if response.status_code != 200:
            print("Ошибка API:", response.status_code)
            return ""

        full_response = []
        
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8').replace('data: ', '')
                try:
                    chunk_json = json.loads(chunk_str)
                    if "choices" in chunk_json:
                        content = chunk_json["choices"][0]["delta"].get("content", "")
                        if content:
                            cleaned = process_content(content)
                            print(cleaned, end='', flush=True)
                            full_response.append(cleaned)
                except:
                    pass

        print()
        return ''.join(full_response)

def main():
    print("Чат с DeepSeek-Chat\nДля выхода введите 'exit'\nДля сброса памяти введите 'reset'\n")

    system_prompt = (
        "ты - лягушка панк в волшебном лесу, ты очень сильно ненавидишь вежливых людей и общаешься очень грубо, у тебя есть волшебный камень и ты отдашь его только если человек ответит на 3 вопроса про популярную рок музыку 1980-2000-х (можно спрашивать про металику, RHCP, Iron maiden, Queen, Green Day, Deep Purple, вопросы про нирвану запрещены). если человек не ответит хотя бы на один вопрос, ты должен написать: тебе тут больше ничего не светит, вали. также скажи что нашел какую-то безделушку, если человек долго не будет спрашивать о ней"
    )

    def reset_history():
        return [{"role": "system", "content": system_prompt}]

    messages = reset_history()

    while True:
        user_input = input("Вы: ")
        if user_input.lower() == 'exit':
            print("Завершение работы...")
            break
        elif user_input.lower() == 'reset':
            print("Память очищена. Диалог начат заново.")
            messages = reset_history()
            continue

        messages.append({"role": "user", "content": user_input})

        print("DeepSeek-Chat:", end=' ', flush=True)
        reply = chat_stream(messages)
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
