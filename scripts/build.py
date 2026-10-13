"""Build data.json for The Horizon 360 and record any missing audio editions.

Reads:   articles/*.txt, editions/*.pdf, team.txt, contact.txt, assets/logo.(png|jpg|jpeg|webp)
Writes:  data.json, audio/<article>.mp3, audio/manifest.json

Run with --no-audio to only rebuild data.json.
"""
import glob, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
VOICE = "af_heart"
MODEL_DIR = os.environ.get("KOKORO_DIR", "/tmp/kokoro")


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "item"


def added_time(path):
    """When the file was first committed (falls back to file time)."""
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--follow", "--format=%ct", "--", path],
                             capture_output=True, text=True, check=True).stdout.split()
        if out:
            return int(out[-1])
    except Exception:
        pass
    return int(os.path.getmtime(path))


def parse_article(path):
    raw = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n")
    meta, body = {}, raw
    if "\n---" in raw or raw.startswith("---"):
        head, _, body = raw.partition("\n---\n") if "\n---\n" in raw else raw.partition("---\n")
        for line in head.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
    else:
        lines = raw.strip().splitlines()
        meta["title"] = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:])
    body = re.sub(r"\n{3,}", "\n\n", body.strip())
    name = os.path.splitext(os.path.basename(path))[0]
    return {
        "id": slug(name),
        "title": meta.get("title") or name.replace("-", " ").title(),
        "author": meta.get("author") or meta.get("by") or "",
        "category": meta.get("section") or meta.get("category") or "",
        "issue": meta.get("issue") or meta.get("month") or "",
        "body": body,
        "_added": added_time(path),
    }


def spoken_text(a):
    t = f"{a['title']}.\n\n" + (f"By {a['author']}.\n\n" if a["author"] else "") + a["body"]
    t = re.sub(r"(\d+)s-(\d+)s", lambda m: f"{m.group(1)}s to {m.group(2)}s", t)
    t = re.sub(r"\b20s\b", "twenties", t); t = re.sub(r"\b30s\b", "thirties", t)
    t = re.sub(r"\b40s\b", "forties", t); t = re.sub(r"\b50s\b", "fifties", t); t = re.sub(r"\b60s\b", "sixties", t)
    t = re.sub(r"(?<=[A-Za-z])/(?=[A-Za-z])", " or ", t)
    t = t.replace("&", " and ")
    return t


_kokoro = None
def synth(text, out_mp3):
    global _kokoro
    import numpy as np, soundfile as sf
    from kokoro_onnx import Kokoro
    if _kokoro is None:
        _kokoro = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.int8.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    parts = []
    for p in [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]:
        a, sr = _kokoro.create(p, voice=VOICE, speed=1.0, lang="en-us")
        parts += [a, np.zeros(int(sr * (0.7 if len(p) < 40 else 0.45)), dtype=np.float32)]
    sf.write(out_mp3, np.concatenate(parts), 24000, format="MP3", bitrate_mode="CONSTANT", compression_level=0.75)


def main():
    make_audio = "--no-audio" not in sys.argv
    os.makedirs("audio", exist_ok=True)
    man_path = "audio/manifest.json"
    manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}

    articles = [parse_article(p) for p in sorted(glob.glob("articles/*.txt")) if not os.path.basename(p).startswith("_")]
    articles = [a for a in articles if a["body"]]
    articles.sort(key=lambda a: (a["issue"], a["_added"]), reverse=True)

    for a in articles:
        mp3 = f"audio/{a['id']}.mp3"
        h = hashlib.sha1(spoken_text(a).encode()).hexdigest()
        custom = os.path.exists(mp3) and a["id"] not in manifest   # someone uploaded their own recording
        if make_audio and not custom and manifest.get(a["id"]) != h:
            print("Recording:", a["title"])
            synth(spoken_text(a), mp3)
            manifest[a["id"]] = h
        a["audio"] = mp3 if os.path.exists(mp3) else ""

    # remove audio for deleted articles
    ids = {a["id"] for a in articles}
    for k in list(manifest):
        if k not in ids:
            manifest.pop(k)
            if os.path.exists(f"audio/{k}.mp3"):
                os.remove(f"audio/{k}.mp3")
    json.dump(manifest, open(man_path, "w"), indent=1)

    editions = []
    for p in glob.glob("editions/*.pdf"):
        stem = os.path.splitext(os.path.basename(p))[0]
        m = re.match(r"(\d{4})[-_ ](\d{1,2})[\s_-]*(.*)", stem)
        month = f"{m.group(1)}-{int(m.group(2)):02d}" if m else ""
        title = (m.group(3) if m else stem).replace("_", " ").strip() or "Edition"
        editions.append({"id": slug(stem), "title": title, "month": month, "pdf": p, "_added": added_time(p)})
    editions.sort(key=lambda e: (e["month"], e["_added"]), reverse=True)

    team = []
    if os.path.exists("team.txt"):
        for line in open("team.txt", encoding="utf-8-sig"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"\s+[-–—]\s+", line, maxsplit=1)
            team.append({"name": parts[0].strip(), "role": parts[1].strip() if len(parts) > 1 else ""})

    contact = {"email": ""}
    if os.path.exists("contact.txt"):
        for line in open("contact.txt", encoding="utf-8-sig"):
            if line.lower().startswith("email:"):
                contact["email"] = line.split(":", 1)[1].strip()

    logo = next((p for p in sorted(glob.glob("assets/logo.*")) if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg"))), None)

    for x in articles + editions:
        x.pop("_added", None)
    json.dump({"articles": articles, "editions": editions, "team": team, "contact": contact, "logo": logo},
              open("data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"data.json: {len(articles)} articles, {len(editions)} editions, {len(team)} team members")


if __name__ == "__main__":
    main()
