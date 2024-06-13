import argparse
import io
import json
import os
import sys
import unittest
from unittest.mock import mock_open
from unittest.mock import patch

from src.stdin2ics import main

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Sample input data
input_data = """Hi Joe.

Let's meet on 7/4/2024 at 2:00 (Eastern) for an hour to discuss firework display. I will call you on 206-555-1212. You can contact me at MichaelRWolf@example.com.

Best,
Michael

-- 
Michael R. Wolf
    MichaelRWolf@att.net  | +1-206-679-7941  |  LinkedIn.com/in/MRWolf
        "All mammals learn by playing"
"""

# Sample expected output for no-execute option
expected_output = """Request data prepared. Here is the data that would be sent:
{
  "prompt": "\\nGather input into variable called 'raw_input'.\\nAnalyze 'raw_input'. If it looks like a calendar event, organize it into the form of an *.ics file and return that as the reply.\\nIf it does not look like a calendar event, throw an error that can be handled by whoever consumes the reply.\\n\\nHi Joe.\\n\\nLet's meet on 7/4/2024 at 2:00 (Eastern) for an hour to discuss firework display. I will call you on 206-555-1212. You can contact me at MichaelRWolf@example.com.\\n\\nBest,\\nMichael\\n\\n-- \\nMichael R. Wolf\\n    MichaelRWolf@att.net  | +1-206-679-7941  |  LinkedIn.com/in/MRWolf\\n        \\\"All mammals learn by playing\\\"\\n",
  "max_tokens": 150
}
"""


# Import the main function from the script

class TestApproval(unittest.TestCase):
    @patch('sys.stdin', io.StringIO(input_data))
    @patch('sys.argv', ['stdin2ics.py', '--no-execute'])
    def test_no_execute(self):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
                patch('sys.stderr', new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2)
            output = mock_stdout.getvalue().strip()
            self.assertEqual(output, expected_output)


# class TestApproval0(unittest.TestCase):
#     @patch('sys.stdin', io.StringIO(input_data))
#     @patch('sys.argv', ['stdin2ics.py', '--no-execute'])
#     def test_no_execute(self):
#         with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
#                 patch('sys.stderr', new_callable=io.StringIO):
#             with self.assertRaises(SystemExit) as cm:
#                 main()
#             self.assertEqual(cm.exception.code, 2)
#             output = mock_stdout.getvalue().strip()
#             self.assertEqual(output, expected_output)
#

class TestStdin2Ics(unittest.TestCase):

    @patch('sys.stdin', new_callable=mock_open, read_data='Not a calendar event')
    @patch('sys.stdout', new_io_mock=True)
    def test_non_calendar_event(self, mock_stdout):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
                patch('sys.stderr', new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)
            output = mock_stdout.getvalue()
            self.assertIn('Error:', output)

    @patch('os.getenv', return_value='test_api_key')
    @patch('requests.post')
    @patch('sys.stdin', new_callable=mock_open, read_data='BEGIN:VCALENDAR\nEND:VCALENDAR')
    def test_valid_calendar_event(self, mock_post, mock_getenv):
        main()
        mock_post.assert_called_once()
        request_data = json.loads(mock_post.call_args[1]['data'])
        self.assertIn('BEGIN:VCALENDAR', request_data['prompt'])

    @patch('os.getenv', return_value=None)
    def test_missing_api_key(self, mock_getenv):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)
        self.assertIn('Error: API key not found in environment variables.', str(cm.exception))

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(no_execute=True))
    @patch('sys.stdout', new_io_mock=True)
    def test_no_execute_option(self, mock_stdout, mock_parse_args):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 2)
        output = mock_stdout.getvalue()
        self.assertIn('Request data prepared. Here is the data that would be sent:', output)

    unittest.main()


if __name__ == '__main__':
    import unittest
