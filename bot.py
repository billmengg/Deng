import os
import discord
import openai
import json
import datetime
from dotenv import load_dotenv

# Read the .env file manually and extract the values
env_file_path = r"c:/Users/William/Documents/YouTube/Coding/Deng/.env"

# Create a dictionary to store the key-value pairs
env_vars = {}

# Read the .env file and extract key-value pairs
with open(env_file_path, "r") as env_file:
    for line in env_file:
        # Strip any leading/trailing whitespace
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Split the line into key and value
        key, value = line.split("=", 1)

        # Add key-value pair to the dictionary
        env_vars[key.strip()] = value.strip()

# Now you can access the environment variables directly
DISCORD_TOKEN = env_vars.get("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = env_vars.get("OPENAI_API_KEY")

# Check if the keys are loaded correctly
if not DISCORD_TOKEN or not OPENAI_API_KEY:
    print("Error: DISCORD_BOT_TOKEN or OPENAI_API_KEY is missing from the .env file.")
else:
    print(f"DISCORD_TOKEN: {DISCORD_TOKEN}")
    print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")


# Check if keys are loaded correctly (optional, for debugging purposes)
if not DISCORD_TOKEN or not OPENAI_API_KEY:
    print("Error: DISCORD_TOKEN or OPENAI_API_KEY is missing from the .env file.")
else:
    print("API keys loaded successfully.")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# File to store schedules
SCHEDULE_FILE = "schedule.json"

# Load or initialize schedule data
if os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "r") as f:
        schedule_data = json.load(f)
else:
    schedule_data = {day: {"current_activity": "", "schedule": []} for day in 
                     ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}


def save_schedule():
    """Save the schedule data to a file."""
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule_data, f, indent=4)


def update_schedule(day, time, activity):
    """Update the schedule with a new activity at a specific time."""
    if day in schedule_data:
        schedule_data[day]["schedule"].append({"time": time, "activity": activity})
        schedule_data[day]["schedule"] = sorted(schedule_data[day]["schedule"], key=lambda x: x["time"])
        save_schedule()


def get_next_activity(day):
    """Get the next activity based on the current time."""
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    for entry in schedule_data[day]["schedule"]:
        if entry["time"] > current_time:
            return entry
    return None


async def get_chatgpt_response(prompt):
    """Get a response from ChatGPT based on the user's message."""
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # You can choose other models as well
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()  # Extract the response text
    except Exception as e:
        print(f"Error getting response from OpenAI: {e}")
        return "Sorry, I encountered an error while processing your request."


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Send a message when the bot starts
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == "schedule":  # Check if the channel is named "schedule"
                await channel.send("Bot is now online and ready to manage your schedule!")

@client.event
async def on_message(message):
    # Ensure the bot only responds to messages in the "schedule" channel
    if message.author == client.user or message.channel.name != "schedule":
        return  # Ignore bot messages & messages from other channels

    # Debugging output: Print raw message
    print(f"Raw message from {message.author.display_name}: {repr(message.content)}")

    # If it's a greeting or help request, respond using ChatGPT
    if "hello" in message.content.lower() or "help" in message.content.lower():
        try:
            # Call OpenAI API for a response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message.content}
                ]
            )
            openai_reply = response['choices'][0]['message']['content']
            await message.channel.send(openai_reply)

        except Exception as e:
            print(f"Error getting response from OpenAI: {e}")
            await message.channel.send("Sorry, I couldn't fetch a response right now. Please try again later.")



client.run(DISCORD_TOKEN)
