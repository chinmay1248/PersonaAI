# PersonaAI: Current Implementation Overview and Future Work

## 1. Project Purpose

PersonaAI is an AI-assisted reply system designed to help a user generate replies, summaries, and tone-aware responses for WhatsApp Web and Telegram Web. The current product direction is browser-extension first, backed by a FastAPI service that handles authentication, context processing, tone learning, summarization, and AI reply generation.

This document covers:

- what has been built so far
- how the current system works
- the technologies used
- where each technology is used
- the current folder structure
- future work required to make the system feel genuinely human

## 2. Current Product State

At the moment, the working product consists of three main parts:

1. A Chrome/Edge browser extension
2. A Python FastAPI backend
3. A legacy Expo/React Native mobile app kept in the repository for reference

The browser extension is the active client. It runs on WhatsApp Web and Telegram Web, reads visible chat content from the page, lets the user select a target message, sends the extracted context to the backend, and receives reply suggestions or summaries in return.

The backend is the main intelligence layer. It manages users, stores configuration and learning data, builds prompts, talks to the language model, and returns structured results to the extension.

## 3. What Has Been Built So Far

### 3.1 Browser Extension

The extension currently provides:

- floating in-page PersonaAI assistant UI on WhatsApp Web and Telegram Web
- extraction of visible chat messages from the DOM
- chat title detection
- support for selected-message reply generation
- fallback mode where replies use the latest incoming messages if no message is selected
- chat summarization
- reply insertion into the active message composer
- training from visible outgoing messages
- popup-based login, settings, and active-chat actions

The extension now follows a backend-driven architecture. It does not rely on a direct Gemini API flow anymore. It sends all reply, summary, and training requests through the backend.

### 3.2 Backend

The backend currently provides:

- authentication endpoints
- chat configuration endpoints
- reply generation endpoints
- summarization endpoints
- tone training endpoints
- feedback-related backend structure
- metadata and health endpoints

It also includes:

- prompt construction for reply generation
- mood detection
- tone profile learning from messages
- LLM client integration through an OpenAI-compatible SDK
- support for local or hosted model providers through configuration

The current local working configuration uses a Groq API key through the OpenAI-compatible client path.

### 3.3 Reply Generation Logic

Reply generation currently does the following:

1. Reads up to the last 50 extracted messages from the active chat
2. Uses a selected incoming message if the user has clicked one
3. Otherwise uses the latest incoming message block
4. Builds conversation history for the backend
5. Detects language tendencies such as English, Hindi, or Hinglish
6. Detects the latest message mood
7. Loads the user’s tone profile
8. Builds a prompt using:
   - recent conversation history
   - recent user style examples
   - mood
   - language preference
   - tone hints
   - emoji hints
   - average message length hints
9. Sends the prompt to the configured language model
10. Parses reply candidates and fills missing options with fallback replies when necessary

### 3.4 Prompt Improvements Already Implemented

The current prompt system already includes:

- recent conversation transcript
- recent examples of how the user usually texts
- tone hints from learned slang patterns
- language-style guidance
- detected mood
- inferred likely purpose of the latest incoming message
- explicit instructions to avoid generic filler
- explicit instructions to respond specifically to what was shared in the conversation

This prompt is intended to make replies less robotic and more context-aware.

### 3.5 Summarization

The summarization path currently supports:

- backend-generated summaries
- backend parsing fallback if the model returns non-ideal output
- extension-side local fallback summary generation if the backend response is unusable

This was added to make sure the user gets a usable summary even when the model output is imperfect.

### 3.6 Tone Learning

The tone-learning path currently supports:

- training from visible outgoing messages
- extraction of slang patterns
- emoji usage estimation
- average message length
- formality estimation
- language-mix detection
- incremental profile updates

The backend stores a tone profile and uses it to guide future replies.

### 3.7 Testing

The backend currently includes automated tests covering:

- reply generation flow
- reply edge cases
- summarizer behavior
- OpenAI-compatible client helper behavior
- API metadata endpoints
- prompt builder behavior

The extension currently has syntax-verified JavaScript and manual interaction testing support, but not a full browser automation suite in the repository yet.

## 4. Current Tech Stack

## 4.1 Browser Extension Stack

- Chrome/Edge Extension Manifest V3
- JavaScript
- HTML
- CSS
- Chrome extension APIs:
  - `chrome.runtime`
  - `chrome.tabs`
  - `chrome.storage`
  - `chrome.permissions`

### Where It Is Used

- `personaai-extension/manifest.json`
  Defines permissions, content scripts, popup, and background service worker
- `personaai-extension/background/background.js`
  Handles extension message routing, backend API calls, auth token usage, chat config creation, summary flow, reply generation flow, and training flow
- `personaai-extension/content/content.js`
  Handles DOM extraction, in-page widget UI, selected-message logic, and text insertion into the chat composer
- `personaai-extension/content/content.css`
  Styles the in-page assistant and selected-message highlighting
- `personaai-extension/popup/popup.html`
  Defines the popup UI
- `personaai-extension/popup/popup.js`
  Handles popup login, settings, health checks, and active chat actions
- `personaai-extension/popup/popup.css`
  Styles the popup UI

## 4.2 Backend Stack

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- Pydantic / pydantic-settings
- PyJWT
- Passlib / bcrypt
- Cryptography
- OpenAI Python SDK
- Pinecone client
- Redis
- Celery
- Pytest

### Where It Is Used

- `personaai-backend/app/main.py`
  FastAPI application setup, router registration, CORS, health endpoint, metadata endpoint, demo-user seeding
- `personaai-backend/app/config.py`
  Environment-driven application and model configuration
- `personaai-backend/app/database.py`
  SQLAlchemy base, engine, and session setup
- `personaai-backend/app/models/`
  Database models for users, conversations, reply suggestions, tone profiles, training samples, feedback, and chat configuration
- `personaai-backend/app/routers/`
  API endpoints for auth, chat config, AI replies, summaries, feedback, and tone operations
- `personaai-backend/app/schemas/`
  Request/response contracts for API communication
- `personaai-backend/app/services/`
  Core business logic including AI generation, summarization, tone learning, auth, encryption, mood detection, and OpenAI-compatible model access
- `personaai-backend/app/utils/prompt_builder.py`
  Builds the current reply-generation prompt
- `personaai-backend/app/middleware/`
  Authentication and rate-limiting middleware
- `personaai-backend/app/workers/`
  Background-job structure for training and updates
- `personaai-backend/tests/`
  Automated backend tests

## 4.3 Legacy Mobile App Stack

- Expo
- React Native
- React 19
- Expo Router
- Zustand
- Axios
- Android native bridge code in Kotlin

### Where It Is Used

- `personaai-app/app/`
  Expo Router screens
- `personaai-app/components/`
  UI components
- `personaai-app/services/`
  API and integration helpers
- `personaai-app/store/`
  Client-side state
- `personaai-app/android/`
  Older Android-native integration and accessibility-related code

This mobile app remains in the repository as legacy/reference material and is not the current primary interface.

## 5. Current Folder Setup

```text
PersonaAI/
|-- assets/                          Branding and documentation images
|-- artifacts/                       Generated build outputs
|-- docs/                            Project documentation
|   |-- archive/                     Older archived notes
|   |-- guides/                      Setup and deployment guides
|   |-- reports/                     Reviews, status notes, and testing reports
|   `-- IMPLEMENTATION_OVERVIEW.md   This document
|-- personaai-app/                   Legacy Expo/React Native mobile app
|   |-- app/                         Screens and route structure
|   |-- components/                  Reusable UI components
|   |-- services/                    App-side service layer
|   |-- store/                       Zustand state stores
|   `-- android/                     Native Android layer
|-- personaai-backend/               Active backend service
|   |-- app/
|   |   |-- middleware/              Auth and rate limiting
|   |   |-- models/                  Database models
|   |   |-- routers/                 API routes
|   |   |-- schemas/                 API schemas
|   |   |-- services/                Business logic and AI orchestration
|   |   |-- utils/                   Prompt-building helpers
|   |   `-- workers/                 Background worker structure
|   |-- alembic/                     Database migration setup
|   `-- tests/                       Backend test suite
|-- personaai-extension/             Active browser extension
|   |-- background/                  Background service worker
|   |-- content/                     In-page extraction and assistant UI
|   |-- icons/                       Extension icons
|   |-- popup/                       Popup UI and logic
|   `-- manifest.json                Extension manifest
|-- scripts/                         Build and deployment scripts
`-- README.md                        Root repository overview
```

## 6. Current Request Flow

The current reply request flow is:

1. User opens WhatsApp Web or Telegram Web
2. Extension content script loads on the supported host
3. User clicks `Replies`, `Summary`, or `Train`
4. Content script extracts the active chat context
5. If a message bubble is selected, that selected incoming message becomes the reply target
6. The extension background worker sends the request to the backend
7. The backend:
   - validates the user
   - ensures a chat configuration exists
   - builds recent conversation history
   - detects mood
   - loads the user’s tone profile
   - builds the prompt
   - calls the configured language model
   - parses results
   - falls back if required
8. The extension receives the reply or summary result
9. The user can insert a selected reply into the active composer

## 7. Current Data and Learning State

What the system currently uses:

- visible recent messages from the open chat
- selected target message if chosen by the user
- current chat label and platform
- saved user authentication state in extension local storage
- backend chat configurations
- tone profile data
- stored training samples
- saved conversations and reply suggestions in the backend database

What the system does not yet do in a complete way:

- persistent per-chat memory retrieval for long histories
- long-term relationship memory
- robust per-contact personalization
- ranking based on actual user reply choices

## 8. Current Limitations

The current system is functional, but it still has important limits:

- it depends on visible or currently loaded DOM messages, not full app-native history
- it does not yet have a dedicated long-term memory layer
- it does not yet store and retrieve enough past real conversations to behave like one consistent human over time
- personalization is present but still shallow compared to real human behavior
- feedback learning is not yet fully integrated into reply ranking
- browser-side automated testing is not yet built into the project

## 9. Future Work

The long-term goal should not be only “generate an AI reply.”

The goal should be:

**AI should behave like a consistent person in an ongoing relationship.**

To make the system feel genuinely human, the following areas need to be built next.

### 9.1 Context Memory

Human conversations feel human because people remember:

- what is currently being discussed
- the recent flow of messages
- earlier plans
- how they talk to a particular person
- inside jokes and recurring references

The system therefore needs:

- short-term memory for recent messages
- medium-term memory for current-topic summaries
- long-term memory for relationship facts, habits, names, and style

### 9.2 Personal Tone Modeling

To sound human, the system must understand:

- whether the user writes short or long replies
- whether the user uses emojis often
- whether the user is teasing, dry, formal, playful, romantic, or blunt
- when the user uses English, Hindi, or Hinglish

This should come from real outgoing messages, not only from prompt wording.

### 9.3 Intent Understanding

The model should not respond only to literal text. It should first understand what the other person is trying to do, such as:

- seeking attention
- asking for an opinion
- teasing
- planning
- seeking validation
- showing something
- sharing a problem

If the system does not understand intent, replies will still feel robotic even when the language is fluent.

### 9.4 Response Diversity with Personality Consistency

Human replies vary, but still feel like the same person. The system should support:

- teasing replies
- direct replies
- short reactions
- follow-up questions
- flirty replies
- sarcastic replies

The requirement is not only variety. It is **variety without losing personality consistency**.

### 9.5 Feedback Learning

The system should learn from:

- which reply the user chose
- which reply the user edited
- which reply the user ignored
- which reply the user sent immediately

This data is essential for learning what the user actually sounds like in practice.

### 9.6 Target Architecture for Human-Like Behavior

The desired architecture should evolve into these layers:

**Layer 1: Raw message storage**

- incoming messages
- outgoing messages
- timestamps
- chat ID
- sender
- selected target message

**Layer 2: Conversation understanding**

- recent thread summary
- current topic
- intent detection
- sentiment or mood
- relationship mode

**Layer 3: Persona modeling**

- writing style
- common openers
- common closers
- slang
- emoji habits
- average message length
- response timing patterns
- language-switching patterns

**Layer 4: Memory retrieval**

Before generation, the system should retrieve:

- similar old conversations
- chat-specific style
- old user replies
- related memory facts

**Layer 5: Generation**

The final generation prompt should include:

- latest message
- recent thread
- user style examples
- chat-specific persona
- relevant memory
- current intent

**Layer 6: Ranking**

The system should generate multiple replies and then rank them based on:

- match with user style
- context fit
- naturalness
- specificity
- likelihood that the user would actually send them

### 9.7 Minimum Features Required for Strong Human-Like Quality

The minimum must-have set is:

- per-chat memory
- stored outgoing messages
- user style examples in the prompt
- intent detection before generation
- retrieval of similar past replies
- ranking of generated options
- a feedback loop

### 9.8 What Makes AI Sound Robotic

The system will continue to sound robotic if it depends on:

- generic prompts
- only the latest message
- no memory
- no user examples
- no per-contact behavior
- replies that are too polite or too safe
- one response style for all situations

### 9.9 What Makes AI Sound Human

The system starts to feel human when it gives:

- specific reactions
- continuity with the prior conversation
- the feeling of the same person returning in each reply
- imperfect but natural language
- strong reflection of the user’s actual style
- appropriate emotional shifts based on context

## 10. Summary

What has been built so far is a working browser-extension and backend system for:

- extracting visible chat context
- selecting a specific incoming message
- generating AI replies
- summarizing visible chats
- learning user tone from outgoing messages
- using an LLM through a backend-controlled architecture

What still needs to be built for truly human-like behavior is not just “better AI text.” It is a complete memory, persona, retrieval, intent, and feedback system that allows the assistant to behave like one consistent person across ongoing conversations.
