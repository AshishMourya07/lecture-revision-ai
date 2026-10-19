import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url_or_id: str) -> str:
    """Extracts the 11-character YouTube video ID from any standard YouTube URL."""
    url_or_id = url_or_id.strip()
    if len(url_or_id) == 11 and " " not in url_or_id:
        return url_or_id

    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:embed\/)([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL. Please paste a valid YouTube video link.")

def fetch_timestamped_transcript(video_id: str) -> str:
    """Fetches English transcript (manual or auto-generated) with MM:SS and seconds."""
    ytt_api = YouTubeTranscriptApi()
    try:
        # Compatible with latest youtube-transcript-api versions
        fetched = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-IN', 'hi'])
        raw_entries = fetched.to_raw_data()
    except AttributeError:
        # Fallback for older versions of youtube-transcript-api
        raw_entries = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-IN', 'hi'])

    lines = []
    for item in raw_entries:
        start_sec = int(item["start"])
        mins, secs = divmod(start_sec, 60)
        text = item["text"].replace("\n", " ").strip()
        lines.append(f"[{mins:02d}:{secs:02d} ({start_sec}s)] {text}")

    return "\n".join(lines)