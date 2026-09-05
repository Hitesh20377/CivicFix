from abc import ABC, abstractmethod
from typing import List, Dict, Any
import structlog
from ...models.meetings import Meeting

logger = structlog.get_logger()

class BaseEmailProvider(ABC):
    """
    Abstract base class for Email integrations.
    """
    
    @abstractmethod
    def send_processing_update(self, user_id: int, meeting_id: int, status: str) -> bool:
        raise NotImplementedError("This feature is not implemented")
        
    @abstractmethod
    def send_unreviewed_notes_reminder(self, user_id: int, meeting_id: int) -> bool:
        raise NotImplementedError("This feature is not implemented")
        
    @abstractmethod
    def send_open_action_item_reminder(self, owner_user_id: int, item_id: int) -> bool:
        raise NotImplementedError("This feature is not implemented")
        
    def share_approved_summary(self, meeting: Meeting, recipients: List[str], summary_data: Dict[str, Any]) -> bool:
        """
        Shared logic enforcing human approval before sending AI-generated summaries.
        """
        if not meeting.summary_approved_at or not meeting.approved_by_user_id:
            logger.warning("Attempted to share unapproved summary", meeting_id=meeting.id)
            return False
            
        return self._execute_share(meeting, recipients, summary_data)
        
    @abstractmethod
    def _execute_share(self, meeting: Meeting, recipients: List[str], summary_data: Dict[str, Any]) -> bool:
        """
        Internal method implemented by subclasses to actually send the email.
        """
        raise NotImplementedError("This feature is not implemented")
