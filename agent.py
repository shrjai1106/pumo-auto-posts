"""
PUMO Technovation - Autonomous Instagram Video Agent
=====================================================
What this does fully automatically every day:
  1. Claude AI writes a 30-second script + caption for today's PUMO course
  2. ElevenLabs turns the script into a voiceover (AI voice)
  3. Pexels API downloads free stock video clips matching the topic
  4. FFmpeg edits everything: clips + voiceover + captions + PUMO branding
  5. Upload-Post API posts the video directly to Instagram

Zero human input needed after setup.
Cost: ~RM15/month (Anthropic API only — everything else is free)
"""

import os
import json
import requests
import subprocess
import sys
from datetime import datetime


# ============================================================
# CONFIGURATION — all values come from GitHub Secrets
# ============================================================
ANTHROPIC_API_KEY   = os.environ.get('ANTHROPIC_API_KEY', '')
ELEVENLABS_API_KEY  = os.environ.get('ELEVENLABS_API_KEY', '')
PEXELS_API_KEY      = os.environ.get('PEXELS_API_KEY', '')
UPLOAD_POST_API_KEY = os.environ.get('UPLOAD_POST_API_KEY', '')

# Your Upload-Post username for Instagram
INSTAGRAM_USERNAME  = 'pumo_technovatio_malaysia'


# ============================================================
# COURSE ROTATION — different topic every day of the week
# ============================================================
COURSES = {
    0: { "name": "Cybersecurity",             "keywords": "cybersecurity hacking technology security" },
    1: { "name": "Cloud and DevOps",          "keywords": "cloud computing servers data centre" },
    2: { "name": "AI and Prompt Engineering", "keywords": "artificial intelligence robot technology future" },
    3: { "name": "Digital Marketing",         "keywords": "social media marketing laptop creative" },
    4: { "name": "BIM and CAD",               "keywords": "construction engineering architecture building" },
    5: { "name": "Mechanical Design CAD/CAM", "keywords": "mechanical engineering factory manufacturing" },
    6: { "name": "Career Tips Malaysia",      "keywords": "office professional career job interview" },
}


# ============================================================
# STEP 1 — Generate script + caption with Claude
# ============================================================
def generate_content():
    print("📝 Step 1: Claude is writing today's content...")

    day    = datetime.utcnow().weekday()
    course = COURSES[day]

    prompt = f"""You are a viral Instagram Reels content creator for PUMO Technovation,
an HRD Corp-registered IT training centre in Brickfields, Kuala Lumpur, Malaysia.

Today's course topic: {course['name']}

Return ONLY a valid JSON object. No markdown. No explanation. Just the JSON.

{{
  "hook": "One punchy opening line that stops scrolling. Max 10 words. English or BM.",
  "script": "30-second spoken voiceover script. Conversational Malaysian English with 1-2 natural BM phrases. Strong hook at start. Mention HRD Corp claimable. End with call to action to contact PUMO at 016-259 2727. Under 90 words. No stage directions.",
  "captions": [
    "Short sentence 1 (max 8 words)",
    "Short sentence 2",
    "Short sentence 3",
    "Short sentence 4",
    "Short sentence 5",
    "Call to action"
  ],
  "post_caption": "Instagram caption with emojis. Engaging. Max 180 chars. Call to action. Include 016-259 2727.",
  "hashtags": "#pumotechnovation #KLtraining #hrdcorp #hrdcorpclaimable #malaysiajobs #kerjaya #techjobs #skilldevelopment #kualalumpur",
  "pexels_search": "3-word search for relevant portrait stock footage"
}}"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key":         ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json"
        },
        json={
            "model":    "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    raw = response.json()['content'][0]['text'].strip()

    # Strip markdown fences if present
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
# STEP 2 — Generate AI voiceover with ElevenLabs (free tier)
# ============================================================
def generate_voiceover(script):
    print("🎙️  Step 2: ElevenLabs is generating the voiceover...")

    VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice — clear and professional

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "Accept":       "audio/mpeg",
            "xi-api-key":   ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text":     script,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability":        0.55,
                "similarity_boost": 0.75
            }
        }
    )

    if response.status_code != 200:
        print(f"   ⚠️  ElevenLabs failed — using fallback TTS")
        return generate_fallback_audio(script)

    audio_path = "/tmp/voiceover.mp3"
    with open(audio_path, "wb") as f:
        f.write(response.content)

    duration = get_audio_duration(audio_path)
    print(f"   ✓ Voiceover ready — {duration:.1f} seconds")
    return audio_path


def generate_fallback_audio(script):
    """System TTS fallback if ElevenLabs fails"""
    audio_path = "/tmp/voiceover.wav"
    subprocess.run(
        ['espeak', '-w', audio_path, '-s', '145', script],
        capture_output=True
    )
    print("   ✓ Fallback audio created")
    return audio_path


# ============================================================
# STEP 3 — Download free stock footage from Pexels
# ============================================================
def download_stock_footage(search_term, count=4):
    print(f"🎬 Step 3: Downloading stock footage for '{search_term}'...")

    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={
            "query":       search_term,
            "per_page":    count + 2,
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
        portrait_files = [
            f for f in files
            if f.get('width', 999) <= f.get('height', 0)
            and f.get('width', 0) >= 540
        ]
        chosen = portrait_files or files
        if not chosen:
            continue

        chosen.sort(key=lambda x: x.get('width', 0))
        video_url = chosen[min(1, len(chosen)-1)].get('link', '')
        if not video_url:
            continue

        try:
            clip_path = f"/tmp/clip_{i}.mp4"
            r = requests.get(video_url, stream=True, timeout=30)
            with open(clip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded.append(clip_path)
            print(f"   ✓ Clip {len(downloaded)}/{count} downloaded")
        except Exception as e:
            print(f"   ⚠️  Clip {i} failed: {e}")

    if not downloaded:
        print("   ⚠️  No clips found — retrying with broader search...")
        return download_stock_footage("office technology people", count)

    return downloaded


# ============================================================
# STEP 4 — Edit video with FFmpeg
#   - Scale clips to 1080x1920 (9:16 — Instagram Reels format)
#   - Trim clips to match voiceover length
#   - Concatenate clips
#   - Add voiceover
#   - Burn in timed captions
#   - Add PUMO branding
# ============================================================
def get_audio_duration(audio_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json',
         '-show_streams', audio_path],
        capture_output=True, text=True
    )
    try:
        for stream in json.loads(result.stdout).get('streams', []):
            if stream.get('codec_type') == 'audio':
                return float(stream.get('duration', 35))
    except Exception:
        pass
    return 35.0


def safe_text(text):
    """Escape special characters for ffmpeg drawtext"""
    return (text
            .replace("\\", "\\\\")
            .replace("'",  "\\'")
            .replace(":",  "\\:")
            .replace("%",  "\\%")
            .replace("\n", " "))


def edit_video(clip_paths, audio_path, content):
    print("✂️  Step 4: FFmpeg is editing the video...")

    audio_duration  = get_audio_duration(audio_path)
    clip_duration   = audio_duration / len(clip_paths)
    processed_clips = []

    # 4a — Scale and trim each clip to 1080x1920 portrait
    for i, clip_path in enumerate(clip_paths):
        out    = f"/tmp/proc_{i}.mp4"
        result = subprocess.run([
            'ffmpeg', '-y', '-i', clip_path,
            '-vf', (
                'scale=1080:1920:force_original_aspect_ratio=increase,'
                'crop=1080:1920,setsar=1'
            ),
            '-t', str(clip_duration + 0.5),
            '-an',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '28', '-r', '30',
            out
        ], capture_output=True)

        if result.returncode == 0:
            processed_clips.append(out)
            print(f"   ✓ Clip {i+1}/{len(clip_paths)} processed")

    if not processed_clips:
        print("❌ No clips processed. Exiting.")
        sys.exit(1)

    # 4b — Concatenate all processed clips
    concat_file = "/tmp/concat_list.txt"
    with open(concat_file, 'w') as f:
        for clip in processed_clips:
            f.write(f"file '{clip}'\n")

    combined = "/tmp/combined.mp4"
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '26', '-r', '30',
        combined
    ], check=True, capture_output=True)

    # 4c — Build caption + branding text overlays
    captions     = content.get('captions', [])
    hook_text    = safe_text(content.get('hook', '')[:55])
    course_name  = safe_text(content['course']['name'])
    branding     = safe_text('PUMO Technovation  |  016-259 2727')
    cap_duration = audio_duration / max(len(captions), 1)

    drawtext_parts = []

    # Hook — big white text, first 3 seconds, top centre
    drawtext_parts.append(
        f"drawtext=text='{hook_text}'"
        f":fontsize=54:fontcolor=white:borderw=4:bordercolor=black@0.9"
        f":x=(w-text_w)/2:y=h*0.10"
        f":enable='between(t,0,3.5)'"
        f":font=DejaVu-Sans-Bold"
    )

    # Timed captions — yellow bold, lower screen, synced to voiceover
    for i, caption in enumerate(captions):
        start = i * cap_duration
        end   = (i + 1) * cap_duration

        # Wrap long captions into 2 lines
        words, lines, current = caption.split(), [], []
        for word in words:
            current.append(word)
            if len(' '.join(current)) > 28:
                lines.append(' '.join(current))
                current = []
        if current:
            lines.append(' '.join(current))
        cap_text = safe_text(' / '.join(lines[:2]))

        drawtext_parts.append(
            f"drawtext=text='{cap_text}'"
            f":fontsize=46:fontcolor=yellow:borderw=4:bordercolor=black@0.9"
            f":x=(w-text_w)/2:y=h*0.76"
            f":enable='between(t,{start:.2f},{end:.2f})'"
            f":font=DejaVu-Sans-Bold"
        )

    # Course badge — top right corner, always visible
    drawtext_parts.append(
        f"drawtext=text='{course_name}'"
        f":fontsize=28:fontcolor=white:borderw=2:bordercolor=black@0.9"
        f":box=1:boxcolor=black@0.55:boxborderw=10"
        f":x=w-text_w-20:y=20"
        f":font=DejaVu-Sans-Bold"
    )

    # PUMO branding — bottom bar, always visible
    drawtext_parts.append(
        f"drawtext=text='{branding}'"
        f":fontsize=26:fontcolor=white:borderw=2:bordercolor=black@0.9"
        f":box=1:boxcolor=black@0.6:boxborderw=8"
        f":x=(w-text_w)/2:y=h*0.935"
        f":font=DejaVu-Sans"
    )

    # 4d — Final render with all overlays + voiceover
    print("   Rendering final video with captions and branding...")
    output = "/tmp/pumo_final.mp4"
    result = subprocess.run([
        'ffmpeg', '-y',
        '-i', combined,
        '-i', audio_path,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '24',
        '-c:a', 'aac', '-b:a', '128k',
        '-map', '0:v:0', '-map', '1:a:0',
        '-shortest', '-movflags', '+faststart', '-r', '30',
        output
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FFmpeg error:\n{result.stderr[-500:]}")
        sys.exit(1)

    size_mb = os.path.getsize(output) / (1024 * 1024)
    print(f"   ✓ Video ready — {size_mb:.1f} MB")
    return output


# ============================================================
# STEP 5 — Post directly to Instagram via Upload-Post API
# ============================================================
def post_to_instagram(video_path, content):
    print("📲 Step 5: Posting to Instagram via Upload-Post...")

    caption  = content['post_caption']
    hashtags = content['hashtags']
    full_cap = f"{caption}\n\n{hashtags}"

    with open(video_path, 'rb') as f:
        response = requests.post(
            "https://api.upload-post.com/api/upload",
            headers={
                "Authorization": f"Apikey {UPLOAD_POST_API_KEY}"
            },
            data={
                "title":      full_cap,
                "user":       INSTAGRAM_USERNAME,
                "platform[]": "instagram"
            },
            files={
                "video": ("pumo_video.mp4", f, "video/mp4")
            }
        )

    if response.status_code in (200, 201):
        print("   ✓ Posted to Instagram successfully!")
        print(f"   ✓ Account: @{INSTAGRAM_USERNAME}")
    else:
        print(f"   ⚠️  Upload-Post response: {response.status_code}")
        print(f"   ⚠️  Details: {response.text}")

    return response.status_code in (200, 201)


# ============================================================
# MAIN — runs the full pipeline
# ============================================================
def main():
    print("=" * 52)
    print("  🤖  PUMO Autonomous Instagram Agent")
    print(f"  📅  {datetime.utcnow().strftime('%A, %d %B %Y')} (UTC)")
    print("=" * 52)

    # Check all required secrets are present
    required = {
        'ANTHROPIC_API_KEY':   ANTHROPIC_API_KEY,
        'ELEVENLABS_API_KEY':  ELEVENLABS_API_KEY,
        'PEXELS_API_KEY':      PEXELS_API_KEY,
        'UPLOAD_POST_API_KEY': UPLOAD_POST_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"❌ Missing GitHub Secrets: {', '.join(missing)}")
        print("   GitHub → Settings → Secrets and variables → Actions")
        sys.exit(1)

    # Run the full pipeline
    content    = generate_content()
    audio_path = generate_voiceover(content['script'])
    clip_paths = download_stock_footage(content['pexels_search'], count=4)
    video_path = edit_video(clip_paths, audio_path, content)
    success    = post_to_instagram(video_path, content)

    print("\n" + "=" * 52)
    print("  ✅  DONE!" if success else "  ⚠️  Completed with warnings.")
    print(f"  🎬  Course:   {content['course']['name']}")
    print(f"  🎣  Hook:     {content['hook']}")
    print(f"  📸  Posted:   Instagram @{INSTAGRAM_USERNAME}")
    print("=" * 52)


if __name__ == "__main__":
    main()
