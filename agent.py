"""
PUMO Technovation - Autonomous Instagram Video Agent v4
=======================================================
Powered by Creatomate — handles everything:
- Stability AI generates visuals from prompts
- ElevenLabs generates voiceover per scene
- Bouncing captions auto-synced to voice
- Pan/zoom animations built into template
- 6 scenes, fully edited, rendered in the cloud

Our job: Claude writes the scripts + image prompts,
Creatomate renders, Upload-Post posts to Instagram.
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
CREATOMATE_API_KEY   = os.environ.get('CREATOMATE_API_KEY', '')
UPLOAD_POST_API_KEY  = os.environ.get('UPLOAD_POST_API_KEY', '')
INSTAGRAM_USERNAME   = 'Pumo_Profile'

CREATOMATE_TEMPLATE  = '0a352a32-f5fe-4526-b7c7-94bdcde05583'


# ============================================================
# COURSE ROTATION
# ============================================================
COURSES = {
    0: {
        "name": "Cybersecurity",
        "pain_point": "data breaches and hacking affecting companies daily",
        "outcome": "protect systems and build a career in one of the most in-demand tech fields",
        "visual_style": "dark dramatic cyberpunk tech, glowing screens, digital security"
    },
    1: {
        "name": "Cloud and DevOps",
        "pain_point": "companies struggling to modernise their outdated IT infrastructure",
        "outcome": "deploy and manage cloud systems that companies are desperate for",
        "visual_style": "futuristic data centre, glowing servers, blue tech aesthetic"
    },
    2: {
        "name": "AI and Prompt Engineering",
        "pain_point": "people losing jobs to AI because they don't know how to use it",
        "outcome": "use AI as a tool that makes you irreplaceable, not replaceable",
        "visual_style": "neural network, glowing AI brain, futuristic digital interface"
    },
    3: {
        "name": "Digital Marketing",
        "pain_point": "businesses wasting money on content nobody sees",
        "outcome": "run campaigns that reach real audiences and drive real results",
        "visual_style": "vibrant social media, phone screens, creative marketing energy"
    },
    4: {
        "name": "BIM and CAD",
        "pain_point": "construction projects failing due to poor digital planning",
        "outcome": "design buildings digitally before construction even begins",
        "visual_style": "3D architectural blueprint, modern building design, technical precision"
    },
    5: {
        "name": "Mechanical Design CAD/CAM",
        "pain_point": "manufacturers struggling to find skilled machine design talent",
        "outcome": "design parts and program machines used in real manufacturing",
        "visual_style": "mechanical engineering, precision gears, factory technology"
    },
    6: {
        "name": "Career Development",
        "pain_point": "fresh grads sending hundreds of applications with zero response",
        "outcome": "position yourself as the candidate employers actually call back",
        "visual_style": "confident professional, modern office, career success energy"
    },
}


# ============================================================
# STEP 1 — Generate 6 scene scripts + image prompts with Claude
# ============================================================
def generate_content():
    print("📝 Step 1: Claude is writing 6 scenes...")

    day    = datetime.utcnow().weekday()
    course = COURSES[day]

    prompt = f"""You are a viral Malaysian Instagram Reels content creator for PUMO Technovation, 
an IT training centre in Kuala Lumpur.

Course: {course['name']}
Problem it solves: {course['pain_point']}  
What students learn: {course['outcome']}
Visual style for AI images: {course['visual_style']}

Create a 6-scene 60-second Instagram Reel. Each scene = ~10 seconds of voiceover.

STRICT RULES:
- NO salary guarantees. NO "earn RM8000" type promises.
- Sound like a real Malaysian — conversational, not corporate.
- Use 1-2 natural BM words per scene (lah, kan, memang, betul ke, serius).
- Voiceover per scene = 2-3 sentences max, punchy, keeps viewer hooked.
- Scene 1: Hook — call out the real pain point, stop the scroll.
- Scene 2: Agitate — make the problem feel real and urgent.
- Scene 3: Introduce the solution — PUMO's course.
- Scene 4: What you actually learn — specific skills, real talk.
- Scene 5: Why now — HRD Corp claimable, employer can sponsor it.
- Scene 6: Soft CTA — DM PUMO or reach out to find out more. NO phone number spoken.
- Image prompts must be vivid, cinematic, 9:16 portrait format descriptions.

Return ONLY valid JSON, no markdown:

{{
  "scenes": [
    {{
      "scene": 1,
      "voiceover": "2-3 punchy sentences for scene 1",
      "image_prompt": "Vivid cinematic image description for Stability AI, {course['visual_style']}, 9:16 portrait, photorealistic"
    }},
    {{
      "scene": 2,
      "voiceover": "2-3 punchy sentences for scene 2",
      "image_prompt": "Vivid cinematic image description, {course['visual_style']}, 9:16 portrait, photorealistic"
    }},
    {{
      "scene": 3,
      "voiceover": "2-3 punchy sentences for scene 3",
      "image_prompt": "Vivid cinematic image description, {course['visual_style']}, 9:16 portrait, photorealistic"
    }},
    {{
      "scene": 4,
      "voiceover": "2-3 punchy sentences for scene 4",
      "image_prompt": "Vivid cinematic image description, {course['visual_style']}, 9:16 portrait, photorealistic"
    }},
    {{
      "scene": 5,
      "voiceover": "2-3 punchy sentences for scene 5. Mention HRD Corp claimable naturally.",
      "image_prompt": "Vivid cinematic image description, {course['visual_style']}, 9:16 portrait, photorealistic"
    }},
    {{
      "scene": 6,
      "voiceover": "2-3 punchy sentences. Soft CTA — DM or reach out to PUMO. No phone number.",
      "image_prompt": "Vivid cinematic image description, {course['visual_style']}, 9:16 portrait, photorealistic"
    }}
  ],
  "post_caption": "Instagram caption. Real Malaysian tone. Emojis. Max 200 chars. Soft CTA. End with: 📞 016-259 2727",
  "hashtags": "#pumotechnovation #KLtraining #hrdcorp #hrdcorpclaimable #malaysiajobs #techjobs #kerjaya #skilldevelopment #kualalumpur #malaysiatech",
  "hook": "Scene 1 first line — 8 words max"
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
            "max_tokens": 2000,
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
        print(f"   ✓ Scene {i+1}: {scene['voiceover'][:50]}...")

    return content


# ============================================================
# STEP 2 — Send to Creatomate for rendering
# Creatomate handles: AI images, voiceover, captions, animations
# ============================================================
def render_with_creatomate(content):
    print("🎬 Step 2: Sending to Creatomate for rendering...")

    scenes = content['scenes']

    modifications = {}
    for i, scene in enumerate(scenes[:6]):
        scene_num = i + 1
        modifications[f"Image-{scene_num}.source"]     = scene['image_prompt']
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
    print(f"   ⏳ Waiting for Creatomate to render...")
    print(f"   (This takes 2-5 minutes)")

    return render_id


# ============================================================
# STEP 3 — Poll Creatomate until render is complete
# ============================================================
def wait_for_render(render_id):
    print("⏳ Step 3: Waiting for render to complete...")

    max_attempts = 60   # 5 minutes max (60 x 5 seconds)
    attempts     = 0

    while attempts < max_attempts:
        time.sleep(10)  # check every 10 seconds
        attempts += 1

        response = requests.get(
            f"https://api.creatomate.com/v2/renders/{render_id}",
            headers={"Authorization": f"Bearer {CREATOMATE_API_KEY}"}
        )

        if response.status_code != 200:
            print(f"   ⚠️  Status check failed: {response.status_code}")
            continue

        render = response.json()
        status = render.get('status', '')
        print(f"   Status: {status} ({attempts * 10}s elapsed)")

        if status == 'succeeded':
            video_url = render.get('url', '')
            print(f"   ✓ Render complete!")
            print(f"   ✓ Video URL: {video_url}")
            return video_url

        elif status == 'failed':
            error = render.get('error_message', 'Unknown error')
            print(f"❌ Render failed: {error}")
            sys.exit(1)

    print("❌ Render timed out after 10 minutes")
    sys.exit(1)


# ============================================================
# STEP 4 — Download rendered video
# ============================================================
def download_video(video_url):
    print("📥 Step 4: Downloading rendered video...")

    response = requests.get(video_url, stream=True, timeout=60)
    video_path = "/tmp/pumo_final.mp4"

    with open(video_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"   ✓ Downloaded — {size_mb:.1f} MB")
    return video_path


# ============================================================
# STEP 5 — Post to Instagram via Upload-Post
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
    print("  🤖  PUMO Autonomous Instagram Agent v4")
    print(f"  📅  {datetime.utcnow().strftime('%A, %d %B %Y')} (UTC)")
    print("  🎬  Powered by Creatomate + Stability AI + ElevenLabs")
    print("=" * 52)

    required = {
        'ANTHROPIC_API_KEY':   ANTHROPIC_API_KEY,
        'CREATOMATE_API_KEY':  CREATOMATE_API_KEY,
        'UPLOAD_POST_API_KEY': UPLOAD_POST_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"❌ Missing secrets: {', '.join(missing)}")
        sys.exit(1)

    content   = generate_content()
    render_id = render_with_creatomate(content)
    video_url = wait_for_render(render_id)
    video_path = download_video(video_url)
    success   = post_to_instagram(video_path, content)

    print("\n" + "=" * 52)
    print("  ✅  DONE!" if success else "  ⚠️  Done with warnings.")
    print(f"  🎬  Course:  {content['course']['name']}")
    print(f"  🎣  Hook:    {content['hook']}")
    print(f"  📸  Posted:  Instagram Reels")
    print(f"  ✨  Engine:  Creatomate + Stability AI + ElevenLabs")
    print("=" * 52)


if __name__ == "__main__":
    main()
