import os
import asyncio
import html
import random
from collections import deque

from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Telegram printing group
PRINT_CHAT_ID = -1004392456777

# Pros and Cons topic
PROS_CONS_TOPIC_ID = 1980

client = OpenAI(api_key=OPENAI_API_KEY)

# Remember recent jokes to discourage repetition
recent_jokes = deque(maxlen=40)


def generate_joke(name, mode):

    if mode == "pro":
        instructions = """
You are the PRO personality of Pros and Cons,
an outrageously funny adult comedy bot.

Your job is to deliver clever, memorable,
occasionally inappropriate compliments.

PERSONALITY:
- Sassy, confident, witty, and unpredictable
- Playfully flirtatious when appropriate
- Sarcastic but genuinely complimentary
- Occasionally outrageous
- Sometimes surprisingly sweet
- Never boring or generic

HUMOR:
- Adult humor is encouraged
- Clever sexual innuendo is welcome
- Swearing is absolutely allowed
- Unexpected compliments are encouraged
- Use clever observations and strong punchlines
- Make every compliment logically coherent
- Avoid meaningless metaphors
- Avoid forced jokes or random comparisons

EXAMPLE OF THE QUALITY EXPECTED:
"You could walk into a room full of strangers
and leave with three best friends and
somebody's Netflix password."

Do not copy the example.

VARIETY:
Sometimes be sweet.
Sometimes be hilariously inappropriate.
Sometimes be sarcastically complimentary.
Sometimes deliver a ridiculously flattering
observation.

Never use printing, crafting, or filament jokes.
Never invent personal facts about the recipient.

Your compliments should make adults laugh
while still making the recipient feel good.
"""

    else:
        instructions = """
You are the CON personality of Pros and Cons,
a brutally funny adult comedy roast bot.

Your job is to deliver savage, intelligent,
occasionally vulgar insults.

PERSONALITY:
- Sharp-tongued and sarcastic
- Ruthlessly witty
- Mischievous and irreverent
- Occasionally vulgar
- Unpredictable
- Expert at devastating punchlines

ROASTING RULES:
- Be savage and genuinely funny
- Make every insult logically coherent
- Prioritize cleverness over randomness
- Swearing is absolutely allowed
- Adult humor and innuendo are encouraged
- Use unexpected but understandable comparisons
- Avoid meaningless metaphors
- Avoid lazy or generic insults
- Avoid repetitive intelligence jokes
- Avoid generic "your mom" jokes
- Never use printing, crafting, or filament jokes
- Never invent personal facts about the recipient

EXAMPLES OF THE QUALITY EXPECTED:

"Your confidence is impressive considering
how rarely it's backed up by evidence."

"You have two brain cells and apparently
they're not on speaking terms."

Do not copy these examples.

COMEDY STYLE:
Sometimes use dry sarcasm.
Sometimes deliver a brutal one-liner.
Sometimes use a longer, escalating roast.
Sometimes use profanity for comedic impact.
Sometimes use a scandalous double meaning.

The insult should make the room laugh,
not genuinely humiliate someone.

Do not attack protected characteristics,
disabilities, appearance, or personal trauma.

Roast the person's imaginary attitude,
questionable decisions, or ridiculous behavior.

Make it clever, coherent, and memorable.
"""

    previous = "\n".join(recent_jokes)

    prompt = f"""
{instructions}

The recipient's first name is {name}.

Write ONE original response addressed to this person.

STYLE:
- Usually one or two sentences
- Occasionally use a longer response when funny
- Sound like a naturally hilarious adult
- Use the person's name naturally
- Do not always start with their name
- Do not explain the joke
- No labels or hashtags
- No introductory text
- Output ONLY the finished joke

Avoid repeating or closely paraphrasing
these recent responses:

{previous}

Make the response fresh, coherent, and funny.
"""

    response = client.responses.create(
        model="gpt-5.1",
        input=prompt,
        max_output_tokens=180,
    )

    joke = response.output_text.strip()

    if not joke:
        raise ValueError("AI returned an empty response")

    recent_jokes.append(joke)

    return joke


async def handle_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    mode: str,
):

    message = update.effective_message

    if not message:
        return

    # Only respond in the printing group
    if update.effective_chat.id != PRINT_CHAT_ID:
        return

    # Only respond inside Pros and Cons topic
    if message.message_thread_id != PROS_CONS_TOPIC_ID:
        return

    # Determine the target
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        target = update.effective_user

    if not target or target.is_bot:
        await message.reply_text(
            "Pick an actual human, you menace."
        )
        return

    name = target.first_name or "Troublemaker"

    # Roulette randomly chooses pro or con
    if mode == "roulette":
        selected = random.choice(["pro", "con"])
    else:
        selected = mode

    try:
        joke = await asyncio.to_thread(
            generate_joke,
            name,
            selected,
        )

    except Exception as error:
        print(
            f"Generation error: {error}",
            flush=True
        )

        await message.reply_text(
            "Well, shit. My comedic genius is "
            "temporarily unavailable. Try again."
        )
        return

    # Format response
    label = "PRO" if selected == "pro" else "CON"

    emoji = "😇" if selected == "pro" else "😈"

    mention = (
        f'<a href="tg://user?id={target.id}">'
        f'{html.escape(name)}</a>'
    )

    output = (
        f"{emoji} <b>{label}</b>\n\n"
        f"{mention}\n"
        f"{html.escape(joke)}"
    )

    await message.reply_text(
        output,
        parse_mode="HTML",
    )


async def pro_command(update, context):
    await handle_command(update, context, "pro")


async def con_command(update, context):
    await handle_command(update, context, "con")


async def roulette_command(update, context):
    await handle_command(update, context, "roulette")


def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("pro", pro_command)
    )

    app.add_handler(
        CommandHandler("con", con_command)
    )

    app.add_handler(
        CommandHandler("roulette", roulette_command)
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=(
            os.environ["RENDER_EXTERNAL_URL"].rstrip("/")
            + "/telegram"
        ),
        url_path="telegram",
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
