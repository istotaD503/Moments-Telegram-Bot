"""
Report command handler — generates an AI-powered summary of the user's stories.
"""
import html
import logging
import os
import re
import tempfile
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .shared import story_db
from services.openai_client import get_openai_client

logger = logging.getLogger(__name__)

PROMPT_ID = "pmpt_69bc64df5b2081949736fe897ca179480007682866b5cd6b"
PROMPT_VERSION = "6"

TELEGRAM_MAX_LENGTH = 4096


class ReportCommandHandlers:
    story_db = story_db

    @staticmethod
    async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        all_stories = ReportCommandHandlers.story_db.get_user_stories(user.id)

        if not all_stories:
            await update.message.reply_text(
                "You haven't recorded any moments yet.\n\nUse /story to capture your first storyworthy moment!"
            )
            return

        cutoff = (datetime.utcnow() - timedelta(weeks=2)).date()
        recent = [s for s in all_stories if s['created_at'][:10] >= str(cutoff)]

        if not recent:
            last_date = all_stories[0]['created_at'][:10]
            keyboard = [[InlineKeyboardButton("📊 Generate from all stories", callback_data="report:all")]]
            await update.message.reply_text(
                f"No new moments in the last 2 weeks — your last entry was on <b>{last_date}</b>.\n\n"
                "Keep the habit going with /story, or generate a report from everything you've captured so far.",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        thinking_msg = await update.message.reply_text("🧠 Generating your report…")
        await _generate_and_send_report(recent, reply_to=update.message, thinking_msg=thinking_msg)

    @staticmethod
    async def report_all_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        all_stories = ReportCommandHandlers.story_db.get_user_stories(query.from_user.id)
        await query.edit_message_text("🧠 Generating your report…")
        await _generate_and_send_report(all_stories, reply_to=query.message, thinking_msg=query.message)


async def _generate_and_send_report(stories, reply_to, thinking_msg) -> None:
    moments = "\n\n".join(
        f"[{s['created_at'][:10]}] {s['story_text']}" for s in stories
    )
    # stories are newest-first; oldest is last
    start_date = stories[-1]['created_at'][:10]
    end_date = stories[0]['created_at'][:10]
    period = start_date if start_date == end_date else f"{start_date} to {end_date}"

    client = get_openai_client()
    response = await client.responses.create(
        prompt={
            "id": PROMPT_ID,
            "version": PROMPT_VERSION,
            "variables": {"period": period, "moments": moments},
        },
        input=[],
        reasoning={"summary": "auto"},
        store=True,
        include=[
            "reasoning.encrypted_content",
            "web_search_call.action.sources",
        ],
    )

    intro_md, rest_md = _split_report(response.output_text)

    # Send intro as Telegram message
    header = "🧠 <b>Your Story Report</b>\n\n"
    intro_html = _md_to_html(intro_md)
    full_intro = header + intro_html

    if len(full_intro) <= TELEGRAM_MAX_LENGTH:
        await thinking_msg.edit_text(full_intro, parse_mode='HTML')
    else:
        await thinking_msg.delete()
        chunks = _split_text(intro_html, TELEGRAM_MAX_LENGTH - len(header))
        await reply_to.reply_text(header + chunks[0], parse_mode='HTML')
        for chunk in chunks[1:]:
            await reply_to.reply_text(chunk, parse_mode='HTML')

    # Send rest as HTML file
    if rest_md.strip():
        export_date = datetime.now().strftime('%Y-%m-%d')
        html_content = _build_report_html(rest_md, period)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name

        try:
            filename = f"report_{export_date}.html"
            with open(temp_path, 'rb') as doc_file:
                await reply_to.reply_document(
                    document=doc_file,
                    filename=filename,
                    caption="📄 Full report details"
                )
        finally:
            os.unlink(temp_path)


def _split_report(text: str):
    """Split at the 'Small moments that were bigger' section heading."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#') and 'small moment' in stripped.lower():
            intro = '\n'.join(lines[:i]).strip()
            rest = '\n'.join(lines[i:]).strip()
            return intro, rest
    return text, ""


def _build_report_html(markdown_text: str, period: str) -> str:
    """Convert a markdown report section to a styled, phone-friendly HTML file."""
    export_date = datetime.now().strftime('%Y-%m-%d')

    def inline_md(text):
        text = html.escape(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text, flags=re.DOTALL)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text, flags=re.DOTALL)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text, flags=re.DOTALL)
        text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', text, flags=re.DOTALL)
        return text

    blocks = re.split(r'\n{2,}', markdown_text.strip())
    parts = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        heading_match = re.match(r'^#{1,6} (.+)$', block)
        if heading_match:
            parts.append(f'<h3>{inline_md(heading_match.group(1))}</h3>')
            continue

        lines = block.split('\n')
        if all(re.match(r'^[ \t]*[*\-] ', ln) for ln in lines if ln.strip()):
            items = [re.sub(r'^[ \t]*[*\-] ', '', ln) for ln in lines if ln.strip()]
            lis = ''.join(f'<li>{inline_md(item)}</li>' for item in items)
            parts.append(f'<ul>{lis}</ul>')
            continue

        parts.append(f'<p>{inline_md(block)}</p>')

    body = '\n'.join(parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Story Report — {html.escape(period)}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      max-width: 680px;
      margin: 0 auto;
      padding: 24px 20px 60px;
      background: #fafaf8;
      color: #1a1a1a;
    }}
    header {{
      border-bottom: 2px solid #e8e4de;
      padding-bottom: 20px;
      margin-bottom: 36px;
    }}
    header h1 {{
      font-size: 1.8rem;
      font-weight: 700;
      margin: 0 0 6px;
    }}
    header p {{
      color: #888;
      font-size: 0.9rem;
      margin: 0;
    }}
    h3 {{
      font-size: 1rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #888;
      border-bottom: 1px solid #e8e4de;
      padding-bottom: 6px;
      margin: 32px 0 16px;
    }}
    p, li {{
      font-size: 1rem;
      line-height: 1.65;
      color: #2d2d2d;
    }}
    p {{ margin: 0 0 16px; }}
    ul {{
      margin: 0 0 16px;
      padding-left: 20px;
    }}
    li {{ margin-bottom: 8px; }}
    strong {{ font-weight: 600; }}
    em {{ font-style: italic; }}
    footer {{
      margin-top: 48px;
      padding-top: 20px;
      border-top: 1px solid #e8e4de;
      font-style: italic;
      color: #aaa;
      font-size: 0.88rem;
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Story Report</h1>
    <p>{html.escape(period)} &middot; {export_date}</p>
  </header>

  {body}

  <footer>
    &ldquo;When you start looking for story-worthy moments in your life,
    you start to see them everywhere.&rdquo;<br>
    &mdash; Matthew Dicks
  </footer>
</body>
</html>"""


def _md_to_html(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'^-{3,}$', '─────────────', text, flags=re.MULTILINE)
    text = re.sub(r'^#{1,6} (.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'^[ \t]*[*\-] (.+)$', r'• \1', text, flags=re.MULTILINE)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text, flags=re.DOTALL)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<i>\1</i>', text, flags=re.DOTALL)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def _split_text(text: str, max_length: int) -> list:
    chunks = []
    while len(text) > max_length:
        split_at = text.rfind('\n', 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    chunks.append(text)
    return chunks
