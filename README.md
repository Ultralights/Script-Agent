# Script-Agent

A lightweight podcast script agent for converting story links into EV-friendly podcast segment drafts.

## What it does

- Fetches the story title and early content from a link.
- Builds a prompt with your ground rules for EV enthusiasm, satire, and newcomer-friendly tone.
- Sends the prompt to OpenAI and returns a draft script.

## Ground rules baked into the agent

- Welcomes new listeners and curious folks.
- Frames EVs as practical, wallet-friendly, future-proof choices.
- Paints fossil fuel/ICE as outdated, unreliable, expensive old tech.
- Uses sharp system-level humor, not attacks on drivers.
- Emphasizes empathy and celebration instead of shaming.

## Setup

1. Create a Python virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Export your OpenAI API key:

   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

## Usage

### Single story segment

```bash
python script_agent.py --mode segment --url "https://example.com/story" --style "snarky and upbeat" --length medium
```

Optional save output:

```bash
python script_agent.py --mode segment --url "https://example.com/story" --style "funny, welcoming new listeners" --length short --output draft.txt
```

### Compiled episode mode

```bash
python script_agent.py --mode episode --urls "https://example.com/story1" "https://example.com/story2" "https://example.com/story3" --style "warm but sharp" --length medium --output episode.txt
```

- Episode mode compiles multiple stories into a single show with segments:
  Local Australia News, International News, Policy News, Infrastructure, Renewable Energy, Environment, Fun Stories.
- The generated output is optimized for teleprompter use with short lines and double-spaced formatting.

## Customizing the voice

- Use `--style` to change the flavor (for example, `snarky but friendly`, `warm and optimistic`, or `sharp energy market critique`).
- Use `--length` for `short`, `medium`, or `long` segments.

## Notes

- The script is built to avoid personal shaming and keep the tone inviting.
- Humor is aimed at fossil fuel volatility, not drivers.
- You can adjust the `PROMPT_TEMPLATE` in `script_agent.py` if you want to refine the tone further.
