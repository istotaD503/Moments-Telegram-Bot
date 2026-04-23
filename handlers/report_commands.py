"""
Report command handler — generates an AI-powered summary of the user's stories.
"""
import html
import logging
import re
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

    report_text = _md_to_html(response.output_text)
    header = "🧠 <b>Your Story Report</b>\n\n"
    full_message = header + report_text

    if len(full_message) <= TELEGRAM_MAX_LENGTH:
        await thinking_msg.edit_text(full_message, parse_mode='HTML')
    else:
        await thinking_msg.delete()
        chunks = _split_text(report_text, TELEGRAM_MAX_LENGTH - len(header))
        await reply_to.reply_text(header + chunks[0], parse_mode='HTML')
        for chunk in chunks[1:]:
            await reply_to.reply_text(chunk, parse_mode='HTML')


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
