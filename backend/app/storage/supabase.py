from supabase import create_client, Client
from app.config import settings
from app.utils.logger import logger

_supabase_client: Client = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        logger.info("Supabase client initialized")
    return _supabase_client


def get_supabase_anon() -> Client:
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )
