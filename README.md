# chat-gpt-experiments

Some experiments for running ChatGPT requests

## Setup

Add your OPENAI_API_KEY to a `.env` file

```bash
echo "OPENAI_API_KEY=${OPENAI_API_KEY}" > .env

```

Install dependencies

```bash
python -m venv .venv
. .venv/bin/activate
pip install requirements.txt
```

### Text to JSON example

To run the text to JSON example, run the main method and point it at the appropriate directory

```bash
python txt_to_json/main.py --directory sample_txt_files/
# or to do a dry run, which just sets the files to empty values
python txt_to_json/main.py --directory sample_txt_files/ --dry_run
```
