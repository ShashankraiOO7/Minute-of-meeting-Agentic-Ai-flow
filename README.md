
# 🧠 Automated Meeting Minutes Generator with CrewAI + Gemini Pro

This project is an **AI-driven workflow** that listens to a `.wav` audio file of a meeting, transcribes it, summarizes the conversation (including sentiment and action items), and creates a **Gmail draft** with the compiled meeting minutes using **CrewAI** agents and **Gemini 1.5 Pro**.

---

## 🚀 Features

- 🎙️ Transcribe `.wav` meeting audio into clean text.
- ✍️ Auto-generate meeting minutes:
  - ✅ Summary
  - 📌 Action Items
  - 🙂 Sentiment/Tone
- 📧 Create a Gmail **draft** (or send email).
- 🧩 Modular, extensible CrewAI architecture using agents and tools.

---

## 🗂️ Project Structure

```

.
├── main.py                          # Main Flow file (entry point)
├── EarningsCall.wav                # Input audio file
├── crews/
│   ├── meeting\_minutes\_crew\.py     # Crew for summarizing meetings
│   ├── gmailcrew\.py                # Crew for creating Gmail drafts
│   └── tools/
│       ├── gmail\_tool.py           # Gmail draft/send logic as CrewAI tool
│       └── gmail\_utility.py        # Gmail API authentication helpers
├── config/
│   ├── agents.yaml                 # Agent role configs
│   └── tasks.yaml                  # Task assignment configs
├── meeting\_minutes/
│   ├── summary.txt                # Generated summary output
│   ├── action\_items.txt          # Extracted action items
│   └── sentiment.txt             # Sentiment of the meeting
├── .env                            # Environment variables
└── README.md

````

---

## 🧠 Flow Overview

### 1. Transcription

Splits audio into 1-minute chunks and sends each chunk to **Gemini 1.5 Pro** for transcription. The result is stored as a full transcript.

### 2. Meeting Minutes Generation

Handled by the `MeetingMinutesCrew`, which consists of:

- `meeting_minutes_summarizer` → extracts summary, action items, sentiment.
- `meeting_minutes_writer` → formats a polished document.

Output is stored in `meeting_minutes/` directory.

### 3. Gmail Draft Creation

The `GmailCrew` agent uses a Gmail Tool to create and save a draft email with the generated meeting minutes.

---

## 👥 CrewAI Architecture

### 🧑‍🤝‍🧑 MeetingMinutesCrew

| Agent | Role |
|-------|------|
| `meeting_minutes_summarizer` | Extracts insights from transcript and writes to files. |
| `meeting_minutes_writer` | Polishes and compiles readable output. |

Tasks:
- `meeting_minutes_summary_task`
- `meeting_minutes_writing_task`

Process: `sequential`

---

### 📬 GmailCrew

| Agent | Role |
|-------|------|
| `gmail_draft_agent` | Uses GmailTool to create/send the meeting summary email. |

Task:
- `gmail_draft_task`

Process: `sequential`

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
````

Ensure the following packages are included:

* `crewai`
* `google-generativeai`
* `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
* `python-dotenv`
* `pydub`
* `tenacity`

### 2. Environment Configuration

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
GMAIL_SENDER=your_email@gmail.com
GMAIL_RECIPIENT=recipient_email@gmail.com
GMAIL_CREDENTIALS=path/to/credentials.json
AGENTOPS_API_KEY=your_agentops_api_key  # (optional)
```

### 3. Gmail API Setup

* Download `credentials.json` from [Google Cloud Console](https://console.cloud.google.com).
* Place it in the root or configure via `GMAIL_CREDENTIALS`.
* First run will generate `token.json` after authorization.

---

## 🏃 Running the App

Ensure `EarningsCall.wav` exists in the root directory.

```bash
python main.py
```

You’ll see logs for:

* Transcription progress
* Minutes generation
* Gmail draft creation

---

## 🛠️ Customization

* Modify `agents.yaml` and `tasks.yaml` under `config/` to change behavior.
* Adjust `GmailTool` to switch between `draft` and `send`.
* Extend agents with memory, knowledge base, or hierarchical reasoning.

---

## ✅ Outputs

After execution:

```
meeting_minutes/
├── summary.txt
├── action_items.txt
└── sentiment.txt
```

Gmail → Draft created with meeting minutes.

---

## 📌 Future Enhancements

* Real-time meeting streaming + transcription
* RAG-based long-context memory
* Multilingual support
* Calendar event integration

---

## 📄 License

MIT License

---

## 🤖 Built With

* [CrewAI](https://github.com/joaomdmoura/crewAI)
* [Google Gemini API](https://ai.google.dev/)
* [Gmail API](https://developers.google.com/gmail/api)

---

## 👋 Contact

For queries or contributions, reach out via [Issues](https://github.com/your-repo/issues).

```

Let me know if you'd like:
- A `requirements.txt` file
- Shields/badges for GitHub Actions, PyPI, etc.
- A GitHub Actions workflow for deployment or CI/CD
```



---

## 👨‍💻 Contributors

### 🔧 [Shashank Rai](https://github.com/ShashankraiOO7)
**Role**: AI Workflow Architect & Developer  
- M.Tech Student at IIIT Lucknow  
- Designed and implemented the end-to-end AI workflow using **CrewAI** and **Gemini 1.5 Pro**
- Engineered the transcription-to-email pipeline with modular, config-driven agents and tasks
- Developed custom tools for Gmail API integration (OAuth, draft creation)
- Ensured a scalable, extensible architecture for meeting automation

---

Interested in contributing? Feel free to fork the repo, raise issues, or submit a pull request!_


