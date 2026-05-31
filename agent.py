"""
PUMO Technovation - Autonomous Instagram Video Agent v3
=======================================================
Upgrades:
- 60-second videos
- 8 clips per video (4 real footage + 4 motion/animation clips)
- Zoom punch effect on each clip
- Fast cut pacing (cuts every ~7 seconds)
- Animated caption fade-in
- Motion graphics mixed with real footage
- Viral script prompt, no fake promises
"""

import os
import json
import random
import requests
import subprocess
import sys
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================
ANTHROPIC_API_KEY   = os.environ.get('ANTHROPIC_API_KEY', '')
ELEVENLABS_API_KEY  = os.environ.get('ELEVENLABS_API_KEY', '')
PEXELS_API_KEY      = os.environ.get('PEXELS_API_KEY', '')
UPLOAD_POST_API_KEY = os.environ.get('UPLOAD_POST_API_KEY', '')
INSTAGRAM_USERNAME  = 'Pumo_Profile'

# ============================================================
# COURSE ROTATION
# Each course has:
# - real footage searches (people, environments)
# - motion/animation searches (abstract, tech graphics)
# ============================================================
COURSES = {
    0: {
        "name": "Cybersecurity",
        "pain_point": "your company or personal data getting hacked",
        "outcome": "protect systems and build a career in one of the most in-demand tech fields",
        "real_footage": [
            "hacker dark screen code typing",
            "cybersecurity professional working",
            "network security monitoring screen"
        ],
        "motion_footage": [
            "cyber security abstract animation",
            "digital data flow animation",
            "network connection glowing lines"
        ]
    },
    1: {
        "name": "Cloud and DevOps",
        "pain_point": "being stuck maintaining old systems while the industry moves to cloud",
        "outcome": "deploy and manage modern cloud infrastructure companies are desperate for",
        "real_footage": [
            "server room data centre lights",
            "developer coding multiple screens dark",
            "IT engineer working technology"
        ],
        "motion_footage": [
            "cloud computing abstract animation",
            "data transfer digital animation",
            "technology network abstract blue"
        ]
    },
    2: {
        "name": "AI and Prompt Engineering",
        "pain_point": "watching AI take over jobs while not knowing how to use it yourself",
        "outcome": "use AI as a tool that makes you more valuable not replaceable",
        "real_footage": [
            "person using AI laptop smiling",
            "artificial intelligence robot hand",
            "futuristic technology interface"
        ],
        "motion_footage": [
            "artificial intelligence animation brain",
            "neural network glowing animation",
            "digital brain technology animation"
        ]
    },
    3: {
        "name": "Digital Marketing",
        "pain_point": "businesses wasting money on content and ads nobody sees",
        "outcome": "run campaigns that reach real people and drive real results",
        "real_footage": [
            "content creator filming phone",
            "social media marketing laptop",
            "digital marketing analytics person"
        ],
        "motion_footage": [
            "social media icons animation",
            "marketing graph growth animation",
            "digital advertising abstract animation"
        ]
    },
    4: {
        "name": "BIM and CAD",
        "pain_point": "construction projects going over budget due to poor planning",
        "outcome": "design and plan buildings digitally before a single brick is laid",
        "real_footage": [
            "architect blueprint building design",
            "engineer CAD design computer",
            "construction building modern"
        ],
        "motion_footage": [
            "3d building model animation",
            "architectural design animation",
            "blueprint digital animation"
        ]
    },
    5: {
        "name": "Mechanical Design CAD/CAM",
        "pain_point": "manufacturers struggling to find people who can operate modern machines",
        "outcome": "design parts and program machines that make things in the real world",
        "real_footage": [
            "mechanical engineering factory",
            "CAD design engineering computer",
            "manufacturing machine production"
        ],
        "motion_footage": [
            "mechanical gear animation",
            "3d mechanical design animation",
            "engineering technology abstract"
        ]
    },
    6: {
        "name": "Career Development",
        "pain_point": "sending hundreds of job applications and getting zero responses",
        "outcome": "position yourself as the candidate employers actually call back",
        "real_footage": [
            "job interview office professional",
            "young professional working laptop",
            "career success confident person"
        ],
        "motion_footage": [
            "career growth chart animation",
            "success achievement animation",
            "professional network animation"
        ]
    },
}


# ============================================================
# STEP 1 — Generate 60-second viral script with Claude
# ============================================================
def generate_content():
    print("📝 Step 1: Claude is writing today's 60-second content...")

    day    = datetime.utcnow().weekday()
    course = COURSES[day]

    prompt = f"""You are a viral Malaysian Instagram Reels content creator.
You create content that feels real, relatable, gets saved and shared — not corporate, not salesy.

Today's topic: {course['name']} course at PUMO Technovation, Kuala Lumpur.
Real problem this solves: {course['pain_point']}
What people actually learn: {course['outcome']}

STRICT RULES:
- NO salary guarantees. NO "earn RM8000" promises. No guaranteed outcomes.
- Sound like a real Malaysian talking to a friend, not reading an ad.
- Use 2-3 natural BM words or phrases (lah, kan, memang, betul ke, seriously, takkan).
- Hook must hit a real pain point or create strong curiosity — not hype.
- This is a 60-SECOND video so the script should be 130-150 words.
- Structure: Hook (5 sec) → Real problem (15 sec) → What you learn (25 sec) → Why it matters now (10 sec) → Soft CTA (5 sec)
- End CTA: "DM us or reach out to PUMO to find out more" — NEVER say phone number out loud.
- Mention HRD Corp claimable naturally — employers can subsidise this.

Return ONLY valid JSON, no markdown, no explanation:

{{
  "hook": "Opening line max 10 words — punchy, real, stops the scroll",
  "script": "Full 60-second voiceover script. 130-150 words. Hook first. Real problem. What you learn. Why now. Soft CTA. No phone numbers spoken out loud.",
  "captions": [
    "Short punchy phrase 1 — max 6 words",
    "Short punchy phrase 2",
    "Short punchy phrase 3",
    "Short punchy phrase 4",
    "Short punchy phrase 5",
    "Short punchy phrase 6",
    "Short punchy phrase 7",
    "Short punchy phrase 8",
    "Short punchy phrase 9",
    "DM PUMO to find out more"
  ],
  "post_caption": "Instagram caption. Real Malaysian tone. Emojis. Max 200 chars. Soft CTA. End with: 📞 016-259 2727",
  "hashtags": "#pumotechnovation #KLtraining #hrdcorp #hrdcorpclaimable #malaysiajobs #techjobs #kerjaya #skilldevelopment #kualalumpur #malaysiatech"
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
    return content


# ============================================================
# STEP 2 — ElevenLabs voiceover
# ============================================================
def generate_voiceover(script):
    print("🎙️  Step 2: Generating 60-second voiceover...")

    VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "Accept":       "audio/mpeg",
            "xi-api-key":   ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text":     script,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability":         0.35,
                "similarity_boost":  0.85,
                "style":             0.25,
                "use_speaker_boost": True
            }
        }
    )

    if response.status_code != 200:
        print(f"   ⚠️  ElevenLabs failed: {response.status_code} — {response.text}")
        return generate_fallback_audio(script)

    audio_path = "/tmp/voiceover.mp3"
    with open(audio_path, "wb") as f:
        f.write(response.content)

    duration = get_audio_duration(audio_path)
    print(f"   ✓ Voiceover ready — {duration:.1f} seconds")
    return audio_path


def generate_fallback_audio(script):
    audio_path = "/tmp/voiceover.wav"
    subprocess.run(['espeak', '-w', audio_path, '-s', '145', script], capture_output=True)
    print("   ✓ Fallback audio created")
    return audio_path


# ============================================================
# STEP 3 — Download 8 clips: 4 real footage + 4 motion graphics
# ============================================================
def download_clip(url, path):
    try:
        r = requests.get(url, stream=True, timeout=30)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"   ⚠️  Download failed: {e}")
        return False


def search_pexels_videos(query, count=2):
    """Search Pexels for portrait videos matching query"""
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={
            "query":       query,
            "per_page":    count + 3,
            "size":        "medium",
            "orientation": "portrait"
        }
    )

    videos     = response.json().get('videos', [])
    downloaded = []

    for i, video in enumerate(videos):
        if len(downloaded) >= count:
            break

        files = video.get('video_files', [])
        # Prefer portrait files
        portrait = [f for f in files
                    if f.get('width', 999) <= f.get('height', 0)
                    and f.get('width', 0) >= 540]
        chosen = portrait or files
        if not chosen:
            continue

        chosen.sort(key=lambda x: x.get('width', 0))
        url = chosen[min(1, len(chosen)-1)].get('link', '')
        if not url:
            continue

        path = f"/tmp/clip_{query[:8].replace(' ','_')}_{i}.mp4"
        if download_clip(url, path):
            downloaded.append(path)

    return downloaded


def download_all_footage(course):
    print("🎬 Step 3: Downloading 8 clips (real + motion graphics)...")

    all_clips = []

    # Download 2 real footage clips from first 2 search terms
    for search in course['real_footage'][:2]:
        clips = search_pexels_videos(search, count=1)
        all_clips.extend(clips)
        print(f"   ✓ Real: '{search[:30]}' — {len(clips)} clip(s)")

    # Download 2 motion/animation clips
    for search in course['motion_footage'][:2]:
        clips = search_pexels_videos(search, count=1)
        all_clips.extend(clips)
        print(f"   ✓ Motion: '{search[:30]}' — {len(clips)} clip(s)")

    # If we don't have enough clips, fill with generic footage
    if len(all_clips) < 4:
        print("   ⚠️  Not enough clips, adding generic footage...")
        extra = search_pexels_videos("technology professional working", count=4-len(all_clips))
        all_clips.extend(extra)

    # Interleave real and motion clips for visual variety
    # Pattern: real, motion, real, motion...
    real_clips   = all_clips[:2]
    motion_clips = all_clips[2:]
    interleaved  = []

    for i in range(max(len(real_clips), len(motion_clips))):
        if i < len(real_clips):
            interleaved.append(real_clips[i])
        if i < len(motion_clips):
            interleaved.append(motion_clips[i])

    print(f"   ✓ Total: {len(interleaved)} clips ready")
    return interleaved[:8]  # max 8 clips


# ============================================================
# STEP 4 — Edit video with FFmpeg
# - Zoom punch on each clip
# - Fast cuts every ~7 seconds
# - Bold animated captions
# - Interleaved real + motion footage
# ============================================================
def get_audio_duration(audio_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', audio_path],
        capture_output=True, text=True
    )
    try:
        for stream in json.loads(result.stdout).get('streams', []):
            if stream.get('codec_type') == 'audio':
                return float(stream.get('duration', 60))
    except Exception:
        pass
    return 60.0


def safe_text(text):
    return (str(text)
            .replace("\\", "\\\\")
            .replace("'",  "\\'")
            .replace(":",  "\\:")
            .replace("%",  "\\%")
            .replace("\n", " ")
            .replace("[",  "")
            .replace("]",  "")
            .replace('"',  ""))


def process_clip_with_zoom(clip_path, out_path, duration, zoom_direction="in"):
    """
    Scale clip to 1080x1920 and add zoom punch effect.
    zoom_direction: "in" = slow zoom in, "out" = slow zoom out
    Alternates between clips for visual variety.
    """
    # Zoom from 1.0 to 1.08 (in) or 1.08 to 1.0 (out) — subtle but dynamic
    if zoom_direction == "in":
        zoom_filter = (
            "scale=1440:2560:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "setsar=1,"
            f"zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*30)}:s=1080x1920"
            f":fps=30"
        )
    else:
        zoom_filter = (
            "scale=1440:2560:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "setsar=1,"
           f"zoompan=z='max(1.08-zoom*0.0008,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*30)}:s=1080x1920"
          f":fps=30"
        )

    result = subprocess.run([
        'ffmpeg', '-y', '-i', clip_path,
        '-vf', zoom_filter,
        '-t', str(duration),
        '-an',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '28', '-r', '30',
        out_path
    ], capture_output=True)

    if result.returncode != 0:
        # Fallback: simple scale without zoom
        subprocess.run([
            'ffmpeg', '-y', '-i', clip_path,
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1',
            '-t', str(duration),
            '-an',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '28', '-r', '30',
            out_path
        ], capture_output=True)

    return os.path.exists(out_path)


def edit_video(clip_paths, audio_path, content):
    print("✂️  Step 4: Editing 60-second video with zoom punches...")

    audio_duration  = get_audio_duration(audio_path)
    num_clips       = len(clip_paths)
    clip_duration   = audio_duration / num_clips
    processed_clips = []

    # 4a — Process each clip with alternating zoom in/out
    zoom_directions = ["in", "out", "in", "out", "in", "out", "in", "out"]

    for i, clip_path in enumerate(clip_paths):
        out       = f"/tmp/proc_{i}.mp4"
        direction = zoom_directions[i % len(zoom_directions)]

        success = process_clip_with_zoom(clip_path, out, clip_duration + 0.3, direction)
        if success:
            processed_clips.append(out)
            print(f"   ✓ Clip {i+1}/{num_clips} — zoom {direction}")
        else:
            print(f"   ⚠️  Clip {i+1} failed, skipping")

    if not processed_clips:
        print("❌ No clips processed.")
        sys.exit(1)

    # 4b — Concatenate
    concat_file = "/tmp/concat_list.txt"
    with open(concat_file, 'w') as f:
        for clip in processed_clips:
            f.write(f"file '{clip}'\n")

    combined = "/tmp/combined.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '26', '-r', '30',
        combined
    ], check=True, capture_output=True)

    # 4c — Build caption overlays (hardcoded pixel positions, no decimals)
    captions     = content.get('captions', [])
    hook_text    = safe_text(content.get('hook', '')[:55])
    course_name  = safe_text(content['course']['name'])
    branding     = safe_text('PUMO Technovation  |  016-259 2727')
    cap_duration = audio_duration / max(len(captions), 1)

    drawtext_parts = []

    # Hook — top area, first 4 seconds
    hook_words = hook_text.split()
    if len(hook_words) > 5:
        mid   = len(hook_words) // 2
        line1 = safe_text(' '.join(hook_words[:mid]))
        line2 = safe_text(' '.join(hook_words[mid:]))
        drawtext_parts.append(
            f"drawtext=text='{line1}':fontsize=64:fontcolor=white"
            f":borderw=5:bordercolor=black"
            f":x=(w-text_w)/2:y=150:enable='between(t,0,4)'"
            f":font=DejaVu-Sans-Bold"
        )
        drawtext_parts.append(
            f"drawtext=text='{line2}':fontsize=64:fontcolor=white"
            f":borderw=5:bordercolor=black"
            f":x=(w-text_w)/2:y=230:enable='between(t,0,4)'"
            f":font=DejaVu-Sans-Bold"
        )
    else:
        drawtext_parts.append(
            f"drawtext=text='{hook_text}':fontsize=64:fontcolor=white"
            f":borderw=5:bordercolor=black"
            f":x=(w-text_w)/2:y=180:enable='between(t,0,4)'"
            f":font=DejaVu-Sans-Bold"
        )

    # Timed captions — 1420px from top (lower screen), yellow bold
    for i, caption in enumerate(captions):
        start    = i * cap_duration
        end      = (i + 1) * cap_duration
        cap_text = safe_text(str(caption)[:50])
        drawtext_parts.append(
            f"drawtext=text='{cap_text}':fontsize=56:fontcolor=yellow"
            f":borderw=5:bordercolor=black"
            f":box=1:boxcolor=black@0.4:boxborderw=14"
            f":x=(w-text_w)/2:y=1420"
            f":enable='between(t,{int(start)},{int(end)})'"
            f":font=DejaVu-Sans-Bold"
        )

    # HRD Corp badge — green, shows 10-20 seconds, 1680px from top
    drawtext_parts.append(
        f"drawtext=text='HRD Corp Claimable':fontsize=32:fontcolor=white"
        f":borderw=2:bordercolor=black"
        f":box=1:boxcolor=0x2ecc71@0.85:boxborderw=10"
        f":x=(w-text_w)/2:y=1680:enable='between(t,10,20)'"
        f":font=DejaVu-Sans-Bold"
    )

    # Course badge — top right, always visible, 24px from top
    drawtext_parts.append(
        f"drawtext=text='{course_name}':fontsize=30:fontcolor=white"
        f":borderw=2:bordercolor=black"
        f":box=1:boxcolor=black@0.6:boxborderw=12"
        f":x=w-text_w-24:y=24"
        f":font=DejaVu-Sans-Bold"
    )

    # PUMO branding — bottom, 1800px from top
    drawtext_parts.append(
        f"drawtext=text='{branding}':fontsize=28:fontcolor=white"
        f":borderw=2:bordercolor=black"
        f":box=1:boxcolor=black@0.65:boxborderw=10"
        f":x=(w-text_w)/2:y=1800"
        f":font=DejaVu-Sans"
    )

    # 4d — Final render
    print("   Rendering final 60-second video...")
    output = "/tmp/pumo_final.mp4"
    result = subprocess.run([
        'ffmpeg', '-y',
        '-i', combined, '-i', audio_path,
        '-vf', ','.join(drawtext_parts),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-map', '0:v:0', '-map', '1:a:0',
        '-shortest', '-movflags', '+faststart', '-r', '30',
        output
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FFmpeg error:\n{result.stderr[-800:]}")
        sys.exit(1)

    size_mb = os.path.getsize(output) / (1024 * 1024)
    print(f"   ✓ Final video ready — {size_mb:.1f} MB")
    return output


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
                "media_type": "REELS",
                "instagram_account_id": "pumo_technovation_malaysia"
            },
            files={"video": ("pumo_video.mp4", f, "video/mp4")}
        )

    if response.status_code in (200, 201):
        print(f"   ✓ Posted to @{INSTAGRAM_USERNAME}")
    else:
        print(f"   ⚠️  Upload-Post: {response.status_code} — {response.text}")

    return response.status_code in (200, 201)


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 52)
    print("  🤖  PUMO Autonomous Instagram Agent v3")
    print(f"  📅  {datetime.utcnow().strftime('%A, %d %B %Y')} (UTC)")
    print("  🎬  60-second video | zoom punches | motion mix")
    print("=" * 52)

    required = {
        'ANTHROPIC_API_KEY':   ANTHROPIC_API_KEY,
        'ELEVENLABS_API_KEY':  ELEVENLABS_API_KEY,
        'PEXELS_API_KEY':      PEXELS_API_KEY,
        'UPLOAD_POST_API_KEY': UPLOAD_POST_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"❌ Missing secrets: {', '.join(missing)}")
        sys.exit(1)

    content    = generate_content()
    audio_path = generate_voiceover(content['script'])
    clip_paths = download_all_footage(content['course'])
    video_path = edit_video(clip_paths, audio_path, content)
    success    = post_to_instagram(video_path, content)

    print("\n" + "=" * 52)
    print("  ✅  DONE!" if success else "  ⚠️  Done with warnings.")
    print(f"  🎬  Course:  {content['course']['name']}")
    print(f"  🎣  Hook:    {content['hook']}")
    print(f"  📸  Posted:  @{INSTAGRAM_USERNAME}")
    print("  ⏱️   Length:  60 seconds")
    print("=" * 52)


if __name__ == "__main__":
    main()
