"""
PUMO Technovation - Autonomous Instagram Video Agent v7
=======================================================
Stack:
- Claude        → viral script + scene prompts
- ElevenLabs    → voiceover with word timestamps
- Replicate     → AI video clips (Seedance 1080p)
- Pexels        → real stock footage
- Remotion      → edits everything together:
                   word-by-word captions, zoom punches,
                   transitions, branding, music sync
- Upload-Post   → posts to Instagram Reels
"""

import os
import json
import time
import random
import requests
import subprocess
import sys
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================
ANTHROPIC_API_KEY    = os.environ.get('ANTHROPIC_API_KEY', '')
ELEVENLABS_API_KEY   = os.environ.get('ELEVENLABS_API_KEY', '')
REPLICATE_API_KEY    = os.environ.get('REPLICATE_API_KEY', '')
PEXELS_API_KEY       = os.environ.get('PEXELS_API_KEY', '')
UPLOAD_POST_API_KEY  = os.environ.get('UPLOAD_POST_API_KEY', '')
INSTAGRAM_USERNAME   = 'Pumo_Profile'
ELEVENLABS_VOICE_ID  = '21m00Tcm4TlvDq8ikWAM'  # Rachel


# ============================================================
# COURSE ROTATION
# ============================================================
COURSES = {
    0: {
        "name": "Cybersecurity",
        "pain_point": "businesses losing data to cyber attacks every single day",
        "outcome": "protect systems and build a career in one of the most in-demand tech fields",
        "pexels_searches": [
            "cybersecurity professional working",
            "IT engineer office technology",
            "network security monitoring"
        ],
        "ai_scene_prompts": [
            "dramatic dark cyber attack visualization, glowing red code streams, cinematic 9:16 portrait",
            "futuristic digital security shield glowing blue, abstract tech, 9:16 portrait cinematic",
            "person triumphantly using computer, success, modern office, 9:16 portrait"
        ]
    },
    1: {
        "name": "Cloud and DevOps",
        "pain_point": "companies stuck on outdated systems while competitors move to cloud",
        "outcome": "deploy and manage cloud infrastructure that every company needs right now",
        "pexels_searches": [
            "server room data centre lights",
            "software developer coding laptop",
            "IT professional working office"
        ],
        "ai_scene_prompts": [
            "dramatic server room with glowing blue lights, cinematic 9:16 portrait",
            "abstract cloud computing visualization, data streams, futuristic 9:16",
            "confident developer at multiple screens, success, modern office 9:16"
        ]
    },
    2: {
        "name": "AI and Prompt Engineering",
        "pain_point": "people watching AI change every industry without knowing how to use it",
        "outcome": "use AI tools that make you more valuable and harder to replace",
        "pexels_searches": [
            "person using laptop technology",
            "professional working modern office",
            "technology innovation digital"
        ],
        "ai_scene_prompts": [
            "dramatic AI neural network visualization, glowing synapses, cinematic 9:16 portrait",
            "futuristic human and AI interface, glowing hologram, 9:16 portrait",
            "confident professional using AI, modern workspace, success energy 9:16"
        ]
    },
    3: {
        "name": "Digital Marketing",
        "pain_point": "businesses spending on content and ads that nobody actually sees",
        "outcome": "create campaigns that reach real audiences and drive real results",
        "pexels_searches": [
            "content creator filming phone",
            "marketing professional laptop analytics",
            "social media phone scrolling"
        ],
        "ai_scene_prompts": [
            "dramatic social media explosion, colorful notifications flying, cinematic 9:16",
            "abstract marketing analytics visualization, graphs growing, colorful 9:16",
            "confident marketer celebrating success, modern office, energy 9:16"
        ]
    },
    4: {
        "name": "BIM and CAD",
        "pain_point": "construction projects going over budget due to poor digital planning",
        "outcome": "design and plan buildings digitally before construction even begins",
        "pexels_searches": [
            "architect blueprint design office",
            "construction building modern",
            "engineer computer CAD design"
        ],
        "ai_scene_prompts": [
            "dramatic 3D building blueprint hologram, glowing blue lines, cinematic 9:16",
            "futuristic architectural visualization, building emerging from blueprint, 9:16",
            "proud engineer viewing completed building, success, cinematic 9:16"
        ]
    },
    5: {
        "name": "Mechanical Design CAD/CAM",
        "pain_point": "manufacturers struggling to find people who can design modern machines",
        "outcome": "design parts and program machines used in real manufacturing",
        "pexels_searches": [
            "mechanical engineering factory",
            "manufacturing machine production",
            "engineer design computer office"
        ],
        "ai_scene_prompts": [
            "dramatic mechanical gears and machinery, industrial cinematic, 9:16 portrait",
            "futuristic 3D CAD design hologram, precision engineering, 9:16",
            "confident engineer in modern factory, success energy, cinematic 9:16"
        ]
    },
    6: {
        "name": "Career Development",
        "pain_point": "graduates sending hundreds of applications and hearing nothing back",
        "outcome": "position yourself as the candidate employers actually want to hire",
        "pexels_searches": [
            "job interview professional office",
            "young professional working laptop",
            "business meeting success"
        ],
        "ai_scene_prompts": [
            "dramatic job rejection pile of resumes, dark moody cinematic, 9:16 portrait",
            "futuristic career success visualization, bright upward trajectory, 9:16",
            "confident professional handshake success, bright modern office, 9:16"
        ]
    },
}


# ============================================================
# STEP 1 — Generate script with Claude
# ============================================================
def generate_content():
    print("📝 Step 1: Claude is writing today's script...")

    day    = datetime.utcnow().weekday()
    course = COURSES[day]

    prompt = f"""You are a content writer for PUMO Technovation, an IT training centre in KL.

Write a 6-scene 60-second Instagram Reel script for: {course['name']} course.
Real problem: {course['pain_point']}
What students learn: {course['outcome']}

RULES:
- Natural clear Malaysian English. NO BM words. NO lah, kan, lor.
- Sound like a trusted friend giving honest career advice.
- Short punchy sentences. High energy. Every sentence hooks the viewer.
- NO salary guarantees. NO income promises whatsoever.
- Mention HRD Corp claimable naturally in scene 5.
- Scene 6: soft CTA — reach out to PUMO. No phone number spoken aloud.
- Each scene: 2-3 sentences maximum. Under 25 words per scene.

Return ONLY valid JSON, no markdown:

{{
  "scenes": [
    {{"scene": 1, "script": "Hook scene — calls out the pain point. Stops the scroll."}},
    {{"scene": 2, "script": "Agitate the problem — make it feel real and urgent."}},
    {{"scene": 3, "script": "Introduce PUMO course as the solution. Keep it natural."}},
    {{"scene": 4, "script": "Specific skills students learn. Concrete not vague."}},
    {{"scene": 5, "script": "Why act now. Mention HRD Corp claimable naturally."}},
    {{"scene": 6, "script": "Soft CTA. Reach out to PUMO to find out more."}}
  ],
  "full_script": "All 6 scenes combined into one continuous script for voiceover. 130-150 words total.",
  "post_caption": "Instagram caption. Genuine tone. Emojis. Max 200 chars. Ends with: 📞 016-259 2727",
  "hashtags": "#pumotechnovation #KLtraining #hrdcorp #hrdcorpclaimable #malaysiajobs #techjobs #kerjaya #skilldevelopment #kualalumpur #malaysiatech",
  "hook": "First sentence only — max 8 words"
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
        print(f"   ✓ Scene {i+1}: {scene['script'][:50]}...")
    return content


# ============================================================
# STEP 2 — Generate voiceover with ElevenLabs
# Returns audio file + word-level timestamps
# ============================================================
def generate_voiceover(full_script):
    print("🎙️  Step 2: ElevenLabs generating voiceover with timestamps...")

    # Generate audio
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "Accept":       "audio/mpeg",
            "xi-api-key":   ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text":     full_script,
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
        print(f"   ⚠️  ElevenLabs failed: {response.status_code}")
        sys.exit(1)

    audio_path = "/tmp/voiceover.mp3"
    with open(audio_path, "wb") as f:
        f.write(response.content)

    # Get word-level timestamps using ElevenLabs alignment endpoint
    align_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/with-timestamps",
        headers={
            "xi-api-key":   ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text":     full_script,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability":         0.35,
                "similarity_boost":  0.85,
                "style":             0.25,
                "use_speaker_boost": True
            }
        }
    )

    word_timestamps = []
    if align_response.status_code == 200:
        align_data = align_response.json()
        # Extract word-level timing
        alignment  = align_data.get('alignment', {})
        chars      = alignment.get('characters', [])
        char_starts = alignment.get('character_start_times_seconds', [])
        char_ends   = alignment.get('character_end_times_seconds', [])

        # Group characters into words
        current_word  = ''
        word_start    = 0
        for i, char in enumerate(chars):
            if char == ' ' or i == len(chars) - 1:
                if char != ' ':
                    current_word += char
                if current_word.strip():
                    word_timestamps.append({
                        "word":  current_word.strip(),
                        "start": round(word_start, 3),
                        "end":   round(char_ends[i] if i < len(char_ends) else word_start + 0.3, 3)
                    })
                current_word = ''
                if i + 1 < len(char_starts):
                    word_start = char_starts[i + 1]
            else:
                if not current_word:
                    word_start = char_starts[i] if i < len(char_starts) else 0
                current_word += char

        print(f"   ✓ Got {len(word_timestamps)} word timestamps")
    else:
        # Fallback: estimate timestamps from word count
        print(f"   ⚠️  Timestamp endpoint not available, estimating...")
        words    = full_script.split()
        duration = 60.0
        per_word = duration / len(words)
        for i, word in enumerate(words):
            word_timestamps.append({
                "word":  word,
                "start": round(i * per_word, 3),
                "end":   round((i + 1) * per_word, 3)
            })

    # Get audio duration
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json',
         '-show_streams', audio_path],
        capture_output=True, text=True
    )
    duration = 60.0
    try:
        for stream in json.loads(result.stdout).get('streams', []):
            if stream.get('codec_type') == 'audio':
                duration = float(stream.get('duration', 60))
    except Exception:
        pass

    print(f"   ✓ Voiceover ready — {duration:.1f}s, {len(word_timestamps)} words")
    return audio_path, word_timestamps, duration


# ============================================================
# STEP 3 — Generate AI clips with Replicate (Seedance)
# ============================================================
def generate_ai_clip(prompt, scene_num):
    print(f"   🤖 Generating AI clip for scene {scene_num}...")

    # Start prediction
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Bearer {REPLICATE_API_KEY}",
            "Content-Type":  "application/json"
        },
        json={
            "version": "bytedance/seedance-1-lite",
            "input": {
                "prompt":       prompt,
                "aspect_ratio": "9:16",
                "duration":     5,
                "resolution":   "1080p"
            }
        }
    )

    if response.status_code not in (200, 201):
        print(f"   ⚠️  Replicate error: {response.status_code}")
        return None

    prediction_id = response.json().get('id', '')
    if not prediction_id:
        return None

    # Poll until done
    for _ in range(60):
        time.sleep(5)
        poll = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers={"Authorization": f"Bearer {REPLICATE_API_KEY}"}
        )
        result = poll.json()
        status = result.get('status', '')

        if status == 'succeeded':
            output = result.get('output', '')
            url    = output if isinstance(output, str) else (output[0] if output else '')
            if url:
                # Download clip
                clip_path = f"/tmp/ai_clip_{scene_num}.mp4"
                r = requests.get(url, stream=True, timeout=60)
                with open(clip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"   ✓ AI clip {scene_num} ready")
                return clip_path

        elif status == 'failed':
            print(f"   ⚠️  AI clip {scene_num} failed")
            return None

    print(f"   ⚠️  AI clip {scene_num} timed out")
    return None


# ============================================================
# STEP 4 — Get stock footage from Pexels
# ============================================================
def get_pexels_clip(search_term, scene_num):
    print(f"   📹 Getting stock clip for scene {scene_num}: '{search_term}'...")

    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={
            "query":       search_term,
            "per_page":    10,
            "orientation": "portrait",
            "size":        "large"
        },
        timeout=15
    )

    videos = response.json().get('videos', [])
    if not videos:
        return None

    video = random.choice(videos[:5])
    files = video.get('video_files', [])

    # Get best HD portrait file
    hd = [f for f in files
          if f.get('width', 0) >= 1080
          and f.get('height', 0) >= f.get('width', 0)]
    if not hd:
        hd = [f for f in files
              if f.get('height', 0) >= f.get('width', 0)]
    if not hd:
        hd = files
    if not hd:
        return None

    hd.sort(key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
    url = hd[0].get('link', '')
    if not url:
        return None

    clip_path = f"/tmp/stock_clip_{scene_num}.mp4"
    r = requests.get(url, stream=True, timeout=30)
    with open(clip_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"   ✓ Stock clip {scene_num} ready")
    return clip_path


# ============================================================
# STEP 5 — Get all 6 clips
# Scenes 1, 4, 6 = AI generated
# Scenes 2, 3, 5 = Stock footage
# ============================================================
def get_all_clips(content):
    print("🎬 Steps 3-4: Getting all 6 clips...")

    course      = content['course']
    ai_prompts  = course['ai_scene_prompts']
    pexels_searches = course['pexels_searches']
    clips       = {}

    # AI scenes: 1, 4, 6 (indices 0, 3, 5)
    ai_scene_map = {1: 0, 4: 1, 6: 2}
    for scene_num, prompt_idx in ai_scene_map.items():
        prompt = ai_prompts[prompt_idx % len(ai_prompts)]
        clip   = generate_ai_clip(prompt, scene_num)
        clips[scene_num] = clip

    # Stock scenes: 2, 3, 5 (indices 1, 2, 4)
    stock_scene_map = {2: 0, 3: 1, 5: 2}
    for scene_num, search_idx in stock_scene_map.items():
        search = pexels_searches[search_idx % len(pexels_searches)]
        clip   = get_pexels_clip(search, scene_num)
        clips[scene_num] = clip

    # Fallback: if any clip failed, use stock footage
    for scene_num in range(1, 7):
        if not clips.get(scene_num):
            print(f"   ⚠️  Scene {scene_num} failed, using fallback stock clip...")
            fallback = get_pexels_clip("professional office technology", scene_num)
            clips[scene_num] = fallback

    print(f"   ✓ All clips ready: {sum(1 for c in clips.values() if c)} / 6")
    return clips


# ============================================================
# STEP 6 — Build Remotion data payload
# Pass all data to Remotion for rendering
# ============================================================
def render_with_remotion(clips, audio_path, word_timestamps, duration, content):
    print("✂️  Step 5: Remotion rendering video...")

    # Build scene data for Remotion
    scenes = []
    scene_duration = duration / 6  # equal split across 6 scenes

    for i in range(1, 7):
        scene_script = content['scenes'][i-1]['script'] if i-1 < len(content['scenes']) else ''
        scenes.append({
            "scene_num":  i,
            "clip_path":  clips.get(i, ''),
            "script":     scene_script,
            "start_time": round((i-1) * scene_duration, 3),
            "duration":   round(scene_duration, 3),
            "is_ai":      i in [1, 4, 6]
        })

    # Save Remotion input data
    remotion_data = {
        "scenes":          scenes,
        "audio_path":      audio_path,
        "word_timestamps": word_timestamps,
        "total_duration":  duration,
        "course_name":     content['course']['name'],
        "hook":            content['hook'],
        "branding":        "PUMO Technovation  |  016-259 2727"
    }

    data_path = "/tmp/remotion_data.json"
    with open(data_path, 'w') as f:
        json.dump(remotion_data, f)

    # Copy data to Remotion project
    subprocess.run(['cp', data_path, 'remotion/public/data.json'], check=True)
    subprocess.run(['cp', audio_path, 'remotion/public/voiceover.mp3'], check=True)

    # Copy all clips to Remotion public folder
    for i in range(1, 7):
        clip = clips.get(i)
        if clip and os.path.exists(clip):
            subprocess.run(['cp', clip, f'remotion/public/scene_{i}.mp4'], check=True)

    # Render with Remotion
    output_path = "/tmp/pumo_final.mp4"
    result = subprocess.run([
        'npx', 'remotion', 'render',
        'remotion/src/index.tsx',
        'PUMOVideo',
        output_path,
        '--props', data_path,
        '--codec', 'h264',
        '--video-bitrate', '8000K',
        '--crf', '18'
    ], capture_output=True, text=True, cwd=os.getcwd())

    if result.returncode != 0:
        print(f"❌ Remotion error:\n{result.stderr[-500:]}")
        sys.exit(1)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   ✓ Video rendered — {size_mb:.1f} MB")
    return output_path


# ============================================================
# STEP 7 — Post to Instagram
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
    print("  🤖  PUMO Autonomous Instagram Agent v7")
    print(f"  📅  {datetime.utcnow().strftime('%A, %d %B %Y')} (UTC)")
    print("  🎬  Replicate AI + Pexels HD + Remotion Editor")
    print("=" * 52)

    required = {
        'ANTHROPIC_API_KEY':   ANTHROPIC_API_KEY,
        'ELEVENLABS_API_KEY':  ELEVENLABS_API_KEY,
        'REPLICATE_API_KEY':   REPLICATE_API_KEY,
        'PEXELS_API_KEY':      PEXELS_API_KEY,
        'UPLOAD_POST_API_KEY': UPLOAD_POST_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"❌ Missing secrets: {', '.join(missing)}")
        sys.exit(1)

    content                          = generate_content()
    audio_path, word_timestamps, dur = generate_voiceover(content['full_script'])
    clips                            = get_all_clips(content)
    video_path                       = render_with_remotion(clips, audio_path, word_timestamps, dur, content)
    success                          = post_to_instagram(video_path, content)

    print("\n" + "=" * 52)
    print("  ✅  DONE!" if success else "  ⚠️  Done with warnings.")
    print(f"  🎬  Course:  {content['course']['name']}")
    print(f"  🎣  Hook:    {content['hook']}")
    print(f"  📸  Posted:  Instagram Reels")
    print(f"  🎥  Engine:  Replicate + Remotion")
    print("=" * 52)


if __name__ == "__main__":
    main()
