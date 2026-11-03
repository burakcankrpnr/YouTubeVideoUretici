# Global AI Animation Studio

Animation Studio is integrated into the MoneyPrinterTurbo WebUI (not a separate app).

## Open the panel

1. Start the WebUI (`webui.bat` / `uv run streamlit run webui/Main.py`).
2. In the sidebar, choose **Workspace → Animation Studio**.
3. For hands-off operation: open **Autopilot** and press **START AUTOPILOT**.
   The AI invents the episode, MoneyPrinterTurbo renders it, and publish runs
   automatically (Upload-Post YouTube when configured; otherwise labeled mock publish).

## Architecture

```text
Studio (bible → script → storyboard → owner gates)
        ↓
MoneyPrinterTurbo task.start  (TTS + footage + FFmpeg → real MP4)
        ↓
Owner review / approve exact render
        ↓
Upload-Post YouTube  (MPT settings: API key, username, platforms includes youtube)
```

## What it includes

- Series Bible, characters, continuity memory
- Idea/script/safety/storyboard pipeline
- Storyboard approval gate before animation
- **Real video production through MoneyPrinterTurbo** (`app/studio/mpt_bridge.py`)
- Durable production jobs, cost estimates, budget hard stops
- Owner review workspace (checksum-bound approval)
- Mock providers only as explicit fallback / demos
- **YouTube publish via Upload-Post** (same integration as classic MPT)
- Automation modes (default **Assisted**; auto-publish off)
- Long-form (default 5–8 min) and Shorts formats
- Localization stubs and analytics snapshots
- Implementation Status page (honest P0/P1/P2 backlog)

## YouTube setup (required for real channel publish)

In `config.toml` / WebUI settings:

```toml
upload_post_enabled = true
upload_post_api_key = "..."
upload_post_username = "..."
upload_post_platforms = ["youtube"]
upload_post_youtube_privacy_status = "private"
upload_post_youtube_made_for_kids = true
```

Also configure a `video_source` (e.g. Pexels API keys) and FFmpeg so Studio→MPT can render.

## Data location

SQLite DB and studio assets live under `storage/studio/` (or `$MPT_HOME/storage/studio`).

## Configuration

See `.env.example` for YouTube OAuth and optional provider placeholders. Existing MPT `config.toml` LLM/TTS keys are reused when available.
