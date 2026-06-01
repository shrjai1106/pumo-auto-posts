"""
PUMO Technovation - Autonomous Instagram Video Agent v10
========================================================
Architecture: Claude is the DIRECTOR
- Claude writes script AND directs every scene:
  * Visual type (AI or stock)
  * AI generation prompt (for Replicate)
  * Stock search term (for Pexels)
  * Scene duration (matches speech pace — no gaps)
  * Transition type (slam/slide/whip_pan/zoom/fade)
  * Keyword overlay + position + colour per scene
- Remotion follows Claude's exact direction
- ElevenLabs word timestamps eliminate all audio gaps
- 14 courses × 6 formats = 84 unique video types
"""

import os, json, time, random, requests, subprocess, sys
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
ANTHROPIC_API_KEY   = os.environ.get('ANTHROPIC_API_KEY', '')
ELEVENLABS_API_KEY  = os.environ.get('ELEVENLABS_API_KEY', '')
REPLICATE_API_KEY   = os.environ.get('REPLICATE_API_KEY', '')
PEXELS_API_KEY      = os.environ.get('PEXELS_API_KEY', '')
UPLOAD_POST_API_KEY = os.environ.get('UPLOAD_POST_API_KEY', '')
INSTAGRAM_USERNAME  = 'Pumo_Profile'
VOICE_ID            = '21m00Tcm4TlvDq8ikWAM'

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/download/audio/2022/03/15/audio_8cb749c411.mp3",
    "https://cdn.pixabay.com/download/audio/2023/01/04/audio_d0c6ff1bab.mp3",
    "https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3",
]

VALID_TRANSITIONS = ["slam","slide_left","slide_right","slide_up","fade","zoom_in","zoom_out","whip_pan"]

# ============================================================
# 6 VIDEO FORMATS
# ============================================================
VIDEO_FORMATS = {
    "story":        {"label":"Story-Driven",   "structure":"Hook pain → Agitate → Solution → Skills → Why now → CTA"},
    "myth_reality": {"label":"Myth vs Reality","structure":"Myth 1 → Reality 1 → Myth 2 → Reality 2 → Myth 3 → CTA"},
    "quick_tips":   {"label":"Quick Tips",     "structure":"Hook (count) → Tip 1 → Tip 2 → Tip 3 → Tip 4 → CTA"},
    "day_in_life":  {"label":"Day in the Life","structure":"Morning → Task 1 → Task 2 → Problem solved → Tools → CTA"},
    "before_after": {"label":"Before vs After","structure":"Before pain → Struggle → Turning point → After → Outcome → CTA"},
    "hot_take":     {"label":"Hot Take",       "structure":"Controversial hook → Why wrong → Data → Truth → PUMO → CTA"},
}
FORMAT_KEYS = list(VIDEO_FORMATS.keys())

# ============================================================
# 14 COURSES
# ============================================================
COURSES = {
    0:  {"name":"Cybersecurity",           "pain":"Malaysian businesses hit by cyber attacks every 10 minutes",         "outcome":"protect systems and launch a high-demand security career",        "trends":["3,000+ cybersecurity jobs unfilled in Malaysia","SMEs losing RM millions to ransomware daily","Malaysia top 10 most targeted countries for cyber attacks"]},
    1:  {"name":"Generative AI",           "pain":"60% of Malaysian companies adopting AI but workers don't know how",  "outcome":"build AI tools, automate workflows, become indispensable",         "trends":["AI adoption in Malaysia jumped 60% in 2024","Generative AI creating 97M new roles globally","Prompt skills separating top performers from the rest"]},
    2:  {"name":"Sales Engineering",       "pain":"technical talent who can sell is the rarest and highest paid combo", "outcome":"bridge tech expertise with sales to close enterprise deals",       "trends":["Sales engineers earn 2x average tech salary in Malaysia","ASEAN enterprise software market hit USD 8B in 2024","Demand for technical sales roles up 45% year on year"]},
    3:  {"name":"Digital Marketing",       "pain":"businesses spending on ads that get zero engagement or conversions", "outcome":"run data-driven campaigns that reach and convert real audiences",   "trends":["Malaysian digital ad spend hitting RM 3B in 2025","TikTok Shop making digital marketers essential for SMEs","90% of consumers research online before buying anything"]},
    4:  {"name":"AWS/Azure & DevOps",      "pain":"companies stuck on outdated systems while competitors scale on cloud","outcome":"deploy scalable cloud infrastructure companies desperately need",   "trends":["Malaysia cloud adoption up 45% year on year","AWS and Azure engineers among highest paid IT roles","Government cloud-first mandate driving demand surge"]},
    5:  {"name":"Logistics & Supply Chain","pain":"supply chain failures costing Malaysian businesses billions yearly",  "outcome":"optimise logistics, cut costs, manage complex supply chains",       "trends":["Malaysia logistics sector growing 8% annually in 2025","E-commerce boom creating urgent demand for logistics talent","Supply chain resilience now a board-level priority"]},
    6:  {"name":"Prompt Engineering",      "pain":"everyone uses AI but almost nobody gets actually useful results",     "outcome":"master prompting that produces professional-grade AI outputs",      "trends":["Prompt engineers earning USD 300K at top US companies","Bad prompting costing companies hours of rework daily","Prompt skills the single biggest AI productivity differentiator"]},
    7:  {"name":"Agentic AI",              "pain":"most professionals use AI passively instead of making it work for them","outcome":"build autonomous AI agents that complete complex tasks alone",    "trends":["AI agents automating 80% of repetitive knowledge work","Agentic AI market projected to hit USD 47B by 2030","Early adopters gaining massive competitive advantage now"]},
    8:  {"name":"Social Media Marketing",  "pain":"Malaysian brands posting daily with zero growth or engagement",       "outcome":"build audiences, create viral content, monetise social presence",  "trends":["Malaysian social media users hit 29M active in 2025","TikTok creators earning RM 10K-50K monthly in Malaysia","Reels get 5x more reach than static posts on Instagram"]},
    9:  {"name":"Graphic Design & Video",  "pain":"businesses losing to competitors with better-looking content",        "outcome":"create professional graphics and videos with Canva and CapCut",    "trends":["Video content drives 3x more engagement than images","Canva used by 170M people globally in 2025","Good design increases brand trust and conversions by 75%"]},
    10: {"name":"Python & Web Development","pain":"businesses paying tens of thousands for basic websites they could build","outcome":"build AI-powered websites and apps without a CS degree",        "trends":["Python remains top programming language 5 years running","AI-assisted coding cutting development time by 60%","Malaysian web dev roles averaging RM 80K annually in 2025"]},
    11: {"name":"BIM & Tekla",             "pain":"construction projects failing due to poor digital coordination",       "outcome":"model buildings digitally, reduce rework, save project costs",    "trends":["Malaysia mandating BIM for all government projects","BIM specialists earning 40% more than traditional engineers","Construction rework reduced by 30% with proper BIM adoption"]},
    12: {"name":"QA/QC Lean Six Sigma",    "pain":"manufacturing defects costing Malaysian factories millions in waste",  "outcome":"eliminate defects and cut operational costs systematically",      "trends":["Manufacturing defects cost Malaysian industry RM 1.5B yearly","Lean Six Sigma reduces waste by 40% on average","Quality talent in critical shortage across Malaysian manufacturing"]},
    13: {"name":"Career Development",      "pain":"graduates sending 200+ applications and getting zero responses",       "outcome":"position yourself as the candidate employers fight over",         "trends":["Malaysian fresh grad unemployment at 10.7% in 2024","80% of CVs rejected within 6 seconds by hiring managers","Skills gap costing Malaysian economy RM 8 billion annually"]},
}

# ============================================================
# PRE-FLIGHT — validates before spending any credits
# ============================================================
def preflight_check():
    print("\n🔍 Pre-flight checks...")
    errors = []

    required = {
        'ANTHROPIC_API_KEY':   ANTHROPIC_API_KEY,
        'ELEVENLABS_API_KEY':  ELEVENLABS_API_KEY,
        'REPLICATE_API_KEY':   REPLICATE_API_KEY,
        'PEXELS_API_KEY':      PEXELS_API_KEY,
        'UPLOAD_POST_API_KEY': UPLOAD_POST_API_KEY,
    }
    for k, v in required.items():
        if not v: errors.append(f"Missing secret: {k}")
        else:     print(f"   ✓ {k}")

    for path in ["remotion/src/index.tsx", "remotion/package.json"]:
        if not os.path.exists(path): errors.append(f"Missing file: {path}")
        else:                        print(f"   ✓ {path}")

    try:
        r = requests.get("https://api.replicate.com/v1/account",
            headers={"Authorization": f"Bearer {REPLICATE_API_KEY}"}, timeout=10)
        if r.status_code == 200: print("   ✓ Replicate OK")
        else: errors.append(f"Replicate invalid: {r.status_code}")
    except Exception as e: errors.append(f"Replicate unreachable: {e}")

    try:
        r = requests.get("https://api.elevenlabs.io/v1/models",
            headers={"xi-api-key": ELEVENLABS_API_KEY}, timeout=10)
        if r.status_code == 200:
            print("   ✓ ElevenLabs OK")
        else:
            errors.append(f"ElevenLabs invalid: {r.status_code}")
    except Exception as e:
        errors.append(f"ElevenLabs unreachable: {e}")

    try:
        r = requests.get("https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query":"test","per_page":1}, timeout=10)
        if r.status_code == 200: print("   ✓ Pexels OK")
        else: errors.append(f"Pexels invalid: {r.status_code}")
    except Exception as e: errors.append(f"Pexels unreachable: {e}")

    if errors:
        print("\n❌ PRE-FLIGHT FAILED — zero credits used:")
        for e in errors: print(f"   • {e}")
        sys.exit(1)
    print("   ✅ All pre-flight checks passed\n")


# ============================================================
# STEP 1 — Claude writes script AND directs every scene
# ============================================================
def generate_directed_content(course, fmt_key):
    print("🎬 Step 1: Claude directing script + visuals...")

    fmt       = VIDEO_FORMATS[fmt_key]
    trends    = "\n".join([f"- {t}" for t in course['trends']])

    prompt = f"""You are the DIRECTOR and scriptwriter for a viral 60-second Instagram Reel for PUMO Technovation, an IT training centre in Kuala Lumpur.

COURSE: {course['name']}
REAL PROBLEM: {course['pain']}
WHAT STUDENTS LEARN: {course['outcome']}
VIDEO FORMAT: {fmt['label']} — {fmt['structure']}
CURRENT TRENDS:
{trends}

Your job: Write the script AND direct every single scene visually.

SCRIPT RULES:
- Natural Malaysian English. Zero BM slang.
- Every sentence makes the viewer need the next one.
- Use trending data naturally — feel current and urgent.
- No salary promises. No income guarantees.
- Mention HRD Corp claimable in scene 12 or 13 naturally.
- Scene 15: soft CTA to reach out to PUMO. No phone number spoken.
- Each scene: 1-2 punchy sentences. MAX 15 words per scene.
- Total full_script: 130-150 words for a 60-second voiceover.

SCENE DURATION RULES (critical — prevents audio gaps):
- Assign duration based on how many words are in that scene's script.
- Short scene (5-8 words) = 2.5-3.0 seconds
- Medium scene (9-12 words) = 3.5-4.5 seconds  
- Long scene (13-15 words) = 4.5-5.5 seconds
- ALL 15 durations must sum to EXACTLY 60.0 seconds.

VISUAL DIRECTION RULES:
- visual_type: "ai" for dramatic/abstract/impact moments, "stock" for people/workplace
- Use "ai" for scenes 1, 4, 8, 12, 15 typically (hook, turning points, CTA)
- ai_prompt: specific cinematic description for Replicate Seedance. Include "9:16 portrait", "cinematic", "photorealistic". Be vivid and specific.
- stock_search: 3-4 word Pexels search for "stock" scenes. Portrait orientation.
- transition_in: choose from [slam, slide_left, slide_right, slide_up, fade, zoom_in, zoom_out, whip_pan]
  * slam = impact moments, reveals
  * whip_pan = fast energy shifts
  * slide_left/right = natural flow between scenes
  * zoom_in = building tension
  * zoom_out = reveal/release
  * fade = gentle transitions
- keyword_overlay: ONE powerful word to slam on screen during this scene. Empty string if none.
- overlay_position: "center" (dominant), "top" (subtle), "bottom" (below caption area)
- text_color: "yellow" (default), "white", "red" (danger/urgency), "green" (positive)

Return ONLY valid JSON, no markdown:
{{
  "scenes": [
    {{
      "scene": 1,
      "duration": 3.5,
      "script": "scene 1 voiceover text",
      "visual_type": "ai",
      "ai_prompt": "vivid specific Replicate prompt",
      "stock_search": "",
      "transition_in": "slam",
      "keyword_overlay": "WORD",
      "overlay_position": "center",
      "text_color": "red"
    }}
    ... all 15 scenes
  ],
  "full_script": "all 15 scenes as one continuous natural voiceover — 130-150 words",
  "post_caption": "Instagram caption. Genuine tone. Emojis. Max 200 chars. Ends with: 📞 016-259 2727",
  "hashtags": "#pumotechnovation #KLtraining #hrdcorp #hrdcorpclaimable #malaysiajobs #kerjaya #skilldevelopment #kualalumpur",
  "hook": "scene 1 first sentence only. Max 8 words. Uppercase.",
  "keywords": ["4 powerful single words from script"],
  "stats": ["key stat from trends e.g. 3000+", "one-word label e.g. shortage"]
}}"""

    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key":ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
        json={"model":"claude-sonnet-4-20250514","max_tokens":3000,"messages":[{"role":"user","content":prompt}]}
    )
    raw = r.json()['content'][0]['text'].strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
        raw = raw.split("```")[0]

    content = json.loads(raw.strip())

    # ── VALIDATE + FIX DURATIONS ──────────────────────────────
    scenes      = content.get('scenes', [])
    total_dur   = sum(s.get('duration', 4.0) for s in scenes)
    scale       = 60.0 / max(total_dur, 1)
    running     = 0.0
    for i, s in enumerate(scenes):
        if i == len(scenes) - 1:
            s['duration'] = round(60.0 - running, 3)
        else:
            s['duration'] = round(s.get('duration', 4.0) * scale, 3)
        running += s['duration']
        # Sanitise transitions
        if s.get('transition_in') not in VALID_TRANSITIONS:
            s['transition_in'] = 'slide_left'
        # Ensure visual_type is valid
        if s.get('visual_type') not in ['ai','stock']:
            s['visual_type'] = 'stock'

    content['scenes']       = scenes
    content['course']       = course
    content['format']       = fmt_key
    content['format_label'] = fmt['label']

    if not content.get('keywords') or len(content['keywords']) < 3:
        content['keywords'] = ["SKILLS","CAREER","LEARN","NOW"]
    if not content.get('stats') or len(content['stats']) < 2:
        content['stats'] = ["1,000+","needed"]

    # Log summary
    print(f"   ✓ Course:    {course['name']}")
    print(f"   ✓ Format:    {fmt['label']}")
    print(f"   ✓ Hook:      {content['hook']}")
    print(f"   ✓ Durations: {[s['duration'] for s in scenes]} = {sum(s['duration'] for s in scenes):.1f}s")
    print(f"   ✓ Transitions: {[s['transition_in'] for s in scenes]}")
    ai_scenes    = [s['scene'] for s in scenes if s['visual_type']=='ai']
    stock_scenes = [s['scene'] for s in scenes if s['visual_type']=='stock']
    print(f"   ✓ AI scenes: {ai_scenes}")
    print(f"   ✓ Stock scenes: {stock_scenes}")
    return content


# ============================================================
# STEP 2 — ElevenLabs voiceover + word timestamps
# ============================================================
def generate_voiceover(full_script):
    print("🎙️  Step 2: ElevenLabs voiceover + timestamps...")

    vs = {"stability":0.35,"similarity_boost":0.85,"style":0.25,"use_speaker_boost":True}

    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={"Accept":"audio/mpeg","xi-api-key":ELEVENLABS_API_KEY,"Content-Type":"application/json"},
        json={"text":full_script,"model_id":"eleven_multilingual_v2","voice_settings":vs}
    )
    if r.status_code != 200:
        print(f"❌ ElevenLabs audio: {r.status_code} — {r.text[:200]}")
        sys.exit(1)

    audio_path = "/tmp/voiceover.mp3"
    with open(audio_path,"wb") as f: f.write(r.content)

    # Word timestamps
    r2 = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps",
        headers={"xi-api-key":ELEVENLABS_API_KEY,"Content-Type":"application/json"},
        json={"text":full_script,"model_id":"eleven_multilingual_v2","voice_settings":vs}
    )

    word_timestamps = []
    if r2.status_code == 200:
        al    = r2.json().get('alignment',{})
        chars = al.get('characters',[])
        cs    = al.get('character_start_times_seconds',[])
        ce    = al.get('character_end_times_seconds',[])
        word  = ''; ws = 0
        for i, ch in enumerate(chars):
            if ch == ' ' or i == len(chars)-1:
                if ch != ' ': word += ch
                if word.strip():
                    word_timestamps.append({"word":word.strip(),"start":round(ws,3),"end":round(ce[i] if i<len(ce) else ws+0.3,3)})
                word = ''
                if i+1 < len(cs): ws = cs[i+1]
            else:
                if not word: ws = cs[i] if i<len(cs) else 0
                word += ch
        print(f"   ✓ {len(word_timestamps)} word timestamps from ElevenLabs")
    else:
        words = full_script.split()
        pw    = 60.0 / max(len(words),1)
        word_timestamps = [{"word":w,"start":round(i*pw,3),"end":round((i+1)*pw,3)} for i,w in enumerate(words)]
        print(f"   ⚠️  Estimated {len(word_timestamps)} timestamps (fallback)")

    # Get actual audio duration
    res      = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams',audio_path],capture_output=True,text=True)
    duration = 60.0
    try:
        for s in json.loads(res.stdout).get('streams',[]):
            if s.get('codec_type')=='audio': duration = float(s.get('duration',60))
    except: pass

    print(f"   ✓ Audio duration: {duration:.1f}s")
    return audio_path, word_timestamps, duration


# ============================================================
# STEP 3 — Background music
# ============================================================
def download_music():
    print("🎵 Step 3: Downloading background music...")
    url = random.choice(MUSIC_TRACKS)
    path = "/tmp/music.mp3"
    try:
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(path,'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
            print("   ✓ Music ready")
            return path
    except Exception as e:
        print(f"   ⚠️  Music failed: {e}")
    return None


# ============================================================
# STEP 4 — Replicate AI clips (Claude-directed prompts)
# ============================================================
def generate_ai_clip(prompt, clip_num):
    print(f"   🤖 AI clip {clip_num}: {prompt[:55]}...")
    r = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={"Authorization":f"Bearer {REPLICATE_API_KEY}","Content-Type":"application/json"},
        json={"version":"bytedance/seedance-1-pro","input":{"prompt":prompt,"aspect_ratio":"9:16","duration":5,"resolution":"1080p"}}
    )
    if r.status_code not in (200,201): return None
    pid = r.json().get('id','')
    if not pid: return None

    for _ in range(60):
        time.sleep(5)
        poll   = requests.get(f"https://api.replicate.com/v1/predictions/{pid}",headers={"Authorization":f"Bearer {REPLICATE_API_KEY}"})
        result = poll.json()
        status = result.get('status','')
        if status == 'succeeded':
            output = result.get('output','')
            url    = output if isinstance(output,str) else (output[0] if output else '')
            if url:
                path = f"/tmp/ai_clip_{clip_num}.mp4"
                rr   = requests.get(url,stream=True,timeout=60)
                with open(path,'wb') as f:
                    for chunk in rr.iter_content(chunk_size=8192): f.write(chunk)
                print(f"   ✓ AI clip {clip_num} ready")
                return path
        elif status == 'failed': return None
    return None


# ============================================================
# STEP 5 — Pexels stock footage (Claude-directed searches)
# ============================================================
def get_pexels_clip(search_term, clip_num):
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization":PEXELS_API_KEY},
            params={"query":search_term,"per_page":10,"orientation":"portrait","size":"large"},
            timeout=15
        )
        videos = r.json().get('videos',[])
        if not videos: return None
        video = random.choice(videos[:5])
        files = video.get('video_files',[])
        hd    = [f for f in files if f.get('width',0)>=1080 and f.get('height',0)>=f.get('width',0)]
        if not hd: hd = [f for f in files if f.get('height',0)>=f.get('width',0)]
        if not hd: hd = files
        if not hd: return None
        hd.sort(key=lambda x:x.get('width',0)*x.get('height',0),reverse=True)
        url = hd[0].get('link','')
        if not url: return None
        path = f"/tmp/stock_clip_{clip_num}.mp4"
        rr   = requests.get(url,stream=True,timeout=30)
        with open(path,'wb') as f:
            for chunk in rr.iter_content(chunk_size=8192): f.write(chunk)
        return path
    except: return None


# ============================================================
# STEP 6 — Get all clips following Claude's direction
# ============================================================
def get_all_clips(content):
    print("🎬 Steps 4-5: Fetching clips per Claude's direction...")
    clips = {}
    for scene in content['scenes']:
        n = scene['scene']
        if scene['visual_type'] == 'ai' and scene.get('ai_prompt'):
            clip = generate_ai_clip(scene['ai_prompt'], n)
            clips[n] = clip
        else:
            search = scene.get('stock_search','professional office technology')
            clip   = get_pexels_clip(search, n)
            clips[n] = clip
            if clip: print(f"   ✓ Stock clip {n}: '{search[:35]}'")

    # Fallback for any missing
    for n in range(1, len(content['scenes'])+1):
        if not clips.get(n):
            clips[n] = get_pexels_clip("professional technology office", n)

    ready = sum(1 for c in clips.values() if c)
    print(f"   ✓ Clips ready: {ready}/{len(content['scenes'])}")
    return clips


# ============================================================
# STEP 7 — Render with Remotion
# ============================================================
def render_with_remotion(clips, audio_path, word_timestamps, audio_duration, content, music_path):
    print("✂️  Step 6: Remotion rendering with director data...")

    # Scale scene durations to match actual audio length
    scenes_raw  = content['scenes']
    total_scripted = sum(s['duration'] for s in scenes_raw)
    scale          = audio_duration / max(total_scripted, 1)

    running = 0.0
    scenes  = []
    for i, s in enumerate(scenes_raw):
        if i == len(scenes_raw)-1:
            dur = round(audio_duration - running, 3)
        else:
            dur = round(s['duration'] * scale, 3)
        running += dur

        n = s['scene']
        scenes.append({
            "scene_num":        n,
            "clip_path":        f"scene_{n}.mp4" if clips.get(n) else "",
            "script":           s.get('script',''),
            "start_time":       round(running - dur, 3),
            "duration":         dur,
            "is_ai":            s.get('visual_type','stock') == 'ai',
            "transition_in":    s.get('transition_in','fade'),
            "keyword_overlay":  s.get('keyword_overlay',''),
            "overlay_position": s.get('overlay_position','bottom'),
            "text_color":       s.get('text_color','yellow'),
        })

    remotion_data = {
        "scenes":          scenes,
        "word_timestamps": word_timestamps,
        "total_duration":  audio_duration,
        "course_name":     content['course']['name'],
        "hook":            content.get('hook',''),
        "branding":        "PUMO Technovation  |  016-259 2727",
        "has_music":       music_path is not None,
        "video_format":    content.get('format','story'),
        "format_label":    content.get('format_label','Story-Driven'),
        "keywords":        content.get('keywords',[]),
        "stats":           content.get('stats',[]),
    }

    with open("remotion/public/data.json",'w') as f: json.dump(remotion_data,f)
    subprocess.run(['cp',audio_path,'remotion/public/voiceover.mp3'],check=True)
    if music_path and os.path.exists(music_path):
        subprocess.run(['cp',music_path,'remotion/public/music.mp3'],check=True)
    for s in scenes:
        n    = s['scene_num']
        clip = clips.get(n)
        if clip and os.path.exists(clip):
            subprocess.run(['cp',clip,f'remotion/public/scene_{n}.mp4'],check=True)

    subprocess.run(['npm','install','--save-dev','@remotion/cli@4.0.290'],cwd='remotion',check=True,capture_output=True)

    output = "/tmp/pumo_final.mp4"
    result = subprocess.run(
        ['./node_modules/.bin/remotion','render','src/index.tsx','PUMOVideo',output,'--codec','h264','--video-bitrate','8000K'],
        cwd='remotion',capture_output=True,text=True
    )
    if result.returncode != 0:
        print(f"❌ Remotion:\n{result.stderr[-600:]}")
        sys.exit(1)

    print(f"   ✓ Video rendered — {os.path.getsize(output)/1024/1024:.1f} MB")
    return output


# ============================================================
# STEP 8 — Post to Instagram
# ============================================================
def post_to_instagram(video_path, content):
    print("📲 Step 7: Posting to Instagram...")
    full_cap = f"{content['post_caption']}\n\n{content['hashtags']}"
    with open(video_path,'rb') as f:
        r = requests.post(
            "https://api.upload-post.com/api/upload",
            headers={"Authorization":f"Apikey {UPLOAD_POST_API_KEY}"},
            data={"title":full_cap,"user":INSTAGRAM_USERNAME,"platform[]":"instagram","media_type":"REELS"},
            files={"video":("pumo_video.mp4",f,"video/mp4")}
        )
    ok = r.status_code in (200,201)
    print(f"   {'✓' if ok else '⚠️'} Upload-Post: {r.status_code}")
    if not ok: print(f"   Response: {r.text[:200]}")
    return ok


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  🤖  PUMO Autonomous Instagram Agent v10")
    print(f"  📅  {datetime.utcnow().strftime('%A, %d %B %Y')} (UTC)")
    print("  🎬  Claude Director · 14 Courses · 6 Formats · Dynamic Editing")
    print("=" * 60)

    # Pre-flight — validates everything before spending credits
    preflight_check()

    # Rotation — course and format based on day of year
    doy        = datetime.utcnow().timetuple().tm_yday
    course_idx = doy % len(COURSES)
    fmt_idx    = (doy // len(COURSES)) % len(FORMAT_KEYS)
    course     = COURSES[course_idx]
    fmt_key    = FORMAT_KEYS[fmt_idx]

    print(f"  📚  Course: {course['name']}")
    print(f"  🎭  Format: {VIDEO_FORMATS[fmt_key]['label']}")
    print("=" * 60 + "\n")

    # Run full pipeline
    content                          = generate_directed_content(course, fmt_key)
    audio_path, word_timestamps, dur = generate_voiceover(content['full_script'])
    music_path                       = download_music()
    clips                            = get_all_clips(content)
    video_path                       = render_with_remotion(clips, audio_path, word_timestamps, dur, content, music_path)
    success                          = post_to_instagram(video_path, content)

    print("\n" + "=" * 60)
    print("  ✅  DONE!" if success else "  ⚠️  Done with warnings.")
    print(f"  📚  Course:  {course['name']}")
    print(f"  🎭  Format:  {VIDEO_FORMATS[fmt_key]['label']}")
    print(f"  🎣  Hook:    {content.get('hook','')}")
    print(f"  🎵  Music:   {'Yes' if music_path else 'No'}")
    print(f"  📸  Posted:  Instagram Reels")
    print("=" * 60)

if __name__ == "__main__":
    main()
