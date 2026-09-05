<div align="center">
  <!-- Logo Placeholder -->
  <img src="https://via.placeholder.com/150x150/4B0082/FFFFFF?text=SMA+Logo" alt="Smart Meeting Assistant Logo" width="150" height="150">
  
  # Smart Meeting Assistant

  ***“Turn every conversation into clear, actionable intelligence.”***

</div>

<br/>

## 🎨 Identity & Palette
To ensure a professional and trust-inspiring user experience, the Smart Meeting Assistant utilizes the following brand palette:
- **Deep Indigo (`#4B0082`)**: Represents deep intelligence, technology, and focus.
- **Trust Blue (`#0056B3`)**: Projects security, reliability, and enterprise-grade safety.
- **Crisp White (`#FFFFFF`)**: Offers clean contrast for distraction-free reading.

> [!NOTE]
> **Demo Environment Indicator**: When the system is configured for demonstrations (`DEMO_MODE=True`), the UI will prominently display a banner:  
> **`Demo environment — fictional data`**  
> This guarantees that stakeholders know they are interacting with synthetic records, keeping production boundaries clear.

---

## 🏢 Business Context

### The Business Problem
Modern enterprises lose countless hours deciphering meeting recordings, tracking down decisions, and following up on scattered action items. Manual note-taking is inconsistent and heavily subject to bias, leading to misaligned teams, dropped priorities, and unchecked risks. 

### Target Users
- **Product Managers**: To instantly extract requirements and feature decisions from stakeholder syncs.
- **Engineering Leads**: To capture technical risks, assign architectural action items, and unblock developers.
- **Executives & Directors**: To quickly digest the high-level outcomes of multiple meetings without listening to hours of audio.

### Main Value Proposition
**Smart Meeting Assistant** securely ingests, transcribes, and analyzes enterprise conversations to automatically generate immutable, evidence-backed intelligence. By pairing state-of-the-art NLP models with an enterprise-grade version control and collaboration system, it guarantees that every extracted decision, action item, and risk is traceable directly to its timestamped source—without ever compromising data security or organizational privacy.

---

## 🛠️ Key Capabilities

- **Secure Pipeline**: Fully localized AI processing pipeline (Transcription, Diarization, Sentiment, and Summarization) designed to keep sensitive audio files within the enterprise boundary.
- **Evidence-Grounded Search**: Vector-embedded semantic search via PostgreSQL `pgvector`, allowing users to ask natural language questions and receive answers tied to exact audio timestamps.
- **Immutable Audit Trails**: A sophisticated `ContentVersion` collaboration engine that allows users to review and edit AI-generated insights while preserving an indestructible history of changes.
- **Enterprise Integrations**: Zero-knowledge API keys and webhook dispatches to seamlessly connect extracted action items to external workflow tools (like Jira or Asana) under strict, scoped permissions.
- **Organizational Analytics**: Macro-level meeting health metrics (e.g., action-item completion rates, decision velocity) to optimize corporate time-management without individual employee surveillance.
