import argparse
import os
import re
import sys
import textwrap

import openai
import requests
from bs4 import BeautifulSoup

DEFAULT_MODEL = "gpt-3.5-turbo"

STYLE_GUIDELINES = (
    "You are writing a draft podcast segment for an EV-focused show. "
    "The script should be enthusiastic, welcoming, and optimistic for newcomers. "
    "Use witty, irreverent satire to poke at fossil fuel volatility, oil geopolitics, and outdated ICE car economics, "
    "but avoid shaming people who still drive petrol/diesel vehicles. "
    "Emphasize that EVs are practical, wallet-friendly, and future-proof as oil prices and fuel costs keep rising. "
    "Keep the tone inviting and upbeat, with sharp commentary on systemic absurdities rather than individuals."
)

PROMPT_TEMPLATE = (
    "You are a podcast writer. Create a draft segment in a lively, listener-friendly style using the following rules.\n\n"
    "Ground rules:\n"
    "- Encourage and welcome new listeners and curious folks.\n"
    "- Highlight EVs as practical, wallet-friendly, future-proof choices.\n"
    "- Frame fossil fuel and ICE as outdated, unreliable, expensive old tech.\n"
    "- Use humor inspired by George Carlin (systems satire), Jon Oliver/Jon Stewart (satirical breakdowns), and "
    "  Dungeon AI (snarky chaotic market takes), but keep it positive toward EVs.\n"
    "- Avoid direct offense toward users/drivers. Empathize with fuel pain and celebrate EV wins.\n"
    "- Use cheeky roasts like 'wild oil price rollercoasters courtesy of geopolitics', "
    "  'paying premium for dinosaur juice that swings like a bad crypto trade', or "
    "  'ICE cars still guzzling while EVs sip electrons at home'.\n"
    "- Make newcomers feel invited, informed, and excited rather than preached to.\n\n"
    "Write a segment draft based on this story link and summary. Use the requested style if provided. "
    "Include a strong hook, a clear explanation of the main story, and a compelling closing that points toward why "
    "EV adoption makes sense now.\n\n"
    "Story link: {url}\n"
    "Story title: {title}\n"
    "Story summary: {summary}\n\n"
    "Desired style notes: {style_notes}\n"
    "Preferred length: {length_description}\n"
    "Write in natural, spoken language suitable for a podcast host."
)

EPISODE_PROMPT_TEMPLATE = (
    "You are a podcast writer crafting a single podcast episode. The episode must be organized into these segments:\n"
    "- Local Australia News\n"
    "- International News\n"
    "- Policy News\n"
    "- Infrastructure\n"
    "- Renewable Energy\n"
    "- Environment\n"
    "- Fun Stories\n\n"
    "Use short, teleprompter-friendly lines and double-spaced formatting so the host can read directly from the script. "
    "Keep the tone enthusiastic, welcoming, and optimistic for newcomers. "
    "Use witty, irreverent satire on fossil fuel volatility and outdated ICE economics, but avoid shaming drivers. "
    "Celebrate EV adoption as practical, wallet-friendly, and future-proof. "
    "Start with a strong welcome for new listeners and end with an upbeat closing on why EVs are the better choice now.\n\n"
    "Here are the story summaries to include or reference in the episode. Place each story in the best fitting segment.\n\n"
    "{stories}\n\n"
    "Desired style notes: {style_notes}\n"
    "Preferred length: {length_description}\n"
    "Write directly in teleprompter-ready format with short lines and blank lines between each line."
)


def fetch_story_text(url: str) -> tuple[str, str]:
    """Fetch the title and a clean summary from the provided URL."""
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "script-agent/1.0"})
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch URL: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")

    title = (soup.title.string if soup.title else "Untitled story").strip()
    article_text = []

    for tag in soup.find_all(["p", "h1", "h2", "h3"]):
        text = tag.get_text(separator=" ", strip=True)
        if text:
            article_text.append(text)
        if len(article_text) >= 10:
            break

    raw_text = "\n\n".join(article_text)
    summary = clean_text(raw_text)
    if len(summary) > 1200:
        summary = summary[:1200].rsplit(" ", 1)[0] + "..."

    return title, summary


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"https?://\S+", "", text)
    return text.strip()


def build_prompt(url: str, title: str, summary: str, style_notes: str, length: str, mode: str) -> str:
    length_description = {
        "short": "a concise 2-3 minute segment",
        "medium": "a balanced 3-5 minute segment",
        "long": "an in-depth 5-7 minute segment",
    }.get(length, "a balanced 3-5 minute segment")

    if mode == "episode":
        return EPISODE_PROMPT_TEMPLATE.format(
            stories=summary,
            style_notes=(style_notes.strip() if style_notes else "Keep it upbeat, conversational, and positive toward EV adoption."),
            length_description=length_description,
        )

    return PROMPT_TEMPLATE.format(
        url=url,
        title=title,
        summary=summary,
        style_notes=(style_notes.strip() if style_notes else "Keep it upbeat, conversational, and positive toward EV adoption."),
        length_description=length_description,
    )


def format_teleprompter_text(text: str, width: int = 60) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    formatted_blocks = []

    for paragraph in paragraphs:
        wrapped = textwrap.wrap(paragraph, width=width)
        if not wrapped:
            continue
        formatted_blocks.append("\n\n".join(wrapped))

    return "\n\n\n".join(formatted_blocks)


def call_openai(prompt: str, model: str, max_tokens: int = 900) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Export it as an environment variable before running this script."
        )

    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": STYLE_GUIDELINES},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a podcast script draft from one story or compile multiple stories into a teleprompter-ready episode."
    )
    parser.add_argument("--mode", choices=["segment", "episode"], default="segment",
                        help="Choose segment mode for a single story or episode mode for a compiled show.")

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--url", help="Link to the story or article for a single segment.")
    source_group.add_argument("--urls", nargs="+", help="One or more story links to compile into an episode.")

    parser.add_argument("--style", default="",
                        help="Optional direction for style or mood (e.g. 'snarky but friendly', 'bright and urgent', 'deep explainer').")
    parser.add_argument("--length", choices=["short", "medium", "long"], default="medium",
                        help="Preferred draft length for the segment or episode.")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="OpenAI model to use (default: gpt-3.5-turbo).")
    parser.add_argument("--output", help="Optional file path to save the generated script.")
    return parser.parse_args()


def fetch_multiple_story_texts(urls: list[str]) -> list[tuple[str, str]]:
    texts = []
    for url in urls:
        texts.append(fetch_story_text(url))
    return texts


def build_episode_story_block(stories: list[tuple[str, str]]) -> str:
    blocks = []
    for index, (title, summary) in enumerate(stories, start=1):
        if len(summary) > 400:
            summary = summary[:400].rsplit(" ", 1)[0] + "..."
        blocks.append(f"Story {index}: {title}\n{summary}")
    return "\n\n".join(blocks)


def main() -> int:
    args = parse_args()

    story_title = None
    story_summary = None
    max_tokens = 900

    try:
        if args.mode == "episode":
            if not args.urls:
                raise RuntimeError("Episode mode requires --urls with one or more story links.")
            stories = fetch_multiple_story_texts(args.urls)
            story_summary = build_episode_story_block(stories)
            max_tokens = 1200
        else:
            if not args.url:
                raise RuntimeError("Segment mode requires --url.")
            story_title, story_summary = fetch_story_text(args.url)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    prompt = build_prompt(
        args.url if args.mode == "segment" else None,
        story_title,
        story_summary,
        args.style,
        args.length,
        args.mode,
    )

    try:
        script_draft = call_openai(prompt, args.model, max_tokens=max_tokens)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"OpenAI request failed: {exc}", file=sys.stderr)
        return 1

    if args.mode == "episode":
        script_draft = format_teleprompter_text(script_draft)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(script_draft)
        print(f"Saved script draft to: {args.output}")
    else:
        print(script_draft)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
