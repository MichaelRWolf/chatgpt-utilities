#! /usr/bin/env python3

import io
import argparse
import subprocess

CHAT_PROGRAM_DEFAULT = 'chatGPT-CLI'


def get_instructions(url):
    instructions = f"""
*Goal - Create content for a logseq node

**Task - Retrieve page from URL that is provided

**Task - Using template (provided below), fill in values for fields

- Title
- Author(s)
- Publication - or media, blog, channel...
- Publication Date

**Task - Summarize article

- If possible, provide a short paragraph summarizing the article.

**URL

{url}
"""
    return instructions

def get_template():
    template = """
* Template

''' mark-down
* Reference & Citation

| Title | |
| Author(s) | |
| Publication | |
| Publication Date | |

** APA Citation
** MLA Citation
** CSM Citation

* Summary

'''
"""
    return template




def process_input(url, chat_program):
    instructions = get_instructions(url)
    template = get_template()
    input_text = f"{instructions}\n{template}"

    if chat_program == 'chatGPT-CLI':
        subprocess.run([chat_program, input_text], input=input_text, text=True)
        # subprocess.run([chat_program], input=input_text.encode(), text=True)
    else:
        print(input_text)

def main():
    parser = argparse.ArgumentParser(description='Process a URL with a chat program.')
    parser.add_argument('url', 
                        help='The URL to process')

    parser.add_argument('--chat-program',
                        default=CHAT_PROGRAM_DEFAULT,
                        help=f"The chat program to use (default: {CHAT_PROGRAM_DEFAULT})")h

    parser.add_argument("--no-execute",
                        action="store_true",
                        help="Behave as if '--chat-program cat' is set")


    args = parser.parse_args()

    if args.no_execute:
        args.chat_program = "cat"


    process_input(args.url, args.chat_program)

if __name__ == "__main__":
    main()
