================================================================================
CARNATION v2.5 — REAL-TIME ALERTS + WEEKLY DIGEST + EMERGING COMPETITOR DETECTION
================================================================================

Welcome to Carnation — your competitive intelligence system.

(Formerly called "Competitor Scout")

WHAT YOU'VE GOT:
================

✅ Real-time Slack alerts to #competitor-watch when competitors move
✅ Weekly digest summarizing all changes (Monday 9 AM AEST)
✅ 🌹 Automatic detection of emerging competitors & competitive threats
✅ High-level format (1-2 sentences + links)
✅ Automatic change detection (no false alerts)
✅ Multiple deployment options (manual, cron, GitHub Actions)

MONITORS 6 KNOWN COMPETITORS:
=============================

• LangChain        (Medium threat) — Framework layer only
• Composio         (High threat)   — Public APIs only
• Workato          (Medium threat) — Cloud data routing
• Membrane         (High threat)   — Private APIs but early stage
• Paragon          (Low threat)    — Embedded integrations
• Prismatic        (Medium threat) — iPaaS + agents

PLUS: Automatically scans for emerging competitors in your space

YOUR COMPETITIVE EDGES:
=======================

✓ Pontil = Infrastructure-level API enablement (LangChain is just a framework)
✓ Pontil = Private backend SDK generation (Composio is public APIs only)
✓ Pontil = On-prem execution = compliance advantage (Workato is cloud-based)
✓ Pontil = Proven enterprise GTM (Membrane is early stage)
✓ Pontil = Only player doing this at scale (early mover advantage)

FILES YOU HAVE:
===============

GETTING STARTED:
1. 00_READ_THIS_FIRST.txt      ← Read this first!
2. START_HERE.md                ← 9-step setup guide (15-20 min)
3. CARNATION_BRANDING.md        ← What changed with the new name
4. QUICK_START.md               ← Command reference

THE SYSTEM:
5. carnation.py                 ← The agent (run this)
6. INTEGRATION_CHECKLIST.md     ← Verify everything configured
7. SLACK_WEBHOOK_SETUP.md       ← How to create Slack webhook
8. SLACK_SETUP.md               ← Detailed Slack integration

DOCUMENTATION:
9. RELEASE_NOTES.md             ← What's new in v2.5
10. NEW_COMPETITOR_DETECTION.md ← Emerging competitor scanning
11. TIMEZONE_GUIDE.md           ← Timezone conversion for cron
12. MONDAY_9AM_AEST_SCHEDULE.txt ← Weekly schedule reference
13. COMPETITOR_SCOUT_GUIDE.md   ← Advanced customisation
14. Other guides (VISUAL_GUIDE.txt, etc.)

QUICKEST PATH TO SUCCESS:
=========================

1. Open: START_HERE.md
2. Follow steps 1-9 in order (15-20 minutes total)
3. Check #competitor-watch for alerts
4. Done! Competitive intelligence is flowing.

KEY COMMANDS:
=============

# Run Carnation
python3 carnation.py

# Test without sending to Slack
python3 carnation.py --dry-run

# Monitor one competitor
python3 carnation.py --competitor composio

# List all tracked competitors
python3 carnation.py --list

SCHEDULE:
=========

Every MONDAY at 9:00 AM AEST (Sydney Time)
Cron: 0 9 * * 1

Your weekly competitive intelligence report posts to #competitor-watch

SETUP REQUIREMENTS:
==================

• Anthropic API key (get at console.anthropic.com)
• Slack workspace access (to create webhook)
• Python 3.9+ installed
• Terminal access

ESTIMATED TIME:
===============

Setup:       15-20 minutes
First run:   2 minutes
Automation:  5-15 minutes (optional)

Total to fully operational: ~30 minutes

WHAT YOU'LL SEE IN SLACK:
========================

Real-Time Alert (when changes detected):
  🎯 Composio: Announced 50 new integrations
  Threat Level: HIGH
  [clickable link]

Real-Time Alert (when new competitor discovered):
  🚨 NEW COMPETITOR DETECTED: StartupXYZ
  What They Do: Private API SDK auto-generation
  Threat Level: HIGH
  [clickable link]

Weekly Digest (Monday 9 AM AEST):
  📋 Weekly Competitive Intelligence Report
  
  🎯 Competitive Moves (existing competitors)
  - Composio: Announced 50 new integrations — [link]
  - Workato: Released on-prem option — [link]
  
  🚨 New Competitive Threats (emerging competitors)
  - StartupXYZ: Private API enablement — HIGH THREAT
  
  🚀 Most Important Threat
  StartupXYZ entry is the biggest threat.
  
  📋 Recommended Action
  Brief sales team. Review roadmap impact.

If no changes detected during the week: Silent (no Slack spam)

NEXT STEPS:
===========

1. Download all files above
2. Open START_HERE.md
3. Follow the 9 steps (in order)
4. Check #competitor-watch for messages
5. Share results with your leadership team

SUPPORT:
========

✓ Setup help                    → START_HERE.md or SLACK_WEBHOOK_SETUP.md
✓ Name/branding questions       → CARNATION_BRANDING.md
✓ New competitor detection help → NEW_COMPETITOR_DETECTION.md
✓ Verify config                 → INTEGRATION_CHECKLIST.md
✓ Quick reference               → QUICK_START.md
✓ Deep customisation            → COMPETITOR_SCOUT_GUIDE.md
✓ Visual walkthrough             → VISUAL_GUIDE.txt
✓ Troubleshooting               → SLACK_SETUP.md (Troubleshooting section)

================================================================================
Ready to get started? Open START_HERE.md and follow the steps.
================================================================================
