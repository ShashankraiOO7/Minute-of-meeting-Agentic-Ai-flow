from __future__ import annotations

# ───── 1️⃣  AgentOps must be initialised *before* any LLM libraries ────────────
import agentops
# agentops.init()  # picks up AGENTOPS_API_KEY from env
# agentops.start_session("Meeting‑Minutes Run")

# ───── 2️⃣  Standard library & util imports ─────────────────────────────────────
import asyncio
import os
import warnings
from pathlib import Path
from typing import List
import pickle
#   ▸ Silence irrelevant warnings from PyDub
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydub")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub.utils")

# ───── 3️⃣  Third‑party libraries ───────────────────────────────────────────────
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel
from pydub import AudioSegment
from pydub.utils import make_chunks
from crewai.flow.flow import Flow, listen, start

#   Importing 
# own crews
from crews.meeting_minutes_crew.meeting_minutes_crew import MeetingMinutesCrew
from crews.gmailcrew.gmailcrew import GmailCrew

# ───── Configure Gemini (Gemini 1.5 Pro) ──────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY env var is missing.")

genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-pro")
# -----------------------------------------------------------------------------
# Data state for the flow
# -----------------------------------------------------------------------------
class MeetingMinutesState(BaseModel):
    transcript: str = ""
    meeting_minutes: str = ""

# -----------------------------------------------------------------------------
# Flow definition
# -----------------------------------------------------------------------------
class MeetingMinutesFlow(Flow[MeetingMinutesState]):

    # 1️⃣  TRANSCRIBE AUDIO -----------------------------------------------------
    @start()
    def transcribe_meeting(self):
        print("\n▶ 1/3  Generating transcription (Gemini 1.5 Pro)…")

        script_dir = Path(__file__).parent
        audio_path = script_dir / "EarningsCall.wav"
        if not audio_path.exists():
            raise FileNotFoundError(f"{audio_path} not found")

        audio = AudioSegment.from_file(audio_path, format="wav")
        chunk_length_ms = 60_000  # 1‑minute chunks
        chunks: List[AudioSegment] = make_chunks(audio, chunk_length_ms)

        transcriptions: List[str] = []
        for i, chunk in enumerate(chunks, start=1):
            print(f"   • Transcribing chunk {i}/{len(chunks)}")
            chunk_path = script_dir / f"chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")

            with chunk_path.open("rb") as f:
                audio_bytes = f.read()

            messages = [
                {
                    "role": "user",
                    "parts": [
                        {"text": "Transcribe the following audio to text:"},
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": audio_bytes,
                            }
                        },
                    ],
                }
            ]
            try:
                response = GEMINI_MODEL.generate_content(messages)
                transcriptions.append(response.text.strip())
            except Exception as exc:
                print(f"Gemini error on chunk {i}: {exc}")
            # finally:
            #     chunk_path.unlink(missing_ok=True)

        self.state.transcript = " ".join(transcriptions)
        print("▶  Finished transcription.")

    # 2️⃣  GENERATE MINUTES -----------------------------------------------------
    @listen(transcribe_meeting)
    def generate_meeting_minutes(self):
        print("\n▶ 2/3  Generating meeting minutes with MeetingMinutesCrew…")

        crew = MeetingMinutesCrew()
        output = crew.crew().kickoff({"transcript": self.state.transcript})
        # CrewAI returns a CrewOutput – take .result if present, else str()
        self.state.meeting_minutes = getattr(output, "result", str(output))

    # 3️⃣  CREATE GMAIL DRAFT ---------------------------------------------------
    @listen(generate_meeting_minutes)
    def create_draft_meeting_minutes(self):
        print("\n▶ 3/3  Creating Gmail draft with GmailCrew…")

        crew = GmailCrew()
        output = crew.crew().kickoff({"body": self.state.meeting_minutes})
        draft_id = getattr(output, "result", str(output))
        print(f"✓ Draft created – id: {draft_id}\n")

# -----------------------------------------------------------------------------
# Launcher convenience wrapper
# -----------------------------------------------------------------------------

def kickoff():
    session = agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

    meeting_minutes_flow = MeetingMinutesFlow()
    meeting_minutes_flow.plot()
    meeting_minutes_flow.kickoff()
    with open("flow_snapshot.pkl", "wb") as f:
        pickle.dump(meeting_minutes_flow, f)

    session.end_session()


if __name__ == "__main__":
    print("ABC")
    kickoff()



