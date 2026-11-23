import html
import json
import os
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
QUEUE_PATH = os.path.join(PROJECT_DIR, "swarm_queue.json")
PORT = 8500


def load_queue() -> list:
    if os.path.exists(QUEUE_PATH):
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_queue(queue: list) -> None:
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def get_media_list(item: dict) -> list:
    paths = item.get("media_paths")
    if isinstance(paths, list):
        return [p.strip() for p in paths if p and p.strip()]
    single = item.get("media_path", "").strip()
    return [single] if single else []


def render_page(queue: list, filter_status: str = "SCHEDULED", filter_account: str = "ALL", sort_by: str = "day") -> str:
    counts = {
        "PENDING_APPROVAL": sum(1 for x in queue if x.get("status") == "PENDING_APPROVAL"),
        "APPROVED": sum(1 for x in queue if x.get("status") == "APPROVED"),
        "SCHEDULED": sum(1 for x in queue if x.get("status") == "SCHEDULED"),
        "PUBLISHED": sum(1 for x in queue if x.get("status") == "PUBLISHED"),
        "REJECTED": sum(1 for x in queue if x.get("status") == "REJECTED"),
    }
    items = [
        x for x in queue
        if (filter_status == "ALL" or x.get("status") == filter_status)
        and (filter_account == "ALL" or x.get("account") == filter_account)
    ]
    if sort_by == "score":
        items.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
    else:
        items.sort(key=lambda x: (x.get("day_index") or 999, x.get("account", ""), -x.get("viral_score", 0)))

    cards_html = []
    for item in items:
        item_id = html.escape(str(item.get("id", "")))
        account = html.escape(item.get("account", ""))
        status = html.escape(item.get("status", ""))
        fmt = html.escape(item.get("format", "Carousel (3 frames)"))
        pillar = html.escape(item.get("pillar", ""))
        location = html.escape(item.get("location", ""))
        prompt = html.escape(item.get("image_prompt", ""))
        caption = html.escape(item.get("caption", ""))
        created_at = html.escape(item.get("created_at", ""))
        viral_score = int(item.get("viral_score", 0))
        viral_reason = html.escape(item.get("viral_reason", ""))
        day_label = html.escape(item.get("day_label", f"Day {item.get('day_index', '?')}"))
        scheduled_for = html.escape(item.get("scheduled_for", "Unscheduled"))

        raw_tags = item.get("tagged_users") or item.get("tags") or []
        tags_str = ", ".join(raw_tags) if isinstance(raw_tags, list) else str(raw_tags)
        alt_text = html.escape(item.get("alt_text", ""))

        media_list = get_media_list(item)
        media_text = html.escape("\n".join(media_list))

        existing_imgs = [p for p in media_list if os.path.exists(p)]
        if existing_imgs:
            thumbs = "".join(
                f'<video src="/media?path={urllib.parse.quote(p)}" controls muted playsinline style="width:100%; max-height:220px; border-radius:6px; object-fit:cover;"></video>'
                if p.lower().endswith((".mp4", ".mov")) else
                f'<img src="/media?path={urllib.parse.quote(p)}" alt="slide" />'
                for p in existing_imgs
            )
            img_preview = f'<div class="carousel-strip">{thumbs}</div><div class="slide-count">✓ {len(existing_imgs)}/3 4:5 2K Slides Attached</div>'
        else:
            img_preview = (
                f'<div class="no-img">Drop 1 or more images in draft_media/{account}/<br>'
                f'or paste multiple file paths (one per line)</div>'
            )

        score_class = "score-high" if viral_score >= 82 else ("score-mid" if viral_score >= 65 else "score-low")
        tags_pill = "".join(f'<span class="badge tag-pill">@{html.escape(t.strip())}</span>' for t in tags_str.split(",") if t.strip())

        cards_html.append(f"""
        <div class="card">
          <div class="card-head">
            <span class="badge day-badge">{day_label}</span>
            <span class="badge account">@{account}</span>
            <span class="badge id-badge">ID: {item_id}</span>
            <span class="badge {score_class}">Score: {viral_score}/100</span>
            <span class="badge status-{status.lower()}">{status}</span>
            <span class="meta">📍 {location}</span>
          </div>
          <div class="tags-row">
            <span class="tags-label">Tagged Accounts:</span> {tags_pill}
            <span class="sched-pill">🕒 Scheduled For: <strong>{scheduled_for}</strong></span>
          </div>
          <div class="viral-note">{viral_reason}</div>
          <div class="card-body">
            <div class="preview">{img_preview}</div>
            <form method="POST" action="/action" class="fields">
              <input type="hidden" name="id" value="{item_id}" />
              <label>Content Pillar</label>
              <div class="pillar">{pillar}</div>
              
              <div class="row-2col">
                <div>
                  <label>Location Geotag</label>
                  <input type="text" name="location" value="{location}" class="text-input" />
                </div>
                <div>
                  <label>Tagged Accounts (comma-separated)</label>
                  <input type="text" name="tags" value="{html.escape(tags_str)}" class="text-input" />
                </div>
              </div>

              <label>Image Accessibility / Alt Text (SEO)</label>
              <textarea name="alt_text" rows="2" class="alt-box">{alt_text}</textarea>

              <label>Media File Paths (1692×2114 4:5 2K)</label>
              <textarea name="media_paths" rows="3">{media_text}</textarea>

              <label>Instagram Caption & Hashtags</label>
              <textarea name="caption" rows="4">{caption}</textarea>

              <div class="actions">
                <button type="submit" name="decision" value="APPROVE" class="btn approve">Approve & Queue</button>
                <button type="submit" name="decision" value="SAVE" class="btn save">Save All Edits</button>
                <button type="submit" name="decision" value="REJECT" class="btn reject">Reject</button>
              </div>
            </form>
          </div>
        </div>
        """)

    cards_block = "\n".join(cards_html) if cards_html else '<div class="empty">No drafts in this view.</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Resrise Swarm Approval Dashboard</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #0d1117; color: #e6edf3; margin: 0; padding: 24px; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; }}
    h1 {{ margin: 0 0 6px; font-size: 24px; }}
    .sub {{ color: #8b949e; margin-bottom: 18px; font-size: 14px; }}
    .tabs {{ display: flex; gap: 10px; margin-bottom: 22px; flex-wrap: wrap; }}
    .tab {{ padding: 8px 14px; border-radius: 8px; background: #161b22; color: #c9d1d9; text-decoration: none; border: 1px solid #30363d; font-size: 13px; }}
    .tab.active {{ background: #238636; color: #fff; border-color: #238636; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 18px; margin-bottom: 18px; }}
    .card-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }}
    .badge {{ padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .day-badge {{ background: #8957e533; color: #d2a8ff; border: 1px solid #8957e5; }}
    .account {{ background: #1f6feb33; color: #58a6ff; font-weight: 700; }}
    .id-badge {{ background: #30363d; color: #8b949e; font-family: monospace; font-size: 11px; }}
    .score-high {{ background: #23863644; color: #3fb950; border: 1px solid #238636; }}
    .score-mid {{ background: #d2992233; color: #e3b341; border: 1px solid #d29922; }}
    .score-low {{ background: #f8514933; color: #ff7b72; }}
    .status-pending_approval {{ background: #d2992233; color: #e3b341; }}
    .status-approved {{ background: #23863633; color: #3fb950; }}
    .status-scheduled {{ background: #1f6feb33; color: #58a6ff; }}
    .status-published {{ background: #8957e533; color: #bc8cff; }}
    .status-rejected {{ background: #f8514933; color: #ff7b72; }}
    .meta {{ color: #8b949e; font-size: 12px; margin-left: auto; }}
    .tags-row {{ display: flex; align-items: center; gap: 6px; margin-bottom: 10px; font-size: 12px; flex-wrap: wrap; }}
    .tags-label {{ color: #8b949e; font-weight: 600; }}
    .tag-pill {{ background: #21262d; color: #58a6ff; border: 1px solid #30363d; padding: 2px 8px; font-size: 11px; }}
    .sched-pill {{ margin-left: auto; color: #a5d6ff; font-size: 12px; }}
    .viral-note {{ font-size: 12px; color: #8b949e; margin-bottom: 14px; }}
    .card-body {{ display: grid; grid-template-columns: 290px 1fr; gap: 18px; }}
    .carousel-strip {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }}
    .carousel-strip img {{ width: 100%; height: 125px; border-radius: 6px; object-fit: cover; border: 1px solid #30363d; }}
    .slide-count {{ margin-top: 8px; font-size: 12px; color: #3fb950; font-weight: 600; text-align: center; }}
    .no-img {{ height: 240px; border: 1px dashed #30363d; border-radius: 8px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 14px; color: #8b949e; font-size: 13px; }}
    .fields {{ display: flex; flex-direction: column; gap: 8px; }}
    .row-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    label {{ font-size: 12px; color: #8b949e; font-weight: 600; }}
    .pillar {{ font-size: 14px; font-weight: 600; color: #f0f6fc; margin-bottom: 2px; }}
    .text-input {{ width: 100%; box-sizing: border-box; background: #0d1117; color: #e6edf3; border: 1px solid #30363d; border-radius: 6px; padding: 7px 10px; font-family: inherit; font-size: 12px; }}
    textarea {{ width: 100%; box-sizing: border-box; background: #0d1117; color: #e6edf3; border: 1px solid #30363d; border-radius: 6px; padding: 8px 10px; font-family: inherit; font-size: 12px; }}
    .alt-box {{ color: #7ee787; font-size: 11px; }}
    .actions {{ display: flex; gap: 10px; margin-top: 6px; }}
    .btn {{ padding: 8px 14px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px; }}
    .approve {{ background: #238636; color: #fff; }}
    .save {{ background: #1f6feb; color: #fff; }}
    .reject {{ background: #da3633; color: #fff; }}
    .empty {{ padding: 40px; text-align: center; color: #8b949e; background: #161b22; border-radius: 12px; border: 1px solid #30363d; }}
    @media (max-width: 760px) {{ .card-body {{ grid-template-columns: 1fr; }} .row-2col {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Resrise Swarm Approval Dashboard</h1>
    <div class="sub">100% Attire-Matched Carousels with Complete IDs, Geotags, Alt Text & User Tags across @avanyamehra, @mairamehraofficial, and @iamgagankumar.</div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
      <div class="tabs" style="margin-bottom: 0;">
        <a class="tab {'active' if filter_status == 'SCHEDULED' else ''}" href="/?status=SCHEDULED&account={filter_account}&sort={sort_by}">Scheduled ({counts['SCHEDULED']})</a>
        <a class="tab {'active' if filter_status == 'APPROVED' else ''}" href="/?status=APPROVED&account={filter_account}&sort={sort_by}">Approved ({counts['APPROVED']})</a>
        <a class="tab {'active' if filter_status == 'PENDING_APPROVAL' else ''}" href="/?status=PENDING_APPROVAL&account={filter_account}&sort={sort_by}">Pending ({counts['PENDING_APPROVAL']})</a>
        <a class="tab {'active' if filter_status == 'PUBLISHED' else ''}" href="/?status=PUBLISHED&account={filter_account}&sort={sort_by}">Published ({counts['PUBLISHED']})</a>
        <a class="tab {'active' if filter_status == 'REJECTED' else ''}" href="/?status=REJECTED&account={filter_account}&sort={sort_by}">Rejected ({counts['REJECTED']})</a>
        <a class="tab {'active' if filter_status == 'ALL' else ''}" href="/?status=ALL&account={filter_account}&sort={sort_by}">All ({len(queue)})</a>
      </div>
      <form method="POST" action="/schedule_all_approved" style="margin: 0;">
        <button type="submit" title="Publishes due posts via Official Meta Graph API v27.0 (Zero Playwright Risk)" style="background: #1f6feb; color: #fff; border: 1px solid #388bfd; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 14px; box-shadow: 0 2px 8px rgba(31,111,235,0.4); display: flex; align-items: center; gap: 8px;">
          🚀 Dispatch Approved via API ({counts['APPROVED']})
        </button>
      </form>
    </div>
    <div class="cards">{cards_block}</div>
  </div>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/media":
            qs = urllib.parse.parse_qs(parsed.query)
            target = qs.get("path", [""])[0]
            if os.path.exists(target) and os.path.isfile(target):
                self.send_response(200)
                ext = os.path.splitext(target)[1].lower()
                if ext in (".mp4", ".m4v"):
                    mime = "video/mp4"
                elif ext == ".mov":
                    mime = "video/quicktime"
                elif ext == ".png":
                    mime = "image/png"
                else:
                    mime = "image/jpeg"
                self.send_header("Content-Type", mime)
                self.send_header("Cache-Control", "max-age=3600")
                self.end_headers()
                with open(target, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
            return

        qs = urllib.parse.parse_qs(parsed.query)
        f_status = qs.get("status", ["SCHEDULED"])[0]
        f_account = qs.get("account", ["ALL"])[0]
        sort_by = qs.get("sort", ["day"])[0]

        queue = load_queue()
        body = render_page(queue, f_status, f_account, sort_by).encode("utf-8")
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
            pass

    def do_POST(self):
        if self.path == "/schedule_all_approved":
            import subprocess
            import sys
            pub_script = os.path.join(SCRIPT_DIR, "ig_publisher_api.py")
            subprocess.Popen([sys.executable, pub_script])
            self.send_response(303)
            self.send_header("Location", self.headers.get("Referer", "/"))
            self.end_headers()
            return

        if self.path != "/action":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        form = urllib.parse.parse_qs(raw, keep_blank_values=True)

        item_id = form.get("id", [""])[0]
        decision = form.get("decision", ["SAVE"])[0]
        caption = form.get("caption", [""])[0]
        location = form.get("location", [""])[0]
        tags_raw = form.get("tags", [""])[0]
        alt_text = form.get("alt_text", [""])[0]
        raw_paths = form.get("media_paths", [""])[0]
        media_paths = [line.strip() for line in raw_paths.splitlines() if line.strip()]

        tags_list = [t.strip().lstrip("@") for t in tags_raw.replace(",", " ").split() if t.strip()]

        queue = load_queue()
        for item in queue:
            if str(item.get("id")) == str(item_id):
                item["caption"] = caption
                item["location"] = location
                item["tagged_users"] = tags_list
                item["tags"] = tags_list
                item["alt_text"] = alt_text
                item["media_paths"] = media_paths
                item.pop("media_path", None)
                if decision == "APPROVE":
                    item["status"] = "APPROVED"
                elif decision == "REJECT":
                    item["status"] = "REJECTED"
                break
        save_queue(queue)

        self.send_response(303)
        self.send_header("Location", self.headers.get("Referer", "/"))
        self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    url = f"http://localhost:{PORT}/"
    print(f"Resrise Swarm Approval Dashboard running at {url}")
    while True:
        try:
            server = ThreadingHTTPServer(("0.0.0.0", PORT), DashboardHandler)
            server.daemon_threads = True
            server.serve_forever()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Server error, restarting in 1s: {e}")
            import time
            time.sleep(1)


if __name__ == "__main__":
    main()
