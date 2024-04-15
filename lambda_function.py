# Only God knows how this works 15/4/24 rmbr do not add the asyncio package it is routed by aws to retieve that packagage ~zlyj
import numpy as np
import asyncio
import aiohttp
import json
import ast
import os


def lambda_handler(event, context):
    sentences = json.loads(event["body"])["data"]

    main_data = []

    async def api_analyze(sentences, userinput=None):
        def constructor(sentence, instruct):
            content = f"Review:\n{sentence}"
            return {
                "messages": [
                    {"role": "system", "content": instruct},
                    {"role": "user", "content": content},
                ],
                "temperature": 0,
                "top_p": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "max_tokens": 1000,
                "stop": "null",
            }

        API_KEY = os.getenv("API_KEY")

        async def analyze_sentence(session, endpoint_url, sentence, instruct):
            async with session.post(
                endpoint_url, json=constructor(sentence, instruct)
            ) as response:
                print(f"Endpoint: {endpoint_url}|Data: {sentence}")
                if response.status == 200:
                    result = await response.json()
                    raw = json.dumps(result)
                    tokens_used = result["usage"]["total_tokens"]
                    input_token = result["usage"]["prompt_tokens"]
                    output_token = result["usage"]["completion_tokens"]
                    cost = (input_token * input_cost) + (output_token * output_cost)
                    try:
                        cleaned_result = ast.literal_eval(
                            result["choices"][0]["message"]["content"]
                        )
                        score, theme, keywords = cleaned_result
                        if DEBUG:
                            print(
                                f"DEBUG from ast.literal_eval: {score}, {keywords}, {theme}"
                            )
                        data_row = [
                            sentence,
                            endpoint_url.replace(
                                API_KEY, "███████████████████████████████"
                            ),
                            score,
                            theme,
                            keywords,
                            None,
                            tokens_used,
                            cost,
                            raw,
                        ]
                    except Exception:
                        other = result["choices"][0]["message"]["content"]
                        if other:
                            data_row = [
                                sentence,
                                endpoint_url.replace(
                                    API_KEY, "███████████████████████████████"
                                ),
                                None,
                                None,
                                None,
                                other,
                                tokens_used,
                                cost,
                                raw,
                            ]
                        else:
                            data_row = [
                                sentence,
                                endpoint_url.replace(
                                    API_KEY, "███████████████████████████████"
                                ),
                                None,
                                None,
                                None,
                                None,
                                tokens_used,
                                cost,
                                raw,
                            ]
                    nonlocal main_data
                    main_data.append(data_row)
                    if DEBUG:
                        print("Added!")
                else:
                    if response.status == 429:
                        retry_after = int(
                            response.headers.get("Retry-After", delay_time)
                        )
                        print(f"Rate limit reached. Waiting for {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                    print(f"Endpoint {endpoint_url} returned error: {response.status}")
            return True

        DEBUG = False
        input_cost = 1.5 / 1000000
        output_cost = 2 / 1000000
        delay_time = 60
        CHUNK_SIZE = 18
        DELAY_BETWEEN_CHUNKS = 5

        if not (userinput is None or ""):
            instruct = f"Instuct:\nPerform aspect based sentiment analysis on the below review.\n- Provide a sentiment polarity score between 0 to 10 where 0 is negative and 10 is positive\n- Classify the key themes of the text into the most fitting category: {userinput}\n- Provide a list of keywords that indicate the theme\n\nGuidelines:\nReturn the score and the classified themes in the following format, [{{score}},[{{classified_themes}}],[{{list_of_keywords}}]]. I do not want any other text apart from the format given. If unable leave as [None,None,None]\n\nExample:\n[8,['Ease of use','Convenience'],['set up was easy', 'effortless']]"
        else:
            instruct = "Instuct:\nPerform aspect based sentiment analysis on the below review.\n- Provide a sentiment polarity score between 0 to 10 where 0 is negative and 10 is positive\n- Provide the key themes of the text\n- Provide a list of keywords that indicate the theme\n\nGuidelines:\nReturn the score and the themes in the following format, [{score},[{key_themes}],[{list_of_keywords}]]. I do not want any other text apart from the format given. If unable leave as [None,None,None]\n\nExample:\n[8,['Ease of use','Convenience'],['set up was easy', 'effortless']]"

        endpoint_urls = [
            f"https://intern2024openai.openai.azure.com/openai/deployments/gpt-35-thread{i}/chat/completions?api-version=2024-02-15-preview&api-key={API_KEY}"
            for i in range(1, 4)
        ]

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(sentences), CHUNK_SIZE):
                tasks = []
                chunk = sentences[i : i + CHUNK_SIZE]
                for j, sentence in enumerate(chunk):
                    endpoint_url = endpoint_urls[j % len(endpoint_urls)]
                    tasks.append(
                        analyze_sentence(session, endpoint_url, sentence, instruct)
                    )

                await asyncio.gather(*tasks)

                if i + CHUNK_SIZE < len(sentences):
                    print(
                        f"Finished a chunk. Waiting for {DELAY_BETWEEN_CHUNKS} seconds..."
                    )
                    await asyncio.sleep(DELAY_BETWEEN_CHUNKS)

    asyncio.run(api_analyze(sentences))

    main_data_array = np.array(main_data, dtype=object)

    # Convert the NumPy array to a list for JSON serialization
    main_data_list = main_data_array.tolist()

    # Return the list instead of the NumPy array
    return {"data": main_data_list}
