from typing import Dict, Optional, Any
from datetime import datetime
from app.utils.logger import logger
import json


class SessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.intent_data: Dict[str, Any] = {}
        self.planning_results: Dict[str, Any] = {}
        self.selection_options: Dict[str, Any] = {}
        self.awaiting_selection: bool = False
        self.approval_form: Optional[Dict[str, Any]] = None
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "intent_data": self.intent_data,
            "planning_results": self.planning_results,
            "selection_options": self.selection_options,
            "awaiting_selection": self.awaiting_selection,
            "approval_form": self.approval_form,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self._sessions.get(session_id)

    def create_session(self, session_id: str) -> SessionState:
        if session_id in self._sessions:
            return self._sessions[session_id]
        session = SessionState(session_id)
        self._sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session

    def update_session(self, session_id: str, **kwargs) -> Optional[SessionState]:
        session = self._sessions.get(session_id)
        if session:
            session.update(**kwargs)
            logger.info(f"Updated session {session_id}: {list(kwargs.keys())}")
        return session

    def clear_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        return False

    def has_active_selection(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        return session.awaiting_selection if session else False

    def get_planning_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self._sessions.get(session_id)
        return session.planning_results if session else None

    def get_selection_options(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self._sessions.get(session_id)
        return session.selection_options if session else None

    def parse_user_selection(self, user_message: str, selection_options: Dict[str, Any]) -> Dict[str, Any]:
        user_message_lower = user_message.lower()
        
        transport_options = selection_options.get("transport", [])
        hotel_options = selection_options.get("hotel", [])
        dining_options = selection_options.get("dining", [])

        selected = {
            "transport": None,
            "hotel": None,
            "dining": None
        }

        transport_map = {str(i+1): opt for i, opt in enumerate(transport_options)}
        hotel_map = {str(i+1): opt for i, opt in enumerate(hotel_options)}
        dining_map = {str(i+1): opt for i, opt in enumerate(dining_options)}

        for key, opt in transport_map.items():
            if key in user_message or str(opt.get("index")) in user_message:
                selected["transport"] = opt
                break

        for key, opt in hotel_map.items():
            if key in user_message or str(opt.get("index")) in user_message:
                selected["hotel"] = opt
                break

        for key, opt in dining_map.items():
            if key in user_message or str(opt.get("index")) in user_message:
                selected["dining"] = opt
                break

        if "都" in user_message or "全部" in user_message or "所有" in user_message:
            if transport_options:
                selected["transport"] = transport_options[0]
            if hotel_options:
                selected["hotel"] = hotel_options[0]
            if dining_options:
                selected["dining"] = dining_options[0]

        logger.info(f"Parsed user selection: {selected}")
        return selected


session_manager = SessionManager()
