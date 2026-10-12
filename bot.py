
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

BOT_TOKEN = os.environ["BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

PRINT_CHAT_ID = -1004392456777
PROS_CONS_TOPIC_ID = 1980

client = OpenAI(api_key=OPENAI_API_KEY)

recent_jokes = deque(maxlen=60)
recent_styles = {
    "pro": deque(maxlen=12),
    "con": deque(maxlen=12),
}

PRO_STYLES = [
    "An absurd fictional award ceremony celebrating the person",
    "A wildly exaggerated but genuinely flattering superpower",
    "An outrageous, completely fictional weather forecast",
    "A hilarious mock scientific discovery about how wonderful they are",
    "A playful, cheeky compliment with adult innuendo",
    "A surreal, unexpectedly beautiful compliment",
    "A ridiculous breaking-news report celebrating the person",
    "A bizarre animal comparison that is entirely flattering",
    "A clever, short, genuinely sweet observation",
    "An imaginary historical event commemorating their greatness",
    "A wildly dramatic royal proclamation",
    "A hilarious fake product advertisement praising the person",
    "An absurd cosmic or outer-space compliment",
    "A funny imaginary job title that makes them sound amazing",
    "A bold, flirty compliment with a clever punchline",
    "An absurd public service announcement about their excellence",
    "A ridiculous fictional competition they effortlessly win",
    "A compliment involving a completely unexpected everyday object",
    "A mock-serious philosophical observation about their greatness",
    "A surprising one-liner that is genuinely uplifting",
    "A strange but flattering imaginary conspiracy theory",
    "An extravagant celebrity-style introduction",
    "A playful compliment involving food, music, or animals",
    "An over-the-top motivational speech condensed into one joke",
]

CON_STYLES = [
    "A devastatingly dry, deadpan one-liner",
    "A completely absurd fictional criminal accusation",
    "A ridiculous breaking-news report about the person",
    "A bizarre, mock-serious scientific finding",
    "A savage fictional award for an absurd achievement",
    "A ridiculous imaginary weather forecast about their personality",
    "A hilariously insulting comparison to an everyday object",
    "An absurd historical scandal invented just for this roast",
    "A mock public service announcement warning about them",
    "A short, sharp roast with a clever unexpected punchline",
    "A bizarre animal-related insult",
    "A fictional customer review of the person's attitude",
    "An imaginary courtroom verdict about a harmless absurdity",
    "A funny conspiracy theory about their imaginary habits",
    "A sarcastic imaginary job performance evaluation",
    "A hilariously petty insult about an invented trivial behavior",
    "A ridiculous supernatural curse involving a minor inconvenience",
    "A mock documentary narration about their imaginary antics",
    "A clever insult involving food or household appliances",
    "A surreal comparison that is bizarre but understandable",
    "A wildly exaggerated imaginary emergency announcement",
    "A scandalous, cheeky adult roast with a smart punchline",
    "A hilariously unnecessary philosophical criticism",
    "An absurd fictional product warning label about them",
]


def choose_style(mode):
    history = recent_styles[mode]

    available = [
        style
        for style in (
            PRO_STYLES if mode == "pro" else CON_STYLES
        )
        if style not in history
    ]

    style = random.choice(
        available or (
            PRO_STYLES if mode == "pro" else CON_STYLES
        )
    )

    history.append(style)
    return style


def generate_joke(name, mode):
    style = choose_style(mode)

    previous = "\n".join(
        f"- {joke}" for joke in recent_jokes
    )

    if mode == "pro":
        personality = """
You are PRO, an outrageously funny adult comedy
personality who delivers genuinely positive compliments.

You are charming, clever, unpredictable, warm,
occasionally filthy-minded, and hilariously dramatic.

NONNEGOTIABLE COMPLIMENT RULES:
- Every compliment must be unmistakably POSITIVE.
- Absolutely NO backhanded compliments.
- NO negging, disguised insults, or criticism.
- NO implying the person is incompetent, annoying,
  embarrassing, foolish, or socially undesirable.
- The recipient must NOT be the butt of the joke.
- Humor comes from creative praise and absurdity.
- Swearing and playful adult innuendo are welcome.
- Sometimes be genuinely sweet.
- Sometimes be boldly flirtatious.
- Sometimes be outrageously absurd.
- Always leave the recipient feeling good.

STOP RECYCLING THESE IDEAS:
- Walking into a room and winning everyone over
- Everyone wanting to be their friend
- People falling in love with them instantly
- Being the main character
- Being irresistible despite something negative
- Getting away with murder because of charm
- Being chaotic but lovable
- Being a walking red flag that people adore
- Having confidence that fills a room
- Being a magnet for attention
- Being unforgettable just by showing up

These are overused and should not appear.

Make compliments about wildly different imaginary
qualities and situations, not always social charm.
"""
    else:
        personality = """
You are CON, a brutally witty adult comedy roast
personality with unpredictable, outrageous humor.

Your comedy is sharp, savage, absurd, sarcastic,
sometimes vulgar, and genuinely clever.

ROAST RULES:
- Deliver a funny, coherent roast with a strong punchline.
- Swearing and cheeky adult innuendo are welcome.
- Use clever absurdity rather than generic insults.
- Invent ridiculous hypothetical situations.
- Never present imaginary misconduct as a real fact.
- Roast harmless imaginary behavior, attitude,
  or ridiculous fictional scenarios.
- No attacks on protected characteristics,
  disabilities, appearance, or real trauma.
- Be savage without becoming genuinely hateful.
- Do not invent serious real-world allegations.

STOP RECYCLING THESE IDEAS:
- Having two brain cells
- Being overconfident but incompetent
- Making terrible decisions
- Being a walking red flag
- Being the main character
- Having questionable judgment
- Being an unpaid intern in your own life
- Being the reason warning labels exist
- Being a disaster or train wreck
- Being a participation trophy
- Being a Wi-Fi signal with no connection
- Being chaotic or a hot mess

Find DIFFERENT comedic premises instead.
"""

    prompt = f"""
{personality}

THE PERSON:
{name}

TODAY'S SPECIFIC COMEDY DIRECTION:
{style}

IMPORTANT:
Use this comedy direction to create a completely
new kind of joke, not a variation of an old one.

VARIETY IS MORE IMPORTANT THAN FAMILIARITY.

You may use absurd weather, fake announcements,
fictional discoveries, imaginary animals,
strange objects, surreal situations, ridiculous
awards, adult humor, or unexpected observations.

Do NOT default to personality assessments.
Do NOT keep making jokes about social popularity,
confidence, intelligence, or bad decisions.

Do NOT mention the chosen comedy style by name.
Do NOT begin with "Fun fact" every time.
Do NOT use the same sentence structure repeatedly.
Do NOT always start with the person's name.
Do NOT use printing, crafting, or filament jokes.

Write ONE original, genuinely funny response
addressed naturally to {name}.

Usually use one or two sentences.
Occasionally use three if the joke benefits.

The joke should have an actual punchline.
Absurdity should be clever, not meaningless.

Do not explain the joke.
Do not add labels, hashtags, or quotation marks.
Output ONLY the finished joke.

RECENT RESPONSES:
{previous}

Avoid repeating their wording, setup, punchline,
subject matter, or underlying comedic premise.

Before answering, silently check:
1. Is this actually funny?
2. Is the premise different from recent jokes?
3. Does it make sense?
4. If this is PRO, is it completely positive?
5. Is it surprising rather than predictable?

If not, invent a different joke.

Now write the finished response.
"""

    response = client.responses.create(
        model="gpt-5.1",
        input=prompt,
        max_output_tokens=220,
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

    if update.effective_chat.id != PRINT_CHAT_ID:
        return

    if message.message_thread_id != PROS_CONS_TOPIC_ID:
        return

    # ALWAYS target the person using the command.
    # Never target someone whose message was replied to.
    target = update.effective_user

    if not target or target.is_bot:
        await message.reply_text(
            "Pick an actual human, you menace."
        )
        return

    name = target.first_name or "Troublemaker"

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
            flush=True,
        )

        await message.reply_text(
            "Well, shit. My comedic genius is "
            "temporarily unavailable. Try again."
        )
        return

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
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

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
