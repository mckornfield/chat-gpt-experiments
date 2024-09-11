import os
import glob
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tap import Tap
import asyncio

load_dotenv()

PROMPT = """This GPT processes text files containing Grateful Dead shows and converts them into structured JSON data.
It reads through the text, extracts relevant details like the date, location, setlist, and other metadata,
then organizes this data into a JSON format. 
The format follows:
{"id": "1969-01-25", "date": "1969-01-25", "venue": {"name": "Avalon Ballroom", "city": "San Francisco", "state": "CA"}, "setlist": [{"set": 1, "track": 1, "song": "Dark Star ->", "transition": true, "length": "14:06.58"}, ... ]}. 
The GPT prioritizes transitions, song lengths, venue details, setlists, set numbers, and track numbers.
It should ask for clarification on ambiguous or missing data, handle various text formats, and inconsistencies.
The GPT will only return data for the file uploaded in each instance and will not reference prior conversions.
"""
client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

sem = asyncio.Semaphore(3)


async def safe_send_prompt_and_write(
    input_file_location: str, output_file_location: str, dry_run: bool = False
):
    async with sem:  # semaphore limits num of simultaneous downloads
        return await send_prompt_and_write(
            input_file_location, output_file_location, dry_run
        )


async def send_prompt_and_write(
    input_file_location: str, output_file_location: str, dry_run: bool = False
) -> None:
    # Files had weird windows encoding
    with open(input_file_location, encoding="cp1252") as f:
        file_contents = f.read()
    prompt = PROMPT + "\n" + file_contents
    completion = "{}"
    if not dry_run:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o",
        )
        completion = chat_completion.choices[-1].message.content

    # Naively place into output file
    with open(output_file_location, "w", encoding="utf-8") as f:
        f.write(completion)


class ClientParser(Tap):
    directory: str  # Directory containing txt files to send with prompt
    dry_run: bool = False  # Set to true to avoid sending to ChatGPT


async def main():

    args: ClientParser = ClientParser().parse_args()
    tasks = []
    for input_file in glob.glob(glob.escape(args.directory) + "**/*.txt"):
        if input_file.endswith("shn.st5.txt"):
            continue
        output_file = os.path.splitext(input_file)[0] + ".json"
        tasks.append(safe_send_prompt_and_write(input_file, output_file, args.dry_run))
    await asyncio.gather(*tasks)

    # with open("sample_txt_files/1969/Grateful_Dead-Boston_1969-04-21-info.txt") as f:
    #     file_contents = f.read()
    # asyncio.run(send_prompt(file_contents))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
