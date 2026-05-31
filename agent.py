"""
PUMO Technovation - Autonomous Instagram Video Agent v6
=======================================================
- Claude generates viral script
- Revid.ai V3 API renders full video:
  * Stock video footage
  * AI voiceover
  * Animated captions at bottom
  * 60 seconds
- Upload-Post posts to Instagram
"""

import os
import json
import time
import requests
import sys
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================
ANTHROPIC_API_KEY    = os.environ.get('ANTHROPIC_API_KEY', '')
REVID_API_KEY        = os.environ.get('REVID_API_KEY', '')
UPLOAD_POST_API_KEY  = os.environ.get('UPLOAD_POST_API_KEY', '')
INSTAGRAM_USERNAME   = 'Pumo_Profile'

# Revid V3 API endpoint
REVID_API_URL        = 'https://www.revid.ai/api/public/v3/create'
REVID_STATUS_URL     = 'https://www.revid.ai/api/public/v3/status'

# Voice ID from your Revid settings
REVID_VOICE_ID       = 'nPczCjzI2devNBz1zQrb'


# ============================================================
# COURSE ROTATION
# ============================================================
COURSES = {
    0: {
        "name": "Cybersecurity",
        "pain_point": "businesses losing data to cyber attacks every single day",
        "outcome": "protect systems and build a career in one of the most in-demand tech fields",
    },
    1: {
        "name": "Cloud and DevOps",
        "pain_point": "companies stuck on outdated systems while competitors move to cloud",
        "outcome": "deploy and manage cloud infrastructure that every company needs right now",
    },
    2: {
        "name": "AI and Prompt Engineering",
        "pain_point": "people watching AI change every industry without knowing how to use it",
        "outcome": "use AI tools that make you more valuable and harder to replace",
    },
    3: {
        "name": "Digital Marketing",
        "pain_point": "businesses spending on content and ads that nobody actually sees",
        "outcome": "create campaigns that reach real audiences and drive real results",
    },
    4: {
        "name": "BIM and CAD",
        "pain_point": "construction projects going over budget due to poor digital planning",
        "outcome": "design and plan buildings digitally before construction even begins",
    },
    5: {
        "name": "Mechanical Design CAD/CAM",
        "pain_point": "manufacturers struggling to find people who can design modern machines",
        "outcome": "design parts and program machines used in real manufacturing",
    },
    6: {
        "name": "Career Development",
        "pain_point": "graduates sending hundreds of applications and hearing nothing back",
        "outcome": "position yourself as the candidate employers actually want to hire",
    },
}


# ============================================================
# STEP 1 — Generate script + caption with Claude
# ============================================================
def generate_content():
    print("📝 Step 1: Claude is writing today's script...")

    day    = datetime.utcnow().weekday()
    course = COURSES[day]

    prompt = f"""You are a content writer for PUMO Technovation, an IT training centre in KL.

Write a 60-second Instagram Reel script for: {course['name']} course.
Real problem: {course['pain_point']}
What students learn: {course['outcome']}

RULES:
- Natural clear Malaysian English. NO BM words. NO lah, kan, lor.
- Sound like a trusted friend giving honest career advice.
- Short punchy sentences. High energy.
- NO salary guarantees. NO income promises.
- Mention HRD Corp claimable naturally in the middle.
- End with soft CTA: reach out to PUMO to find out more.
- Total script: 130-150 words. Under 60 seconds when spoken.

Return ONLY valid JSON, no markdown:

{{
  "script": "Full 60-second script here. 130-150 words.",
  "post_caption": "Instagram caption. Genuine tone. Emojis. Max 200 chars. Ends with: 📞 016-259 2727",
  "hashtags": "#pumotechnovation #KLtraining #hrdcorp #hrdcorpclaimable #malaysiajobs #techjobs #kerjaya #skilldevelopment #kualalumpur #malaysiatech",
  "hook": "First sentence — max 8 words, stops the scroll"
}}"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key":         ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json"
        },
        json={
            "model":      "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages":   [{"role": "user", "content": prompt}]
        }
    )

    raw = response.json()['content'][0]['text'].strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.split("```")[0]

    content           = json.loads(raw.strip())
    content['course'] = course

    print(f"   ✓ Course: {course['name']}")
    print(f"   ✓ Hook:   {content['hook']}")
    print(f"   ✓ Script: {content['script'][:80]}...")
    return content


# ============================================================
# STEP 2 — Send to Revid V3 API
# ============================================================
def create_revid_video(content):
    print("🎬 Step 2: Sending to Revid for rendering...")

    script   = content['script']
    course   = content['course']['name']

    payload = {
        "webhookUrl": "",           # empty — we'll poll instead
        "workflow":   "prompt-to-video",
        "source": {
            "durationSeconds": 60
        },
        "media": {
            "type":         "stock-video",
            "imageModel":   "good",
            "videoModel":   "base"
        },
        "voice": {
            "enabled":          True,
            "voiceId":          REVID_VOICE_ID,
            "speed":            1,
            "useLegacyModel":   False
        },
        "captions": {
            "enabled":  True,
            "preset":   "Wrap 1",
            "position": "bottom"
        },
        "options": {
            "promptTargetDuration": 60
        },
        # The actual script/prompt goes here
        "prompt": f"{script}\n\nContext: This is for PUMO Technovation, an IT training centre in Kuala Lumpur, Malaysia. Course topic: {course}. Use relevant professional visuals."
    }

    response = requests.post(
        REVID_API_URL,
        headers={
            "key":          REVID_API_KEY,
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(f"   Response status: {response.status_code}")
    print(f"   Response: {response.text[:300]}")

    if response.status_code not in (200, 201):
        print(f"❌ Revid error: {response.status_code} — {response.text}")
        sys.exit(1)

    result = response.json()
    pid    = result.get('pid') or result.get('id') or result.get('projectId', '')

    if not pid:
        print(f"❌ No project ID in response: {result}")
        sys.exit(1)

    print(f"   ✓ Revid project created — ID: {pid}")
    print(f"   ⏳ Rendering in progress (5-10 minutes)...")
    return pid


# ============================================================
# STEP 3 — Poll Revid until video is ready
# ============================================================
def wait_for_revid_video(pid):
    print("⏳ Step 3: Waiting for Revid to render...")

    for attempt in range(90):  # 15 minutes max
        time.sleep(10)

        response = requests.get(
            f"{REVID_STATUS_URL}/{pid}",
            headers={"key": REVID_API_KEY}
        )

        if response.status_code != 200:
            print(f"   ⚠️  Status check failed: {response.status_code}")
            continue

        result    = response.json()
        status    = result.get('status', '')
        video_url = result.get('videoUrl') or result.get('url') or result.get('downloadUrl', '')

        print(f"   Status: {status} ({(attempt+1)*10}s elapsed)")

        if status in ('completed', 'done', 'finished', 'succeeded') or video_url:
            if video_url:
                print(f"   ✓ Video ready!")
                return video_url
            else:
                print(f"   ⚠️  Status done but no URL yet, waiting...")
                continue

        elif status in ('failed', 'error'):
            error = result.get('error') or result.get('message', 'Unknown error')
            print(f"❌ Revid render failed: {error}")
            sys.exit(1)

    print("❌ Timed out after 15 minutes")
    sys.exit(1)


# ============================================================
# STEP 4 — Download video
# ============================================================
def download_video(video_url):
    print("📥 Step 4: Downloading video...")

    response   = requests.get(video_url, stream=True, timeout=120)
    video_path = "/tmp/pumo_final.mp4"

    with open(video_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"   ✓ Downloaded — {size_mb:.1f} MB")
    return video_path


# ============================================================
# STEP 5 — Post to Instagram
# ============================================================
def post_to_instagram(video_path, content):
    print("📲 Step 5: Posting to Instagram...")

    full_cap = f"{content['post_caption']}\n\n{content['hashtags']}"

    with open(video_path, 'rb') as f:
        response = requests.post(
            "https://api.upload-post.com/api/upload",
            headers={"Authorization": f"Apikey {UPLOAD_POST_API_KEY}"},
            data={
                "title":      full_cap,
                "user":       INSTAGRAM_USERNAME,
                "platform[]": "instagram",
                "media_type": "REELS"
            },
            files={"video": ("pumo_video.mp4", f, "video/mp4")}
        )

    if response.status_code in (200, 201):
        print(f"   ✓ Posted to Instagram @{INSTAGRAM_USERNAME}")
    else:
        print(f"   ⚠️  Upload-Post: {response.status_code} — {response.text}")

    return response.status_code in (200, 201)


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 52)
    print("  🤖  PUMO Autonomous Instagram Agent v6")
    print(f"  📅  {datetime.utcnow().strftime('%A, %d %B %Y')} (UTC)")
    print("  🎬  Revid.ai V3 — Stock Video + Voice + Captions")
    print("=" * 52)

    required = {
        'ANTHROPIC_API_KEY':   ANTHROPIC_API_KEY,
        'REVID_API_KEY':       REVID_API_KEY,
        'UPLOAD_POST_API_KEY': UPLOAD_POST_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"❌ Missing secrets: {', '.join(missing)}")
        sys.exit(1)

    content    = generate_content()
    pid        = create_revid_video(content)
    video_url  = wait_for_revid_video(pid)
    video_path = download_video(video_url)
    success    = post_to_instagram(video_path, content)

    print("\n" + "=" * 52)
    print("  ✅  DONE!" if success else "  ⚠️  Done with warnings.")
    print(f"  🎬  Course:  {content['course']['name']}")
    print(f"  🎣  Hook:    {content['hook']}")
    print(f"  📸  Posted:  Instagram Reels")
    print(f"  🎥  Engine:  Revid.ai")
    print("=" * 52)


if __name__ == "__main__":
    main()
