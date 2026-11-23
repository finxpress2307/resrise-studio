# Resrise Studio - Agent Guidelines

## Architecture Overview
Resrise Studio is an autonomous multi-creator social media operations engine managing:
- `@avanyamehra` (Virtual high-fashion/editorial muse)
- `@mairamehraofficial` (Saree & ethnic elegance muse)
- `@iamgagankumar` (Menswear, tailoring, grooming)
- `@resrise` (Creative agency / production house)
- `@gagankumarrocks` (Founder & media entrepreneur)

## Core Tools (`scripts/`)
- `login.py`: One-time desktop Chrome login launcher per account.
- `ig_browsing.py` / `ig_network_engager.py`: Feed engagement with vision model inspection and anti-repetition memory.
- `ig_replier.py`: Comment replier with per-user and global 72h anti-repetition guard.
- `update_bios.py`: Updates compliant bios under 150 characters with native Telegram funnel links.
- `swarm_orchestrator.py`: Draft generator and multi-image post creator.
- `approval_dashboard.py`: Web dashboard on port 8500 for reviewing and scheduling drafts.
- `ig_publisher.py`: Automated Playwright publisher with native "Made with AI" toggle.

## Prompts & AI Media
- See `FLOW_AND_CRAFT_PROMPTS.md` for:
  - Universal Google Flow Image Prompt
  - Universal Omni Model Video Prompt
  - 2-Step Motion Replication Workflow
  - CRAFT 10-slide photo dump carousel framework
