# learn_tube_ai/app/services/video_processing_service.py
from .llm_service import generate_analysis_from_text
from youtube_transcript_api import (
    YouTubeTranscriptApi, 
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable 
    # Removed TooManyRequests, NotTranslatable, etc.
)
import os 

def get_youtube_transcript(video_id: str) -> dict:
    """
    Fetches the transcript for a given YouTube video ID.
    Returns a dictionary with:
        'text': The full transcript as a single string.
        'segments': A list of segment dictionaries (e.g., {'text': str, 'start': float, 'duration': float}).
        'error': An error message string if fetching fails, otherwise None.
    """
    try:
        print(f"SERVICE: Attempting to list transcripts for video_id: {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        selected_transcript_obj = None
        # Try to find a manually created or generated transcript in preferred languages
        # The library handles the preference order if multiple languages in the list match
        preferred_langs = ['en', 'en-US', 'en-GB']
        try:
            print(f"SERVICE: Trying to find transcript in {preferred_langs} for {video_id}")
            selected_transcript_obj = transcript_list.find_transcript(preferred_langs)
        except NoTranscriptFound:
            print(f"SERVICE: No transcript in preferred languages {preferred_langs} found for {video_id}.")
            # Optionally, you could try fetching ANY transcript and then translating it
            # For now, we consider this an error if primary languages are not found.
            # Example:
            # try:
            #   any_transcript = transcript_list.find_generated_transcript(transcript_list.languages) # find any
            #   if any_transcript.is_translatable:
            #       selected_transcript_obj = any_transcript.translate('en')
            # except (NoTranscriptFound, NotTranslatable, TranslationLanguageNotAvailable):
            #    pass # Stick with original error
            if not selected_transcript_obj:
                 return {"text": None, "segments": None, "error": f"No transcript found in preferred languages: {', '.join(preferred_langs)}."}


        print(f"SERVICE: Fetching transcript data for {video_id} using found transcript object.")
        fetched_segments_data = selected_transcript_obj.fetch() 
        
        if not fetched_segments_data:
            print(f"SERVICE: Fetched transcript data is empty for {video_id}.")
            return {"text": None, "segments": None, "error": "Fetched transcript is empty."}

        transcript_texts_list = []
        processed_segments_list = []

        for i, seg_data in enumerate(fetched_segments_data):
            # ... (segment processing logic as in the previous version - assuming it's correct for FetchedTranscriptSnippet) ...
            try:
                if hasattr(seg_data, 'text') and hasattr(seg_data, 'start') and hasattr(seg_data, 'duration'):
                    current_text, start_time, duration_val = seg_data.text, seg_data.start, seg_data.duration
                elif isinstance(seg_data, dict) and all(k in seg_data for k in ['text', 'start', 'duration']):
                    current_text, start_time, duration_val = seg_data['text'], seg_data['start'], seg_data['duration']
                else: raise ValueError("Segment format not recognized") # Force into except block
                
                transcript_texts_list.append(current_text)
                processed_segments_list.append({"text": current_text, "start": start_time, "duration": duration_val})
            except Exception as e_seg:
                print(f"SERVICE: Error processing segment {i} for {video_id}: {e_seg}. Data: {str(seg_data)[:100]}")
                transcript_texts_list.append(f"[Segment Error: {str(e_seg)[:30]}]") # Add placeholder
                processed_segments_list.append({"text": f"[Segment Error]", "start": 0, "duration": 0, "error": str(e_seg)})


        if not transcript_texts_list: # Should not happen if fetched_segments_data was not empty and processing worked
            print(f"SERVICE: No text could be extracted from any segments for {video_id}")
            return {"text": None, "segments": [], "error": "No text content in transcript segments."}

        full_transcript_text = " ".join(transcript_texts_list).replace('\n', ' ')
        full_transcript_text = ' '.join(full_transcript_text.split())

        print(f"SERVICE: Transcript processing complete for {video_id}. Text length: {len(full_transcript_text)}, Segments: {len(processed_segments_list)}")
        return {"text": full_transcript_text, "segments": processed_segments_list, "error": None}

    # Specific exceptions from youtube-transcript-api
    except TranscriptsDisabled:
        print(f"SERVICE: Transcripts are disabled for video {video_id}")
        return {"text": None, "segments": None, "error": "Transcripts are disabled for this video."}
    except NoTranscriptFound: # This is a valid exception from the library
        print(f"SERVICE: No transcript found for video {video_id} (overall).")
        return {"text": None, "segments": None, "error": "No transcript could be found for this video."}
    except VideoUnavailable:
        print(f"SERVICE: Video {video_id} is unavailable.")
        return {"text": None, "segments": None, "error": "This video is unavailable."}
    # NoTranscriptAccessible might also not be available, remove if it causes issues
    # # except NoTranscriptAccessible: 
    # #      print(f"SERVICE: No transcript is accessible for {video_id}.")
    # #      return {"text": None, "segments": None, "error": "No transcript is accessible for this video."}
    except Exception as e: 
        print(f"SERVICE: An unexpected error occurred in youtube-transcript-api processing for {video_id}: {str(e)}")
        if "no element found" in str(e).lower():
            error_detail = "YouTube returned an unexpected page structure (possibly an error or consent page). Transcript not parsable."
            # Check for 429 type errors in the generic exception message
        elif "429" in str(e) or "too many requests" in str(e).lower():
            error_detail = "Too many requests to YouTube. Try again later or use VPN."
        else:
            error_detail = str(e)
    return {"text": None, "segments": None, "error": f"Unexpected error fetching transcript: {error_detail}"}

def process_video_for_llm_analysis(video_id: str, transcript_text: str) -> dict:
    """
    Processes the transcript text using an LLM for analysis.
    Returns a dictionary with 'table_of_contents', 'key_terms', 'logical_flow', and 'summary'.
    Handles missing API key gracefully by returning empty/default analysis.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY") # or whatever your key variable is
    default_analysis = {
        "table_of_contents": [],
        "key_terms": [],
        "logical_flow": "LLM analysis not performed.", # Default message
        "summary": "Summary not available." # Default message
    }

    if not api_key:
        print(f"API_KEY not found for LLM. Skipping LLM analysis for {video_id}.")
        default_analysis["logical_flow"] = "LLM analysis skipped: API key not configured."
        default_analysis["summary"] = "Summary skipped: API key not configured."
        return default_analysis
    
    if not transcript_text or not transcript_text.strip():
        print(f"No transcript text provided to LLM for {video_id}. Skipping LLM analysis.")
        default_analysis["logical_flow"] = "LLM analysis skipped: Transcript is empty or unavailable."
        default_analysis["summary"] = "Summary skipped: Transcript is empty or unavailable."
        return default_analysis

    try:
        print(f"Attempting LLM analysis for {video_id}...")
        # Assuming generate_analysis_from_text will use the API key from environment
        llm_response_data = generate_analysis_from_text(transcript_text) # This should return a dict
        
        # Ensure all keys are present in the response, defaulting to empty/null if not
        analysis_data = {
            "table_of_contents": llm_response_data.get("table_of_contents", []),
            "key_terms": llm_response_data.get("key_terms", []),
            "logical_flow": llm_response_data.get("logical_flow", "No logical flow generated."),
            "summary": llm_response_data.get("summary", "No summary generated.")
        }
        print(f"LLM Analysis for {video_id} successful (or mock successful).")
        return analysis_data
        
    except Exception as e:
        print(f"Error during LLM analysis for {video_id}: {e}")
        # import traceback
        # print(traceback.format_exc()) # For more detailed debugging if LLM call fails
        default_analysis["logical_flow"] = f"LLM analysis failed: {str(e)}"
        default_analysis["summary"] = f"Summary generation failed: {str(e)}"
        return default_analysis