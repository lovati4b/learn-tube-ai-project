from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
# The library also has other errors we might want to catch like YouTubeRequestFailed for 429s
from youtube_transcript_api._errors import YouTubeRequestFailed 
import xml.etree.ElementTree # For the new error

def extract_video_id_from_url(youtube_url):
    """
    Extracts the YouTube video ID from a URL.
    Handles standard, short, and embed URLs.
    Returns None if no ID can be found.
    """
    import re
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(video_id_or_url: str):
    """
    Fetches the transcript for a given YouTube video ID or URL.
    Returns the transcript text as a single string or (None, error_message) if not found/error.
    """
    video_id = extract_video_id_from_url(video_id_or_url)
    if not video_id:
        if len(video_id_or_url) == 11 and not video_id_or_url.startswith("http"): # Basic ID check
            video_id = video_id_or_url
        else:
            error_msg = f"Could not extract a valid YouTube video ID from: {video_id_or_url}"
            print(error_msg)
            return None, error_msg

    try:
        print(f"Fetching transcript list for video ID: {video_id}")
        transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript_obj = None

        target_languages = ['en', 'en-US', 'en-GB']
        for lang_code in target_languages:
            try:
                transcript_obj = transcript_list_obj.find_transcript([lang_code])
                print(f"Found transcript object in '{lang_code}' for {video_id}")
                break
            except NoTranscriptFound:
                continue
        
        if not transcript_obj:
            print(f"No English transcript found for {video_id}. Trying any available generated transcript.")
            for tr_info in transcript_list_obj:
                if tr_info.is_generated: 
                    transcript_obj = tr_info
                    print(f"Found generated transcript: {transcript_obj.language} (code: {transcript_obj.language_code}) for {video_id}")
                    break
            if not transcript_obj:
                 print(f"No suitable transcript (English or any generated) found for {video_id}.")
                 return None, "No suitable transcript found for this video."
        
        if not transcript_obj:
             print(f"No transcript object obtained for {video_id}.")
             return None, "Could not obtain any transcript object for this video."

        print(f"Fetching actual transcript content for language '{transcript_obj.language}' for {video_id}")
        fetched_data = transcript_obj.fetch() # This is the FetchedTranscript object OR raises error

        # Process the fetched_data which we expect to be a FetchedTranscript object
        if hasattr(fetched_data, 'snippets') and isinstance(fetched_data.snippets, list):
            full_transcript_text = " ".join([snippet.text for snippet in fetched_data.snippets])
            print(f"Successfully fetched and combined transcript for {video_id} (length: {len(full_transcript_text)} chars).")
            return full_transcript_text, None
        else:
            error_msg = f"Fetched transcript data for {video_id} is not in the expected 'FetchedTranscript' object format with a 'snippets' list."
            print(error_msg)
            print(f"Actual data type: {type(fetched_data)}, Content: {str(fetched_data)[:500]}...") # Print part of content
            return None, error_msg

    except xml.etree.ElementTree.ParseError as e: # Catch the XML parsing error specifically
        error_msg = f"XML parsing error for {video_id} (transcript data likely empty or malformed): {str(e)}"
        print(error_msg)
        return None, error_msg
    except TranscriptsDisabled:
        error_msg = f"Transcripts are disabled for {video_id}"
        print(error_msg)
        return None, error_msg
    except NoTranscriptFound:
        error_msg = f"No transcripts found for {video_id}."
        print(error_msg)
        return None, error_msg
    except VideoUnavailable:
        error_msg = f"Video {video_id} is unavailable."
        print(error_msg)
        return None, error_msg
    except YouTubeRequestFailed as e: # Catch 429s or other direct request failures
        error_msg = f"YouTube request failed for {video_id} (e.g., rate limit, network issue): {str(e)}"
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred for {video_id}: {str(e)}"
        print(error_msg)
        import traceback
        print("Full Traceback:")
        traceback.print_exc()
        return None, error_msg

# --- Example Usage (for testing this file directly) ---
if __name__ == '__main__':
    import time

    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Problematic one
        "https://www.youtube.com/watch?v=3JZ_D3ELwOQ", # Worked
        "https://www.youtube.com/watch?v=WHhZQ3K24HM", 
        "https://youtu.be/xvFZjo5PgG0",                 
        "https://www.youtube.com/shorts/J9y6S-x-fXk",   
        "https://www.youtube.com/watch?v=INVALID_ID_HERE", 
        "not_a_youtube_url"                             
    ]

    for url in test_urls:
        print(f"\n--- Testing URL: {url} ---")
        transcript_text, error = get_youtube_transcript(url)
        
        if error:
            print(f"Failed to get transcript: {error}")
        elif transcript_text is not None :
            print(f"Transcript (first 200 chars): {transcript_text[:200]}...")
        else:
            print("Failed to get transcript (unknown reason: transcript is None, no error msg).")
        
        print("Waiting for 3 seconds before next request...")
        time.sleep(3)