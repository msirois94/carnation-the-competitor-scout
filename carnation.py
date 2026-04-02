#!/usr/bin/env python3
"""
Carnation v2.0 — With Slack Integration
Monitors competitor websites and sends:
  1. Real-time Slack alerts when changes are detected
  2. Weekly digest summary of all competitive moves

Usage:
  python3 carnation.py                  # Full cycle + Slack alerts + weekly digest
  python3 carnation.py --competitor composio  # Monitor single competitor
  python3 carnation.py --list           # List tracked competitors
  python3 carnation.py --dry-run        # Test without sending Slack messages

Environment Variables:
  ANTHROPIC_API_KEY      - Required. Anthropic API key
  SLACK_WEBHOOK_URL      - Required. Slack incoming webhook for #competitor-watch
                           Get this from Slack → Settings → Integrations → Incoming Webhooks
"""

import os
import sys
import json
import hashlib
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Check for Anthropic SDK
try:
    import anthropic
except ImportError:
    print("❌ Error: anthropic package not found.")
    print("Install it with: pip install anthropic --break-system-packages")
    sys.exit(1)

# ============================================================================
# CONFIG
# ============================================================================

COMPETITORS = {
    "LangChain": {
        "url": "https://blog.langchain.dev",
        "type": "framework",
        "focus": ["product updates", "pricing", "agent capabilities"],
        "threat_level": "medium",
    },
    "Composio": {
        "url": "https://composio.dev/blog",
        "type": "direct_competitor",
        "focus": ["integrations", "pricing", "API coverage"],
        "threat_level": "high",
    },
    "Workato": {
        "url": "https://www.workato.com/the-connector",
        "type": "adjacent_competitor",
        "focus": ["enterprise features", "deployment", "compliance"],
        "threat_level": "medium",
    },
    "Membrane": {
        "url": "https://membrane.io",
        "type": "direct_competitor",
        "focus": ["private APIs", "deployment model", "pricing"],
        "threat_level": "high",
    },
    "Paragon": {
        "url": "https://www.useparagon.com/blog",
        "type": "adjacent_competitor",
        "focus": ["embedded integrations", "pricing", "customer stories"],
        "threat_level": "low",
    },
    "Prismatic": {
        "url": "https://prismatic.io/blog",
        "type": "adjacent_competitor",
        "focus": ["iPaaS features", "customer stories", "pricing"],
        "threat_level": "medium",
    },
}

# Search queries for discovering new potential competitors
NEW_COMPETITOR_SEARCHES = [
    "private API enablement platform",
    "API SDK auto-generation",
    "internal API management SaaS",
    "backend API abstraction layer",
    "agentic API integration platform 2025",
    "private backend API connector",
    "on-prem API gateway agent integration",
    "enterprise API enablement startup",
]

SNAPSHOT_DIR = Path("competitor_snapshots")
SNAPSHOT_DIR.mkdir(exist_ok=True)

# ============================================================================
# SLACK INTEGRATION
# ============================================================================

def get_slack_webhook() -> Optional[str]:
    """Get Slack webhook URL from environment."""
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        print("\n⚠️  Warning: SLACK_WEBHOOK_URL not set.")
        print("   Set it with: export SLACK_WEBHOOK_URL='https://hooks.slack.com/...'")
        print("   Or alerts will not be sent to Slack.\n")
    return webhook

def post_to_slack(webhook_url: str, message: Dict, dry_run: bool = False) -> bool:
    """Post a message to Slack. Returns True if successful."""
    if not webhook_url:
        return False
    
    if dry_run:
        print(f"\n   [DRY RUN] Would post to Slack:")
        print(f"   {json.dumps(message, indent=2)}\n")
        return True
    
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Failed to post to Slack: {str(e)}")
        return False

def alert_new_competitor_move(competitor: str, move: str, url: str, 
                              webhook_url: Optional[str], dry_run: bool = False) -> bool:
    """
    Send a real-time alert to Slack when a competitor move is detected.
    
    Format: "🎯 Composio: Announced 50 new integrations — https://..."
    """
    if not webhook_url:
        return False
    
    # Color code by threat level
    threat_level = COMPETITORS.get(competitor, {}).get("threat_level", "medium")
    color_map = {"high": "#FF6B6B", "medium": "#FFA500", "low": "#4CAF50"}
    color = color_map.get(threat_level, "#808080")
    
    message = {
        "channel": "#competitor-watch",
        "username": "Pontil Competitor Scout",
        "icon_emoji": ":mag:",
        "attachments": [
            {
                "color": color,
                "title": f"🎯 {competitor}: {move}",
                "title_link": url,
                "text": f"Threat Level: <b>{threat_level.upper()}</b>",
                "footer": "Competitor Watch",
                "ts": int(datetime.now().timestamp()),
            }
        ]
    }
    
    return post_to_slack(webhook_url, message, dry_run=dry_run)

def post_weekly_summary_to_slack(summary: str, webhook_url: Optional[str], 
                                 dry_run: bool = False) -> bool:
    """Post the weekly digest summary to Slack."""
    if not webhook_url:
        return False
    
    # Break summary into sections for better formatting
    sections = summary.split("\n\n")
    
    message = {
        "channel": "#competitor-watch",
        "username": "Pontil Competitor Scout",
        "icon_emoji": ":mag:",
        "text": "📋 *Weekly Competitor Scout Report*",
        "attachments": [
            {
                "color": "#0099FF",
                "title": "Weekly Competitive Intelligence",
                "text": summary[:3000],  # Slack has char limits per attachment
                "footer": "Pontil Competitor Watch",
                "ts": int(datetime.now().timestamp()),
            }
        ]
    }
    
    return post_to_slack(webhook_url, message, dry_run=dry_run)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_snapshot_path(competitor: str) -> Path:
    """Get the path to a competitor's latest snapshot."""
    return SNAPSHOT_DIR / f"{competitor.lower()}_latest.json"

def get_all_snapshots() -> List[Path]:
    """Get all existing snapshots."""
    return sorted(SNAPSHOT_DIR.glob("*_latest.json"))

def hash_content(content: str) -> str:
    """Generate a hash of content for change detection."""
    return hashlib.md5(content.encode()).hexdigest()

def format_timestamp() -> str:
    """Return ISO timestamp."""
    return datetime.now().isoformat()

# ============================================================================
# FETCH & ANALYSIS
# ============================================================================

def scan_for_new_competitors(webhook_url: Optional[str], dry_run: bool = False) -> Dict:
    """
    Scan the web for potential new competitors in the API enablement space.
    Uses Claude to analyse search results and identify emerging threats.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    prompt = f"""You are a competitive intelligence analyst scanning for emerging competitors in the 
API enablement and agentic workflow space.

Search for potential new SaaS competitors in this space using these search angles:
{json.dumps(NEW_COMPETITOR_SEARCHES, indent=2)}

Based on your knowledge of the market as of March 2026, identify:

1. **New Startups** that have recently launched or been announced:
   - Product: What do they do?
   - Funding: Any recent funding announcements?
   - Positioning: How are they positioning their solution?
   - Threat Level: How much do they compete with Pontil's private API enablement?

2. **Existing Companies** releasing features that compete with Pontil:
   - Company name
   - Recent feature announcement
   - How it competes with Pontil
   - Threat level assessment

3. **Notable Launches or Pivots** in related spaces:
   - Companies pivoting into API enablement
   - New features from existing platforms that threaten Pontil's positioning

Format your response as JSON:

{{
  "scan_date": "YYYY-MM-DD",
  "new_startups": [
    {{
      "name": "...",
      "website": "...",
      "product": "description",
      "positioning": "their value prop",
      "funding_status": "bootstrapped|seed|series_a|etc",
      "threat_level": "high|medium|low",
      "threat_rationale": "why this is a threat",
      "key_move": "one sentence about their positioning"
    }}
  ],
  "feature_launches": [
    {{
      "company": "existing company",
      "feature": "feature announcement",
      "announcement_date": "YYYY-MM-DD",
      "threat_level": "high|medium|low",
      "threat_rationale": "how this competes",
      "key_move": "one sentence summary"
    }}
  ],
  "notable_pivots": [
    {{
      "company": "...",
      "pivot": "description of pivot",
      "threat_level": "high|medium|low"
    }}
  ],
  "summary": "Overall assessment of emerging competitive threats"
}}

Be realistic and specific. Only report genuinely emerging threats, not established players we already know about."""

    message = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text
    
    # Parse the response
    try:
        scan_results = json.loads(response_text)
    except json.JSONDecodeError:
        scan_results = {
            "scan_date": format_timestamp(),
            "error": "Could not parse scan results",
            "raw_response": response_text,
        }
    
    return scan_results

def check_new_competitors_for_changes() -> List[Dict]:
    """
    Compare latest new competitor scan to previous scan.
    Returns list of newly discovered competitors or significant changes.
    """
    scan_path = SNAPSHOT_DIR / "new_competitors_scan_latest.json"
    
    # Run the scan
    new_scan = scan_for_new_competitors(None)
    
    # Load previous scan if it exists
    previous_scan = None
    if scan_path.exists():
        with open(scan_path, 'r') as f:
            previous_scan = json.load(f)
    
    # Save current scan
    with open(scan_path, 'w') as f:
        json.dump(new_scan, f, indent=2)
    
    # Detect new competitors and threats
    new_threats = []
    
    if not previous_scan:
        # First scan - all are "new"
        for startup in new_scan.get("new_startups", []):
            new_threats.append({
                "type": "new_startup",
                "data": startup,
                "is_new": True,
            })
        for feature in new_scan.get("feature_launches", []):
            if feature.get("threat_level") == "high":
                new_threats.append({
                    "type": "feature_launch",
                    "data": feature,
                    "is_new": True,
                })
    else:
        # Compare to previous
        previous_startups = {s.get("name"): s for s in previous_scan.get("new_startups", [])}
        previous_features = {f.get("company"): f for f in previous_scan.get("feature_launches", [])}
        
        # Check for new startups
        for startup in new_scan.get("new_startups", []):
            if startup.get("name") not in previous_startups:
                new_threats.append({
                    "type": "new_startup",
                    "data": startup,
                    "is_new": True,
                })
        
        # Check for new feature threats
        for feature in new_scan.get("feature_launches", []):
            company_key = feature.get("company")
            if company_key not in previous_features and feature.get("threat_level") == "high":
                new_threats.append({
                    "type": "feature_launch",
                    "data": feature,
                    "is_new": True,
                })
    
    return new_threats

def alert_new_competitor_discovered(competitor_info: Dict, webhook_url: Optional[str], 
                                    dry_run: bool = False) -> bool:
    """Alert to Slack when a new competitor is discovered."""
    if not webhook_url:
        return False
    
    threat_level = competitor_info.get("threat_level", "medium")
    threat_colors = {"high": "#FF0000", "medium": "#FFA500", "low": "#FFD700"}
    color = threat_colors.get(threat_level, "#808080")
    
    if competitor_info.get("type") == "new_startup":
        startup = competitor_info.get("data", {})
        message = {
            "channel": "#competitor-watch",
            "username": "Pontil Competitor Scout",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 NEW COMPETITOR DETECTED: {startup.get('name', 'Unknown')}",
                    "title_link": startup.get("website", ""),
                    "fields": [
                        {"title": "What They Do", "value": startup.get("product", ""), "short": False},
                        {"title": "Positioning", "value": startup.get("positioning", ""), "short": False},
                        {"title": "Threat Level", "value": threat_level.upper(), "short": True},
                        {"title": "Funding Status", "value": startup.get("funding_status", "unknown"), "short": True},
                    ],
                    "text": f"🎯 {startup.get('key_move', '')}",
                    "footer": "Competitor Watch — New Threat Detection",
                    "ts": int(datetime.now().timestamp()),
                }
            ]
        }
    else:  # feature_launch
        feature = competitor_info.get("data", {})
        message = {
            "channel": "#competitor-watch",
            "username": "Pontil Competitor Scout",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color,
                    "title": f"⚠️  COMPETITIVE THREAT: {feature.get('company', '')}",
                    "fields": [
                        {"title": "Feature", "value": feature.get("feature", ""), "short": False},
                        {"title": "Threat", "value": feature.get("threat_rationale", ""), "short": False},
                        {"title": "Threat Level", "value": threat_level.upper(), "short": True},
                    ],
                    "text": f"🎯 {feature.get('key_move', '')}",
                    "footer": "Competitor Watch — Feature Launch Detection",
                    "ts": int(datetime.now().timestamp()),
                }
            ]
        }
    
    return post_to_slack(webhook_url, message, dry_run=dry_run)
    """Fetch competitor intelligence via Claude."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    prompt = f"""You are a competitive intelligence analyst researching {competitor}.

Company: {competitor}
Website: {url}
Focus areas: {', '.join(config['focus'])}
Type: {config['type']}

Provide a realistic intelligence snapshot. Describe:
1. **Recent announcements** (title, date, key theme) — only genuinely new things in the last 1-2 weeks
2. **Pricing model** (any recent changes?)
3. **Key product features** (new launches?)
4. **Messaging shifts** (changed positioning?)
5. **Obvious gaps** (what they don't do that Pontil does)
6. **Threat assessment** (how much is this a direct threat to Pontil?)

Format your response as JSON:
{{
  "competitor": "{competitor}",
  "intelligence_date": "YYYY-MM-DD",
  "recent_announcements": [
    {{"title": "...", "date": "YYYY-MM-DD", "url": "...", "theme": "..."}}
  ],
  "pricing_changes": "null or description of recent changes",
  "new_features": ["feature 1", "feature 2"],
  "messaging_shift": "null or description of any messaging change",
  "identified_gaps": ["gap 1", "gap 2"],
  "threat_assessment": {{
    "level": "high|medium|low",
    "specific_threat": "what could hurt Pontil most",
    "key_move": "one-sentence summary of the most important move"
  }}
}}

Be specific, realistic, and only report genuinely new developments."""

    message = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def save_snapshot(competitor: str, content: str) -> tuple[Dict, bool]:
    """
    Save a competitor snapshot and detect changes.
    Returns: (snapshot dict, changes_detected bool)
    """
    snapshot_path = get_snapshot_path(competitor)
    
    # Parse JSON response
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {
            "competitor": competitor,
            "error": "Could not parse JSON",
            "raw_content": content,
        }
    
    content_hash = hash_content(content)
    
    # Check for changes vs. previous snapshot
    changes_detected = False
    previous_data = None
    if snapshot_path.exists():
        with open(snapshot_path, 'r') as f:
            previous = json.load(f)
            previous_hash = previous.get("content_hash", "")
            previous_data = previous.get("data", {})
            if previous_hash and previous_hash != content_hash:
                changes_detected = True
    
    # Build snapshot object
    snapshot = {
        "competitor": competitor,
        "timestamp": format_timestamp(),
        "content_hash": content_hash,
        "changes_from_previous": changes_detected,
        "data": data,
    }
    
    # Save snapshot
    with open(snapshot_path, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return snapshot, changes_detected

def extract_key_move(snapshot: Dict) -> Optional[tuple[str, str]]:
    """
    Extract the single most important move from a snapshot.
    Returns: (move_description, url) or None
    """
    data = snapshot.get("data", {})
    
    # Check for recent announcements
    announcements = data.get("recent_announcements", [])
    if announcements and isinstance(announcements, list) and len(announcements) > 0:
        latest = announcements[0]
        if isinstance(latest, dict):
            title = latest.get("title", "New announcement")
            url = latest.get("url", data.get("competitor", "").replace(" ", "").lower() + ".com")
            return title, url
    
    # Check for pricing changes
    pricing = data.get("pricing_changes")
    if pricing and pricing != "null":
        return f"Pricing change: {pricing}", COMPETITORS.get(data.get("competitor"), {}).get("url", "")
    
    # Check for new features
    features = data.get("new_features", [])
    if features and isinstance(features, list) and len(features) > 0:
        return f"New feature: {features[0]}", COMPETITORS.get(data.get("competitor"), {}).get("url", "")
    
    # Fall back to key_move from threat assessment
    threat = data.get("threat_assessment", {})
    if isinstance(threat, dict):
        key_move = threat.get("key_move")
        if key_move:
            return key_move, COMPETITORS.get(data.get("competitor"), {}).get("url", "")
    
    return None

def generate_weekly_summary(snapshots: List[Dict], new_threats: List[Dict] = None) -> str:
    """Generate a weekly digest of only new/changed items, including new competitors."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # Filter to only snapshots with changes
    changed_snapshots = [s for s in snapshots if s.get("changes_from_previous")]
    
    new_threats = new_threats or []
    
    if not changed_snapshots and not new_threats:
        return "✅ *No competitive changes detected this week.* All competitors remain stable."
    
    snapshots_text = json.dumps(changed_snapshots, indent=2)
    threats_text = json.dumps(new_threats, indent=2)
    
    prompt = f"""You are the Head of Product Strategy at Pontil, an API enablement platform for agentic workflows.

You've received two types of competitive intelligence this week:

1. **Changes from existing competitors:**
{snapshots_text}

2. **New potential competitors discovered:**
{threats_text}

Create a *brief* weekly digest in this format:

## 🎯 Competitive Moves (Only New Changes)

For each competitor with changes, add ONE line + link:
- **Composio**: Announced 50 new integrations — [link]
- **Workato**: Released on-premises deployment option — [link]

## 🚨 New Competitive Threats

If any new competitors or significant competitive moves were discovered:
- **[Company Name]**: [One sentence about their threat] — Threat Level: [HIGH/MEDIUM/LOW]
- List any new startups discovered
- Flag any major feature launches from adjacent players

## 🚀 Most Important Threat
[One sentence about the single biggest competitive threat this week]

## 📋 Recommended Action
[One-sentence action for product/sales team]

Keep it HIGH LEVEL. Only report actual changes. Link to relevant resources.
Prioritise new competitor discoveries and high-threat feature launches."""

    message = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

# ============================================================================
# CLI & COMMANDS
# ============================================================================

def cmd_list_competitors():
    """List all tracked competitors."""
    print("\n📊 Pontil Competitor Scout — Tracked Competitors\n")
    for name, config in COMPETITORS.items():
        threat = config.get("threat_level", "unknown").upper()
        print(f"  {name:15} | Type: {config['type']:20} | Threat: {threat}")
    print()

def cmd_monitor_single(competitor_name: str, webhook_url: Optional[str], dry_run: bool = False):
    """Monitor a single competitor."""
    if competitor_name not in COMPETITORS:
        print(f"\n❌ Competitor '{competitor_name}' not found.")
        print(f"Available: {', '.join(COMPETITORS.keys())}\n")
        return
    
    config = COMPETITORS[competitor_name]
    print(f"\n📊 Monitoring {competitor_name}...")
    
    content = fetch_competitor_content(competitor_name, config["url"], config)
    snapshot, changes = save_snapshot(competitor_name, content)
    
    if changes:
        print(f"  ⚠️  Changes detected!")
        
        # Extract and alert the key move
        move_info = extract_key_move(snapshot)
        if move_info:
            move, url = move_info
            print(f"  📤 Sending Slack alert...")
            if alert_new_competitor_move(competitor_name, move, url, webhook_url, dry_run=dry_run):
                print(f"  ✅ Slack alert sent to #competitor-watch")
            else:
                print(f"  ℹ️  (Slack webhook not configured)")
    else:
        print(f"  ✓ No changes detected")
    
    print(f"  📄 Snapshot saved\n")

def cmd_run_full_cycle(webhook_url: Optional[str], dry_run: bool = False):
    """Run a full competitor monitoring cycle."""
    print(f"\n🔍 Competitor Scout — Full Cycle at {format_timestamp()}\n")
    
    snapshots = []
    changes_count = 0
    
    # Monitor existing competitors
    print("📊 Monitoring Existing Competitors:")
    for competitor, config in COMPETITORS.items():
        print(f"  📊 {competitor:15}", end=" ", flush=True)
        
        try:
            content = fetch_competitor_content(competitor, config["url"], config)
            snapshot, changes = save_snapshot(competitor, content)
            snapshots.append(snapshot)
            
            if changes:
                changes_count += 1
                print("⚠️  (NEW)", end=" ", flush=True)
                
                # Send real-time alert for this competitor
                move_info = extract_key_move(snapshot)
                if move_info and webhook_url:
                    move, url = move_info
                    alert_new_competitor_move(competitor, move, url, webhook_url, dry_run=dry_run)
            
            print("✓")
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
    
    print(f"\n✅ Fetched {len(snapshots)}/{len(COMPETITORS)} existing competitors\n")
    
    # Scan for new competitors
    print("🔎 Scanning for New Potential Competitors...")
    new_threats = check_new_competitors_for_changes()
    
    if new_threats:
        print(f"⚠️  Found {len(new_threats)} potential new threat(s):\n")
        for threat in new_threats:
            if threat.get("type") == "new_startup":
                startup = threat.get("data", {})
                print(f"  🚨 NEW: {startup.get('name')} ({startup.get('threat_level').upper()})")
                if webhook_url:
                    alert_new_competitor_discovered(threat, webhook_url, dry_run=dry_run)
            else:
                feature = threat.get("data", {})
                print(f"  ⚠️  THREAT: {feature.get('company')} — {feature.get('key_move')[:50]}...")
                if webhook_url:
                    alert_new_competitor_discovered(threat, webhook_url, dry_run=dry_run)
        print()
    else:
        print("✓ No new competitors detected\n")
    
    # Generate weekly summary
    if changes_count > 0 or new_threats:
        print("📝 Generating weekly summary...\n")
        summary = generate_weekly_summary(snapshots, new_threats)
        
        # Save summary
        summary_filename = f"weekly_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        summary_path = SNAPSHOT_DIR / summary_filename
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print(summary)
        print(f"\n📤 Posting weekly digest to Slack...\n")
        
        # Post to Slack
        if webhook_url:
            if post_weekly_summary_to_slack(summary, webhook_url, dry_run=dry_run):
                print(f"✅ Weekly digest posted to #competitor-watch\n")
            else:
                print(f"⚠️  Failed to post weekly digest to Slack\n")
        else:
            print(f"ℹ️  Slack webhook not configured (set SLACK_WEBHOOK_URL)\n")
        
        print(f"📄 Summary saved: {summary_path}\n")
    else:
        print("✅ No competitive changes this cycle. No summary needed.\n")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Competitor Scout v2.0 — Real-time Slack alerts + Weekly digest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Setup:
  export ANTHROPIC_API_KEY="sk-ant-..."
  export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

Examples:
  python3 carnation.py                    # Full cycle with Slack alerts
  python3 carnation.py --dry-run          # Test without sending Slack
  python3 carnation.py --competitor composio
  python3 carnation.py --list
        """)
    
    parser.add_argument("--list", action="store_true", help="List tracked competitors")
    parser.add_argument("--competitor", type=str, help="Monitor a specific competitor")
    parser.add_argument("--dry-run", action="store_true", help="Test without sending Slack messages")
    
    args = parser.parse_args()
    
    # Get Slack webhook
    webhook_url = get_slack_webhook()
    
    if args.list:
        cmd_list_competitors()
    elif args.competitor:
        cmd_monitor_single(args.competitor, webhook_url, dry_run=args.dry_run)
    else:
        cmd_run_full_cycle(webhook_url, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
