import json
from typing import Dict, Any, Optional
from ..extensions import db
from ..models.collaboration import ContentVersion
from ..models.enums import TargetEntityType

class CollaborationService:
    """
    Service for wrapping edits to AI-generated content in a reliable audit trail (ContentVersion).
    Avoids direct modifications of the models without tracking versions.
    """
    
    @staticmethod
    def log_edit(meeting_id: int, entity_type: TargetEntityType, entity_id: int, 
                 user_id: int, previous_state: Dict[str, Any], new_state: Dict[str, Any], 
                 reason: str = "") -> ContentVersion:
        """
        Records an edit into the ContentVersion audit table.
        """
        version = ContentVersion(
            meeting_id=meeting_id,
            target_entity_type=entity_type,
            target_entity_id=entity_id,
            edited_by_user_id=user_id,
            previous_content=previous_state,
            new_content=new_state,
            edit_reason=reason
        )
        
        db.session.add(version)
        db.session.commit()
        return version

    @staticmethod
    def get_version_history(entity_type: TargetEntityType, entity_id: int) -> list:
        """
        Fetches the complete audit history for a specific entity.
        """
        return ContentVersion.query.filter_by(
            target_entity_type=entity_type,
            target_entity_id=entity_id
        ).order_by(ContentVersion.created_at.desc()).all()

    @staticmethod
    def restore_version(version_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Reverts an entity to the `previous_content` state of a specific version record.
        This function returns the JSON payload to be re-applied to the target model.
        """
        version = ContentVersion.query.get(version_id)
        if not version:
            return None
            
        # Log the restoration as a new edit
        restoration_log = ContentVersion(
            meeting_id=version.meeting_id,
            target_entity_type=version.target_entity_type,
            target_entity_id=version.target_entity_id,
            edited_by_user_id=user_id,
            previous_content=version.new_content, # The current state (before restore)
            new_content=version.previous_content, # The state being restored
            edit_reason=f"Restored from version {version_id}"
        )
        
        db.session.add(restoration_log)
        db.session.commit()
        
        return version.previous_content
