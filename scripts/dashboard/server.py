"""Resrise Swarm Approval Dashboard - Local HTTP server for reviewing drafts."""
import html
import json
import os
import urllib.parse
import uuid
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.config import get_settings, load_queue, save_queue
from ..core.logging import get_logger
from ..core.utils import get_valid_media_paths, get_media_list, is_subpath


PORT = 8500
ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar"]


logger = get_logger("resrise.dashboard")


def scan_and_attach_media(queue: List[Dict[str, Any]]) -> int:
    """Scan draft_media/<account>/ and attach unassigned files to pending drafts."""
    settings = get_settings()
    used_files = set()
    for item in queue:
        for p in get_media_list(item):
            used_files.add(os.path.normcase(os.path.abspath(p)))
        if item.get("media_path"):
            used_files.add(os.path.normcase(os.path.abspath(item["media_path"])))

    valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov")
    attached_count = 0

    for account in ACCOUNTS:
        acc_dir = settings.draft_media_dir / account
        acc_dir.mkdir(parents=True, exist_ok=True)
        unassigned = []
        for fname in sorted(os.listdir(acc_dir)):
            if fname.lower().endswith(valid_exts):
                full_path = os.path.abspath(os.path.join(acc_dir, fname))
                if os.path.normcase(full_path) not in used_files:
                    unassigned.append(full_path)

        if not unassigned:
            continue

        # Attach to existing PENDING_APPROVAL drafts with no media first
        for item in queue:
            if not unassigned:
                break
            if (
                item.get("account") == account
                and item.get("status") == "PENDING_APPROVAL"
                and not get_media_list(item)
            ):
                limit = 10 if "Carousel" in item.get("format", "") else 1
                batch = unassigned[:limit]
                unassigned = unassigned[limit:]
                item["media_paths"] = batch
                if len(batch) > 1 and "Carousel" not in item.get("format", ""):
                    item["format"] = f"Carousel ({len(batch)} frames)"
                attached_count += len(batch)

        # Create new pending carousel drafts for any remaining unassigned files
        while unassigned:
            batch = unassigned[:10]
            unassigned = unassigned[10:]
            fmt = f"Carousel ({len(batch)} frames)" if len(batch) > 1 else "Single Portrait (4:5)"
            queue.append({
                "id": str(uuid.uuid4())[:8],
                "account": account,
                "display_name": account,
                "status": "PENDING_APPROVAL",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "format": fmt,
                "pillar": "Auto-Imported Visual Batch",
                "location": "Studio / Editorial",
                "viral_score": 84 if len(batch) > 1 else 76,
                "viral_reason": "Auto-imported from draft_media folder.",
                "image_prompt": "Imported directly from draft_media folder.",
                "caption": f"New visual drop for @{account}. ✨\n\n#{account} #ResriseStudio",
                "media_paths": batch,
            })
            attached_count += len(batch)

    return attached_count


def render_page(
    queue: List[Dict[str, Any]],
    filter_status: str = "PENDING_APPROVAL",
    notice: str = "",
) -> str:
    """Render the dashboard HTML page."""
    counts = {
        "PENDING_APPROVAL": sum(1 for x in queue if x.get("status") == "PENDING_APPROVAL"),
        "APPROVED": sum(1 for x in queue if x.get("status") == "APPROVED"),
        "PUBLISHED": sum(1 for x in queue if x.get("status") == "PUBLISHED"),
        "REJECTED": sum(1 for x in queue if x.get("status") == "REJECTED"),
    }
    items = [x for x in queue if filter_status == "ALL" or x.get("status") == filter_status]
    items.sort(key=lambda x: x.get("viral_score", 0), reverse=True)

    cards_html = []
    for item in items:
        item_id = html.escape(item.get("id", ""))
        account = html.escape(item.get("account", ""))
        status = html.escape(item.get("status", ""))
        fmt = html.escape(item.get("format", ""))
        pillar = html.escape(item.get("pillar", ""))
        location = html.escape(item.get("location", ""))
        prompt = html.escape(item.get("image_prompt", ""))
        caption = html.escape(item.get("caption", ""))
        created_at = html.escape(item.get("created_at", ""))
        viral_score = int(item.get("viral_score", 0))
        viral_reason = html.escape(item.get("viral_reason", ""))

        media_list = get_media_list(item)
        media_text = html.escape("\n".join(media_list))

        existing_imgs = [p for p in media_list if os.path.exists(p)]
        if existing_imgs:
            thumbs = "".join(
                f'<img src="/media?path={urllib.parse.quote(p)}" alt="slide" />'
                for p in existing_imgs
            )
            img_preview = f'<div class="carousel-strip">{thumbs}</div><div class="slide-count">{len(existing_imgs)} image(s) attached</div>'
        else:
            img_preview = (
                f'<div class="no-img">Drop 1–10 images in draft_media/{account}/<br>'
                f'and click "Scan draft_media/" above</div>'
            )

        score_class = "score-high" if viral_score >= 82 else ("score-mid" if viral_score >= 65 else "score-low")

        cards_html.append(f"""
        <div class="card">
          <div class="card-head">
            <span class="badge account">@{account}</span>
            <span class="badge {score_class}">Viral Score: {viral_score}/100</span>
            <span class="badge status-{status.lower()}">{status}</span>
            <span class="meta">{fmt} • {location} • {created_at}</span>
          </div>
          <div class="viral-note">{viral_reason}</div>
          <div class="card-body">
            <div class="preview">{img_preview}</div>
            <form method="POST" action="/action" class="fields">
              <input type="hidden" name="id" value="{item_id}" />
              <label>Content Pillar</label>
              <div class="pillar">{pillar}</div>
              <label>Google Flow / Image Prompt (copy to generate visuals)</label>
              <textarea readonly rows="3" class="prompt-box">{prompt}</textarea>
              <label>Media File Paths (1 per line — supports up to 10 slides for Carousels)</label>
              <textarea name="media_paths" rows="3" placeholder="draft_media/{account}/slide1.jpg">{media_text}</textarea>
              <label>Instagram Caption & Hashtags (editable)</label>
              <textarea name="caption" rows="4">{caption}</textarea>
              <div class="actions">
                <button type="submit" name="decision" value="APPROVE" class="btn approve">Approve</button>
                <button type="submit" name="decision" value="SAVE" class="btn save">Save Edits</button>
                <button type="submit" name="decision" value="REJECT" class="btn reject">Reject</button>
              </div>
            </form>
          </div>
        </div>
        """)

    cards_block = "\n".join(cards_html) if cards_html else (
        '<div class="empty">No drafts in this view. Run swarm_orchestrator.py or drop images in draft_media/ and click Scan.</div>'
    )
    notice_html = f'<div class="notice">{html.escape(notice)}</div>' if notice else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Resrise Swarm Approval Dashboard</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #0d1117; color: #e6edf3; margin: 0; padding: 24px; }}
    .wrap {{ max-width: 1160px; margin: 0 auto; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }}
    h1 {{ margin: 0 0 6px; font-size: 24px; }}
    .sub {{ color: #8b949e; margin-bottom: 18px; font-size: 14px; }}
    .notice {{ background: #1f6feb33; border: 1px solid #1f6feb; color: #79c0ff; padding: 10px 14px; border-radius: 8px; margin-bottom: 16px; font-size: 13px; }}
    .tabs {{ display: flex; gap: 10px; margin-bottom: 22px; flex-wrap: wrap; align-items: center; }}
    .tab {{ padding: 8px 14px; border-radius: 8px; background: #161b22; color: #c9d1d9; text-decoration: none; border: 1px solid #30363d; font-size: 13px; }}
    .tab.active {{ background: #238636; color: #fff; border-color: #238636; }}
    .scan-btn {{ padding: 8px 14px; border-radius: 8px; background: #8957e5; color: #fff; border: none; font-weight: 600; font-size: 13px; cursor: pointer; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 18px; margin-bottom: 18px; }}
    .card-head {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }}
    .badge {{ padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .account {{ background: #1f6feb33; color: #58a6ff; }}
    .score-high {{ background: #23863644; color: #3fb950; border: 1px solid #238636; }}
    .score-mid {{ background: #d2992233; color: #e3b341; border: 1px solid #d29922; }}
    .score-low {{ background: #f8514933; color: #ff7b72; }}
    .viral-note {{ font-size: 12px; color: #8b949e; margin-bottom: 14px; }}
    .status-pending_approval {{ background: #d2992233; color: #e3b341; }}
    .status-approved {{ background: #23863633; color: #3fb950; }}
    .status-published {{ background: #8957e533; color: #bc8cff; }}
    .status-rejected {{ background: #f8514933; color: #ff7b72; }}
    .meta {{ color: #8b949e; font-size: 12px; margin-left: auto; }}
    .card-body {{ display: grid; grid-template-columns: 270px 1fr; gap: 18px; }}
    .carousel-strip {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; max-height: 360px; overflow-y: auto; }}
    .carousel-strip img {{ width: 100%; height: 120px; border-radius: 8px; object-fit: cover; border: 1px solid #30363d; }}
    .slide-count {{ margin-top: 8px; font-size: 12px; color: #8b949e; text-align: center; }}
    .no-img {{ height: 240px; border: 1px dashed #30363d; border-radius: 8px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 14px; color: #8b949e; font-size: 13px; }}
    .fields {{ display: flex; flex-direction: column; gap: 8px; }}
    label {{ font-size: 12px; color: #8b949e; font-weight: 600; }}
    .pillar {{ font-size: 14px; font-weight: 600; color: #f0f6fc; margin-bottom: 4px; }}
    textarea {{ width: 100%; box-sizing: border-box; background: #0d1117; color: #e6edf3; border: 1px solid #30363d; border-radius: 8px; padding: 10px; font-family: inherit; font-size: 13px; }}
    .prompt-box {{ color: #a5d6ff; }}
    .actions {{ display: flex; gap: 10px; margin-top: 6px; }}
    .btn {{ padding: 9px 16px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px; }}
    .approve {{ background: #238636; color: #fff; }}
    .save {{ background: #1f6feb; color: #fff; }}
    .reject {{ background: #da3633; color: #fff; }}
    .empty {{ padding: 40px; text-align: center; color: #8b949e; background: #161b22; border-radius: 12px; border: 1px solid #30363d; }}
    @media (max-width: 760px) {{ .card-body {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1>Resrise Swarm Approval Dashboard</h1>
        <div class="sub">Sorted by Viral Score (highest first). Supports single posts and up to 10-slide Carousels across @avanyamehra, @mairamehraofficial, and @iamgagankumar.</div>
      </div>
      <form method="POST" action="/scan">
        <button type="submit" class="scan-btn">Scan draft_media/ & Auto-Attach</button>
      </form>
    </div>
    {notice_html}
    <div class="tabs">
      <a class="tab {'active' if filter_status == 'PENDING_APPROVAL' else ''}" href="/?status=PENDING_APPROVAL">Pending ({counts['PENDING_APPROVAL']})</a>
      <a class="tab {'active' if filter_status == 'APPROVED' else ''}" href="/?status=APPROVED">Approved ({counts['APPROVED']})</a>
      <a class="tab {'active' if filter_status == 'PUBLISHED' else ''}" href="/?status=PUBLISHED">Published ({counts['PUBLISHED']})</a>
      <a class="tab {'active' if filter_status == 'REJECTED' else ''}" href="/?status=REJECTED">Rejected ({counts['REJECTED']})</a>
      <a class="tab {'active' if filter_status == 'ALL' else ''}" href="/?status=ALL">All ({len(queue)})</a>
    </div>
    {cards_block}
  </div>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)

        # Serve media files with path traversal protection
        if parsed.path == "/media":
            qs = urllib.parse.parse_qs(parsed.query)
            file_path = qs.get("path", [""])[0]
            if file_path:
                settings = get_settings()
                real_project = os.path.realpath(settings.project_dir)
                real_target = os.path.realpath(file_path)

                # Security: ensure file is within project directory
                if is_subpath(Path(real_target), Path(real_project)) and os.path.isfile(real_target):
                    ext = os.path.splitext(real_target)[1].lower()
                    mime = {
                        ".jpg": "image/jpeg",
                        ".jpeg": "image/jpeg",
                        ".png": "image/png",
                        ".webp": "image/webp",
                    }.get(ext, "application/octet-stream")
                    with open(real_target, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", mime)
                    self.end_headers()
                    self.wfile.write(data)
                    return

            self.send_error(403 if file_path else 404)
            return

        # Main dashboard page
        qs = urllib.parse.parse_qs(parsed.query)
        status = qs.get("status", ["PENDING_APPROVAL"])[0]
        notice = qs.get("notice", [""])[0]
        queue = load_queue()
        body = render_page(queue, status, notice).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path == "/scan":
            queue = load_queue()
            count = scan_and_attach_media(queue)
            save_queue(queue)
            msg = urllib.parse.quote(f"Scan complete: attached {count} new media file(s) from draft_media/.")
            self.send_response(303)
            self.send_header("Location", f"/?notice={msg}")
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
        raw_paths = form.get("media_paths", [""])[0]
        media_paths = [line.strip() for line in raw_paths.splitlines() if line.strip()]

        queue = load_queue()
        for item in queue:
            if item.get("id") == item_id:
                item["caption"] = caption
                item["media_paths"] = media_paths
                item.pop("media_path", None)
                if decision == "APPROVE":
                    item["status"] = "APPROVED"
                elif decision == "REJECT":
                    item["status"] = "REJECTED"
                break
        save_queue(queue)

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        """Suppress default log messages."""
        pass


def main() -> None:
    """Run the dashboard server."""
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Resrise Swarm Approval Dashboard running at {url}")
    print("Press Ctrl+C in this terminal to stop.")
    webbrowser.open(url)
    HTTPServer(("127.0.0.1", PORT), DashboardHandler).serve_forever()


if __name__ == "__main__":
    main()