from .asyncio_tools import async_to_sync
from .extension_id import get_ext_and_mime
from .tasks import getWhatonImage_celery
from .gemini import gemini_upload_and_chat
from .openai_tools import get_openai_embeddings, call_openai_api
from .config import QDRANT_CLIENT_HOST, SUMMARY_PROMPT, json_schema, GEMINI_PROMPT, build_conversation, SYSTEM_PROMPT, build_chat_conversation, update_chat_conversation, HR_PROMPT
from .text import split_sentences, generate_embeddings, cosine_distance, average_embeddings, merge_fragments, escape_markdown_v2
from .mylogger import logger
from .admin_helper import notify_admin_new_entry, create_conversation_file