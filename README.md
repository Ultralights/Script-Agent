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

   or create a local `.env` file and keep it secret. Do not commit your API key to git.

   ```bash
   cp .env.example .env
   ```

### GitHub Actions

A workflow is included at `.github/workflows/generate-script.yml` that can use a repository secret named `OPENAI_API_KEY`.

1. Add your API key to the repo secrets with the name `OPENAI_API_KEY`.
2. Trigger the workflow manually from GitHub using `workflow_dispatch`.
3. Provide either `url` for single-story segment mode or `urls` for episode mode.

## Usage

### Interactive mode (recommended)

Simply run the script and follow the prompts:

```bash
python script_agent.py
```

You'll be asked to:
- Select mode (segment or episode)
- Enter story URL(s) — comma-separated for multiple stories
- Desired style
- Preferred length

The script will save the output to `segment_script.txt` or `episode_script.txt` by default.

### Command-line mode

Provide all options as arguments:

#### Single story segment

```bash
python script_agent.py --mode segment --url "https://example.com/story" --style "snarky and upbeat" --length medium --output draft.txt
```

#### Episode from multiple stories

```bash
python script_agent.py --mode episode --urls "https://example.com/story1" "https://example.com/story2" "https://example.com/story3" --style "warm but sharp" --length medium --output episode.txt
```

### Weekly automated episodes

A scheduled workflow runs every Monday at 8 AM UTC to generate an episode automatically.

1. Create `upcoming_stories.json` in the repo root (copy from `upcoming_stories.json.example`):

   ```json
   {
     "urls": [
       "https://example.com/story1",
       "https://example.com/story2",
       "https://example.com/story3"
     ]
   }
   ```

2. The workflow will:
   - Read URLs from `upcoming_stories.json`
   - Generate a teleprompter-ready episode
   - Commit and push the script to the repo with a timestamp

You can also trigger it manually from the GitHub Actions tab.

## Customizing the voice

- Use `--style` to change the flavor (for example, `snarky but friendly`, `warm and optimistic`, or `sharp energy market critique`).
- Use `--length` for `short`, `medium`, or `long` segments.

## Notes

- The script is built to avoid personal shaming and keep the tone inviting.
- Humor is aimed at fossil fuel volatility, not drivers.
- Keep your `OPENAI_API_KEY` secret and never commit it to the repo.
- You can adjust the `PROMPT_TEMPLATE` in `script_agent.py` if you want to refine the tone further.
