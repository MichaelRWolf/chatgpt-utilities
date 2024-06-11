#! /usr/bin/env python3

import io
import argparse
import subprocess

CHAT_PROGRAM_DEFAULT = 'chatGPT-CLI'


def get_instructions(url):
    template=get_template()
    instructions = f"""
*Goal - Create content for a logseq node

**Task - Access URL ({url}) to retrieve page content

**Task - Extract information to create a standard citation in 3 formats: APA, MLA, CSM

**Task - Create summary with length being the shorter of 15% of word count or 5 sentences, whichever is longer.

**Task - Output summary and citations using the format specified in `Template` section below

*Template
```mark-down
{template}
```
"""
    return instructions

def get_template():
    template = """
* [Insert Title Here]

[Insert URL here]

** Summary

[Insert Summary here]

** Citations
*** Markdown Citation
| Title | |
| URL | |
| Author(s) | |
| Publication | |
| Publication Date | |
*** APA Citation
[Insert APA Citation here]
*** MLA Citation
[Insert MLA Citation here]
*** CSM Citation
[Insert CSM Citation here]
"""
    return template




def process_input(url, chat_program):
    instructions = get_instructions(url)
    template = get_template()
    # input_text = f"{instructions}\n{template}"
    input_text = f"{instructions}"

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
                        help=f"The chat program to use (default: {CHAT_PROGRAM_DEFAULT})")

    parser.add_argument("--no-execute",
                        action="store_true",
                        help="Behave as if '--chat-program cat' is set")


    args = parser.parse_args()

    if args.no_execute:
        args.chat_program = "cat"


    process_input(args.url, args.chat_program)

if __name__ == "__main__":
    main()
