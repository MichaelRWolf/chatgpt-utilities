import argparse
import json
import logging
import os
import sys

import requests


def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Argument parser setup
    parser = argparse.ArgumentParser(description='Send a prompt to OpenAI and display the result.')
    parser.add_argument('--no-execute', action='store_true', help='Assemble the prompt but do not send the request')
    args = parser.parse_args()

    # Step 1: Check for the API key in environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("Environment variable 'OPENAI_API_KEY' not found.")
        sys.exit("Error: API key not found in environment variables.")

    # api_key = api_key + "foo"
    # Step 2: Read from stdin into the 'raw_input' variable
    raw_input = sys.stdin.read()

    # Step 3: Define the 'instructions' variable
    instructions = """
    Gather input into variable called 'raw_input'.
    Analyze 'raw_input'. If it looks like a calendar event, organize it into the form of an *.ics file and return that as the reply.
    If it does not look like a calendar event, throw an error that can be handled by whoever consumes the reply.
    """

    # Step 4: Concatenate 'instructions' and 'raw_input' to form the prompt
    prompt = json.dumps(instructions + "\n" + raw_input)

    # Define the API endpoint
    # url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
    url = 'https://api.openai.com/v1/chat/completions'

    # Step 5: Prepare the POST request data
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    data = {
        'prompt': prompt,
        'max_tokens': 150,
    }

    data = {
        'model': 'gpt-4o',
        'prompt': 'Say this is a test',
        'max_tokens': 5
    }
    data = {
        'model': 'gpt-4o',
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful assistant.'
            },
            {
                'role': 'user',
                'content': 'Hello'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        # 'max_tokens': 5
    }

    if args.no_execute:
        logging.debug("Request data prepared. Here is the data that would be sent:")
        logging.debug(json.dumps(data, indent=2))
        sys.exit(2)
    else:
        logging.info(f"Will send request to {url}")

        response = None;
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            logging.info(f"Response received. Status: {response.status_code}")
            logging.info(f"Response time: {response.elapsed.total_seconds()} seconds")

            result = response.json()
            logging.info(f"Usage details: {result.get('usage', 'No usage info')}")
            logging.debug(f"result: {result}")

            print("1. result: ", result, "\n")
            print("2. result['choices']", result['choices'], "\n")
            print("3. result['choices'][0]", result['choices'][0], "\n")
            print("4. result['choices'][0]['text']",
                  result['choices'][0].get('text', f"No 'text' value in {result['choices'][0]}"), "\n")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            # logging.debug(f"response: {json.dumps(response)}")
            logging.info(f"headers: {json.dumps(headers, indent=2)}")
            logging.info(f"data: {json.dumps(data, indent=2)}")
            logging.error(f"Response content: {e.response.content.decode() if e.response else 'No response content'}")
            sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
