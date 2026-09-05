from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCalendarProvider(ABC):
    """
    Abstract base class for Calendar integrations.
    """
    
    @abstractmethod
    def import_scheduled_meetings(self, user_id: int, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        Fetch scheduled meetings for a user within a timeframe.
        """
        raise NotImplementedError("This feature is not implemented")
        
    @abstractmethod
    def connect_meeting_to_event(self, meeting_id: int, event_id: str) -> bool:
        """
        Link an application Meeting to a Calendar event.
        """
        raise NotImplementedError("This feature is not implemented")
