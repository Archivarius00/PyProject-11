import requests
import json

API_KEY = "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"
MODEL = "deepseek/deepseek-r1"

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
    print("Чат с DeepSeek-R1\nДля выхода введите 'exit'\nДля сброса памяти введите 'reset'\n")

    system_prompt = (
        "ты - лягушка панк в волшебном лесу, ты ненавидишь вежливых людей, у тебя есть волшебный камень и ты отдашь его только если человек тоже будет грубым резким и 'классным' и ответит на 3 вопроса про рок музыку 1980-2000-х"
    )

    # Функция для сброса истории с сохранением системного промпта
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

        print("DeepSeek-R1:", end=' ', flush=True)
        reply = chat_stream(messages)
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
