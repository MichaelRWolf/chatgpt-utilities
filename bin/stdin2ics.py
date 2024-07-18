#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys

import requests


def main():
    # Configure logging
    logging.basicConfig(level=(getattr(logging,
                                       os.getenv('LOGLEVEL', 'WARNING').upper(),
                                       logging.WARNING)))

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
    - Analyze text input from `Raw Input` section (below).
    - If it looks like a calendar event, 
        then organize it into the form of an *.ics file
        else if it looks like a contact (person or business)
        then organize it into the form of a vCard file
        else the reply should be "No calendar or contact found in this input", followed by the text from 'Raw Input' section.
        
    Other considerations for calendar events
    - Before generating the *.ics file, determine the current date and time.
    - If the event does not contain a year, add a year so that the event is in the future.
    - Do not generate a DTSTAMP line.
    
    Other considerations for contacts
    - Search for information that looks like a person's name, phone number, email address, street address, website URL.  If it contains any of these types of informaton, generate either a person vCard, a business vCard, or both.
    - Realize that information may not be in a standard format.  For instance, it may all be on a single line.
        Example: SoftEd USA, 201 Commonwealth Court, Cary, NC, 27511, United States
    - If there is only a single line, try breaking the line at punctuation, then retry analysis.        
    - If there is a person name, generatea  vCard for a person.  If not, generate a vCard for a business.
    - If there is both a person name and a business name, then generate a vCard for both the person and the business.
    """

    output_format = """
For calendar events 
- never surround *.ics output with triple-back-ticks
- never include leading or trailing explanation    
- output the text as an *.ics file
- use version 2.0 (from RFC 5545)

For person contact cards and business contact cards
- never surround *.vcf output with triple-back-ticks
- never include leading or trailing explanation    
- If fields are missing from an address, remember to add semi-colons to comply with the standars
   ADR:post-office-box;extended-address;street-address;locality;region;postal-code;country-name
Example - this indicates an empty `post-office-box` and `extended-address` field:
   ADR:;;201 Commonwealth Court;Cary;NC;27511;United States

For all output formats
 """

    # Step 4: Concatenate 'instructions' and 'raw_input' to form the prompt
    prompt = json.dumps(f"* Instructions\n{instructions}\n\n"
                        f"* Output Format\n{output_format}\n\n"
                        f"* Raw Input\n{raw_input}\n")

    # Define the API endpoint
    # url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
    url = 'https://api.openai.com/v1/chat/completions'

    # Step 5: Prepare the POST request data
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
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
        'max_tokens': 200
    }

    if args.no_execute:
        print("Request data prepared. Here is the data that would be sent:\n",
              json.dumps(data, indent=2),
              sep='',
              file=sys.stderr)
        sys.exit(2)
    else:
        logging.info(f"Will send request to {url}")

        response = None
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            logging.info(f"Response received. Status: {response.status_code}")
            logging.info(f"Response time: {response.elapsed.total_seconds()} seconds")

            result = response.json()
            logging.debug(f"result: {result}")
            choices_0 = result['choices'][0]
            choices_0_message = choices_0['message']
            usage_details = f"Usage details: {result.get('usage', 'No usage info')}"
            finish_reason = choices_0.get('finish_reason', None)
            if finish_reason == 'stop':
                logging.info(f"Choices 0 finish_reason: {finish_reason}")
                logging.info(usage_details)
            else:
                logging.warning(
                    f"Choices 0 message finish_reason is not 'stop': {finish_reason}")
                logging.warning(usage_details)

            # logging.debug("1. result: ", result, "\n")
            # logging.debug("2. result['choices']", result['choices'], "\n")
            # logging.debug("3. result['choices'][0]", result['choices'][0], "\n")
            # logging.debug("3.1 result['choices'][0]['message']", result['choices'][0]['message'], "\n")
            ics_text = choices_0_message['content']
            # logging.debug("3.2 result['choices'][0]['message']['content']", ics_text, "\n")
            # logging.debug("4. result['choices'][0]['text']",
            #       result['choices'][0].get('text', f"No 'text' value in {result['choices'][0]}"), "\n")
            print(ics_text)
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            # logging.debug(f"response: {json.dumps(response)}")
            logging.info(f"headers: {json.dumps(headers, indent=2)}")
            logging.info(f"data: {json.dumps(data, indent=2)}")
            logging.error(f"Response content: {e.response.content.decode() if e.response else 'No response content'}")
            sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
