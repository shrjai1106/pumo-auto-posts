"""
PUMO Technovation - Autonomous Instagram Video Agent v5
=======================================================
- Pexels real HD video clips (no more Stability AI)
- Natural Malaysian English script (no fake BM)
- Creatomate handles editing, captions, voiceover
- ElevenLabs via Creatomate template
"""

import os
import json
import time
import random
import requests
import sys
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================
ANTHROPIC_API_KEY    = os.environ.get('ANTHROPIC_API_KEY', '')
CREATOMATE_API_KEY   = os.environ.get('CREATOMATE_API_KEY', '')
UPLOAD_POST_API_KEY  = os.environ.get('UPLOAD_POST_API_KEY', '')
PEXELS_API_KEY       = os.environ.get('PEXELS_API_KEY', '')
INSTAGRAM_USERNAME   = 'Pumo_Profile'
CREATOMATE_TEMPLATE  = '0a352a32-f5fe-4526-b7c7-94bdcde05583'


# ============================================================
# COURSE ROTATION
# Each course has specific Pexels search terms per scene
# Mix of real people + tech/environment shots
# ============================================================
COURSES = {
    0: {
        "name": "Cybersecurity",
        "pain_point": "businesses losing data to cyber attacks every single day",
        "outcome": "protect systems and build a career in one of the most in-demand tech fields",
        "pexels_searches": [
            "hacker computer dark",
            "cybersecurity professional",
            "data breach computer",
            "network security technology",
            "IT professional working",
            "technology career office"
        ]
    },
    1: {
        "name": "Cloud and DevOps",
        "pain_point": "companies stuck on outdated systems while competitors move to cloud",
        "outcome": "deploy and manage cloud infrastructure that every company needs right now",
        "pexels_searches": [
            "server room technology",
            "cloud computing developer",
            "software engineer coding",
            "data centre technology",
            "developer laptop coding",
            "technology career success"
        ]
    },
    2: {
        "name": "AI and Prompt Engineering",
        "pain_point": "people watching AI change every industry while not knowing how to use it",
        "outcome": "use AI tools that make you more valuable and harder to replace",
        "pexels_searches": [
            "artificial intelligence technology",
            "person using laptop AI",
            "technology future digital",
            "professional using computer",
            "innovation technology office",
            "career technology success"
        ]
    },
    3: {
        "name": "Digital Marketing",
        "pain_point": "businesses spending on content and ads that nobody actually sees",
        "outcome": "create campaigns that reach real audiences and drive real business results",
        "pexels_searches": [
            "social media marketing",
            "content creator phone",
            "digital marketing analytics",
            "marketing professional laptop",
            "social media phone scrolling",
            "marketing success business"
        ]
    },
    4: {
        "name": "BIM and CAD",
        "pain_point": "construction projects going over budget because of poor digital planning",
        "outcome": "design and plan buildings digitally before construction even begins",
        "pexels_searches": [
            "architect blueprint design",
            "construction building modern",
            "engineer CAD computer",
            "architecture design office",
            "building construction technology",
            "engineering career professional"
        ]
    },
    5: {
        "name": "Mechanical Design CAD/CAM",
        "pain_point": "manufacturers struggling to find skilled people who can design modern machines",
        "outcome": "design parts and program machines used in real manufacturing",
        "pexels_searches": [
            "mechanical engineering factory",
            "manufacturing machine production",
            "engineer design computer",
            "industrial technology machine",
            "engineering professional working",
            "manufacturing career technology"
        ]
    },
    6: {
        "name": "Career Development",
        "pain_point": "graduates sending hundreds of applications and hearing nothing back",
        "outcome": "position yourself as the candidate that employers actually want to hire",
        "pexels_searches": [
            "job interview professional",
            "young professional office",
            "career success confident",
            "resume laptop professional",
            "business meeting office",
            "career growth success"
        ]
    },
}


# ============================================================
# STEP 1 — Get real Pexels video URLs for each scene
# ============================================================
def get_pexels_video_url(search_term):
    """Search Pexels and return a direct HD portrait video URL"""
    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={
                "query":       search_term,
                "per_page":    8,
                "orientation": "portrait",
                "size":        "medium"
            },
            timeout=15
        )

        videos = response.json().get('videos', [])
        if not videos:
            # Fallback search
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={"query": "professional office technology", "per_page": 5, "orientation": "portrait"},
                timeout=15
            )
            videos = response.json().get('videos', [])

        if not videos:
            return None

        # Pick a random video from results for variety
        video = random.choice(videos[:5])
        files = video.get('video_files', [])

        # Prefer HD portrait files
        portrait = [f for f in files
                    if f.get('width', 999) <= f.get('height', 0)
                    and f.get('width', 0) >= 720]

        if not portrait:
            portrait = [f for f in files if f.get('width', 0) >= 540]

        if not portrait:
            portrait = files

        if not portrait:
            return None

        # Sort by quality — pick medium quality
        portrait.sort(key=lambda x: x.get('width', 0), reverse=True)
        chosen = portrait[min(1, len(portrait)-1)]
        return chosen.get('link', None)

    except Exception as e:
        print(f"   ⚠️  Pexels search failed for '{search_term}': {e}")
        return None


def get_all_pexels_videos(course):
    """Get 6 video URLs for the 6 scenes"""
    print("🎬 Step 2: Fetching HD video clips from Pexels...")
    video_urls = []

    for i, search in enumerate(course['pexels_searches'][:6]):
        url = get_pexels_video_url(search)
        if url:
            video_urls.append(url)
            print(f"   ✓ Scene {i+1}: '{search[:35]}' — got clip")
        else:
            # Use a generic fallback
            fallback = get_pexels_video_url("professional office")
            video_urls.append(fallback or "")
            print(f"   ⚠️  Scene {i+1}: using fallback clip")

    return video_urls


# ============================================================
# STEP 2 — Generate 6 scene scripts with Claude
# Natural Malaysian English — no fake BM
# ============================================================
def generate_content():
    print("📝 Step 1: Claude is writing 6 scenes...")

    day    = datetime.utcnow().weekday()
    course = COURSES[day]

    prompt = f"""You are a content writer for PUMO Technovation, an IT training centre in Kuala Lumpur, Malaysia.

Write a 6-scene 60-second Instagram Reel script for: {course['name']} course.
Real problem: {course['pain_point']}
What students learn: {course['outcome']}

VOICE & TONE RULES:
- Write in natural, clear Malaysian English — the way an educated Malaysian speaks to peers.
- NO Bahasa Malaysia words. NO "lah", "kan", "memang", "lor" or any BM slang.
- Sound genuine and direct — like a trusted friend giving honest career advice.
- Conversational but confident. Not corporate. Not robotic.
- Short sentences. High energy. Every line should make the viewer want to hear the next one.

CONTENT RULES:
- NO salary guarantees. NO "earn RM8000" type promises.
- Talk about real skills and real opportunities — let people draw their own conclusions.
- Scene 1: Hook — call out the real pain point in one punchy line. Stop the scroll.
- Scene 2: Agitate — make the problem feel urgent and real.
- Scene 3: Introduce PUMO's solution naturally.
- Scene 4: Specific skills students learn — make it concrete.
- Scene 5: Mention HRD Corp claimable naturally — employers can fund this.
- Scene 6: Soft CTA — reach out to PUMO to find out more. No phone number spoken.
- Each scene = 2-3 short sentences. Max 25 words per scene.

Return ONLY valid JSON, no markdown:

{{
  "scenes": [
    {{"scene": 1, "voiceover": "2-3 short punchy sentences"}},
    {{"scene": 2, "voiceover": "2-3 short punchy sentences"}},
    {{"scene": 3, "voiceover": "2-3 short punchy sentences"}},
    {{"scene": 4, "voiceover": "2-3 short punchy sentences"}},
    {{"scene": 5, "voiceover": "2-3 short punchy sentences. Mention HRD Corp claimable."}},
    {{"scene": 6, "voiceover": "2-3 short punchy sentences. Soft CTA to reach out to PUMO."}}
  ],
  "post_caption": "Instagram caption. Genuine Malaysian tone. Emojis. Max 200 chars. Ends with: 📞 016-259 2727",
  "hashtags": "#pumotechnovation #KLtraining #hrdcorp #hrdcorpclaimable #malaysiajobs #techjobs #kerjaya #skilldevelopment #kualalumpur #malaysiatech",
  "hook": "First line of scene 1 — max 8 words"
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
            "max_tokens": 1500,
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
    for i, scene in enumerate(content['scenes']):
        print(f"   ✓ Scene {i+1}: {scene['voiceover'][:55]}...")

    return content


# ============================================================
# STEP 3 — Send to Creatomate
# Pexels video URLs as sources + voiceover text
# ============================================================
def render_with_creatomate(content, video_urls):
    print("🎬 Step 3: Sending to Creatomate for rendering...")

    scenes = content['scenes']

    modifications = {}
    for i, scene in enumerate(scenes[:6]):
        scene_num = i + 1
        # Real Pexels video as background
        if i < len(video_urls) and video_urls[i]:
            modifications[f"Image-{scene_num}.source"] = video_urls[i]
        # Voiceover text — ElevenLabs in template handles TTS
        modifications[f"Voiceover-{scene_num}.source"] = scene['voiceover']

    payload = {
        "template_id":   CREATOMATE_TEMPLATE,
        "modifications": modifications
    }

    response = requests.post(
        "https://api.creatomate.com/v2/renders",
        headers={
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {CREATOMATE_API_KEY}"
        },
        json=payload
    )

    if response.status_code not in (200, 201, 202):
        print(f"❌ Creatomate error: {response.status_code} — {response.text}")
        sys.exit(1)

    renders = response.json()
    if isinstance(renders, list):
        render = renders[0]
    else:
        render = renders

    render_id = render.get('id', '')
    print(f"   ✓ Render started — ID: {render_id}")
    print(f"   ⏳ Creatomate is rendering (2-5 minutes)...")
    return render_id


# ============================================================
# STEP 4 — Poll until render complete
# ============================================================
def wait_for_render(render_id):
    print("⏳ Step 4: Waiting for render...")

    for attempt in range(60):
        time.sleep(10)

        response = requests.get(
            f"https://api.creatomate.com/v2/renders/{render_id}",
            headers={"Authorization": f"Bearer {CREATOMATE_API_KEY}"}
        )

        if response.status_code != 200:
            print(f"   ⚠️  Status check failed: {response.status_code}")
            continue

        render = response.json()
        status = render.get('status', '')
        print(f"   Status: {status} ({(attempt+1)*10}s elapsed)")

        if status == 'succeeded':
            video_url = render.get('url', '')
            print(f"   ✓ Render complete!")
            return video_url

        elif status == 'failed':
            print(f"❌ Render failed: {render.get('error_message', 'Unknown')}")
            sys.exit(1)

    print("❌ Timed out after 10 minutes")
    sys.exit(1)


# ============================================================
# STEP 5 — Download rendered video
# ============================================================
def download_video(video_url):
    print("📥 Step 5: Downloading rendered video...")

    response   = requests.get(video_url, stream=True, timeout=60)
    video_path = "/tmp/pumo_final.mp4"

    with open(video_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"   ✓ Downloaded — {size_mb:.1f} MB")
    return video_path


# ============================================================
# STEP 6 — Post to Instagram
# ============================================================
def post_to_instagram(video_path, content):
    print("📲 Step 6: Posting to Instagram...")

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
    print("  🤖  PUMO Autonomous Instagram Agent v5")
    print(f"  📅  {datetime.utcnow().strftime('%A, %d %B %Y')} (UTC)")
    print("  🎬  Pexels HD video + Creatomate + ElevenLabs")
    print("=" * 52)

    required = {
        'ANTHROPIC_API_KEY':   ANTHROPIC_API_KEY,
        'CREATOMATE_API_KEY':  CREATOMATE_API_KEY,
        'UPLOAD_POST_API_KEY': UPLOAD_POST_API_KEY,
        'PEXELS_API_KEY':      PEXELS_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"❌ Missing secrets: {', '.join(missing)}")
        sys.exit(1)

    content    = generate_content()
    video_urls = get_all_pexels_videos(content['course'])
    render_id  = render_with_creatomate(content, video_urls)
    video_url  = wait_for_render(render_id)
    video_path = download_video(video_url)
    success    = post_to_instagram(video_path, content)

    print("\n" + "=" * 52)
    print("  ✅  DONE!" if success else "  ⚠️  Done with warnings.")
    print(f"  🎬  Course:  {content['course']['name']}")
    print(f"  🎣  Hook:    {content['hook']}")
    print(f"  📸  Posted:  Instagram Reels")
    print(f"  🎥  Footage: Pexels HD")
    print("=" * 52)


if __name__ == "__main__":
    main()
