"""
Demo Environment Seeder Script

This script populates the database with fictional, safe demo data.
It creates a mocked representation of Meetings, Speakers, Transcripts,
Topics, Summaries, Decisions, Action Items, Risks, and Analytics.
"""
import sys
import os
import random
from datetime import datetime, timedelta

# Add project root to python path to access app modules
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'backend'))

from backend.run import app
from backend.app.extensions import db
from backend.app.models.meetings import Meeting, ActionItem, ActionItemStatus
from backend.app.models.stubs import User
from backend.app.models.collaboration import MeetingParticipant, ContentVersion
from backend.app.models.enums import ParticipantRole, ParticipationStatus, TargetEntityType
from backend.app.models.analytics import MeetingAnalytics

def seed_demo_data():
    with app.app_context():
        # Ensure we are in a safe mode before wiping or seeding data
        print("Initializing Demo Data Seeder...")
        
        # 1. Create Fictional Users/Speakers
        users = [
            User(email="alice.pm@fictional.demo"),
            User(email="bob.eng@fictional.demo"),
            User(email="charlie.exec@fictional.demo")
        ]
        db.session.add_all(users)
        db.session.commit()
        
        # 2. Create Fictional Meetings
        meetings = [
            Meeting(
                title="Q3 Strategy & Roadmap Sync",
                date=datetime.utcnow() - timedelta(days=2),
                recording_url="s3://demo-bucket/q3-strategy.mp3",
                status="processed",
                is_approved=True
            ),
            Meeting(
                title="Database Migration Kickoff",
                date=datetime.utcnow() - timedelta(days=1),
                recording_url="s3://demo-bucket/db-migration.mp3",
                status="processed",
                is_approved=False
            )
        ]
        db.session.add_all(meetings)
        db.session.commit()
        
        # 3. Create Participants
        participants = [
            MeetingParticipant(meeting_id=meetings[0].id, user_id=users[0].id, display_name="Alice (PM)", role=ParticipantRole.ORGANIZER, participation_status=ParticipationStatus.ACCEPTED),
            MeetingParticipant(meeting_id=meetings[0].id, user_id=users[1].id, display_name="Bob (Engineering)", role=ParticipantRole.PARTICIPANT, participation_status=ParticipationStatus.ACCEPTED),
            MeetingParticipant(meeting_id=meetings[1].id, user_id=users[1].id, display_name="Bob (Engineering)", role=ParticipantRole.ORGANIZER, participation_status=ParticipationStatus.ACCEPTED),
        ]
        db.session.add_all(participants)
        db.session.commit()
        
        # 4. Create Fictional Action Items
        action_items = [
            ActionItem(
                meeting_id=meetings[0].id,
                task_text="Draft Q3 Marketing budget",
                normalized_task_text="draft q3 marketing budget",
                owner_name="Alice (PM)",
                owner_user_id=users[0].id,
                deadline=datetime.utcnow() + timedelta(days=5),
                priority="high",
                status=ActionItemStatus.PENDING,
                confidence_score=0.92
            ),
            ActionItem(
                meeting_id=meetings[1].id,
                task_text="Review Postgres scaling limits",
                normalized_task_text="review postgres scaling limits",
                owner_name="Bob (Engineering)",
                owner_user_id=users[1].id,
                priority="critical",
                status=ActionItemStatus.COMPLETED,
                confidence_score=0.98
            )
        ]
        db.session.add_all(action_items)
        db.session.commit()

        # 5. Create Mock ContentVersions for Decisions & Summaries
        versions = [
            ContentVersion(
                meeting_id=meetings[0].id,
                target_entity_type=TargetEntityType.MEETING_SUMMARY,
                target_entity_id=1,
                edited_by_user_id=users[0].id,
                previous_content={"summary": "We talked about Q3."},
                new_content={"summary": "The team aligned on Q3 goals, prioritizing market expansion and technical debt reduction."},
                edit_reason="Added more professional detail."
            ),
            ContentVersion(
                meeting_id=meetings[1].id,
                target_entity_type=TargetEntityType.DECISION,
                target_entity_id=1,
                edited_by_user_id=users[1].id,
                previous_content={"decision": "Use Postgres."},
                new_content={"decision": "Approved migration to PostgreSQL 15 with pgvector extension for AI search."},
                edit_reason="Clarified technical specification."
            )
        ]
        db.session.add_all(versions)
        
        # 6. Create Analytics Mock
        analytics = MeetingAnalytics(
            meeting_id=meetings[0].id,
            duration_seconds=3600,
            participant_count=2,
            speaker_count=2,
            total_words=4500,
            words_per_minute=75.0,
            topic_count=4,
            decision_count=2,
            action_item_count=1,
            unresolved_question_count=0,
            risk_count=1,
            average_confidence=0.94
        )
        db.session.add(analytics)
        db.session.commit()

        print("✅ Demo data successfully injected!")

if __name__ == "__main__":
    seed_demo_data()
