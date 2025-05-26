# learn_tube_ai/app/routes.py
from flask import Blueprint, request, jsonify, make_response
# Ensure all necessary imports are here
from .services.video_processing_service import get_youtube_transcript, process_video_for_llm_analysis 
from .models import Video
from app import db 
import re
from .services.llm_service import explain_selected_text_mock # <<< ADD THIS

main_bp = Blueprint('api', __name__, url_prefix='/api')

def extract_video_id(url):
    # ... (your existing extract_video_id function) ...
    patterns = [ r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)', r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)', r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)', r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)',]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match: return match.group(1)
    return None

@main_bp.route('/process_video', methods=['POST', 'OPTIONS'])
def process_video_route():
    # ... (your existing process_video_route - the one from my last message that handles
    #          transcript fetch errors by returning video_id and video_url) ...
    if request.method == 'OPTIONS': return _build_cors_preflight_response()
    data = request.get_json()
    if not data or 'video_url' not in data: return jsonify({"error": "Missing video_url"}), 400
    video_url = data['video_url']
    video_id = extract_video_id(video_url) 
    if not video_id: return jsonify({"error": "Invalid YouTube URL", "details": "Could not extract video ID.", "video_url": video_url}), 400
    print(f"API: Received video URL: {video_url} -> Extracted video ID: {video_id}")
    video_obj = Video.query.filter_by(video_id=video_id).first()
    response_data = {}; status_code = 200
    if video_obj and video_obj.transcript_text:
        print(f"API: Found video {video_id} with transcript in database (cache).")
        response_data = { "message": "Video data retrieved from cache.", "video_id": video_obj.video_id, "video_url": video_obj.video_url, "title": video_obj.title or f"Video: {video_id}", "transcript_text": video_obj.transcript_text or "", "segments": video_obj.transcript_segments or [], "analysis": { "table_of_contents": video_obj.table_of_contents or [], "key_terms": video_obj.key_terms or [], "logical_flow": video_obj.logical_flow or "Analysis previously cached.", "summary": video_obj.summary or "Summary previously cached."}}
        status_code = 200
    else:
        if video_obj: print(f"API: Video {video_id} found in DB but missing transcript text. Re-fetching.")
        else: print(f"API: Video {video_id} not in database. Fetching transcript.")
        transcript_fetch_result = get_youtube_transcript(video_id)
        transcript_text = transcript_fetch_result.get("text"); transcript_segments = transcript_fetch_result.get("segments"); transcript_error = transcript_fetch_result.get("error")
        if transcript_error or not transcript_text:
            print(f"API: Failed to fetch transcript for {video_id}. Error: {transcript_error}")
            return jsonify({"error": "Failed to retrieve transcript automatically", "details": transcript_error or "Transcript is unavailable or empty.", "video_id": video_id, "video_url": video_url }), 422
        print(f"API: Transcript for {video_id} fetched. Length: {len(transcript_text)}. Processing for LLM.")
        analysis_results = process_video_for_llm_analysis(video_id, transcript_text)
        try:
            if not video_obj: video_obj = Video(video_id=video_id, video_url=video_url); db.session.add(video_obj)
            video_obj.title = f"Video: {video_id}"; video_obj.transcript_text = transcript_text; video_obj.transcript_segments = transcript_segments; video_obj.table_of_contents = analysis_results.get("table_of_contents"); video_obj.key_terms = analysis_results.get("key_terms"); video_obj.logical_flow = analysis_results.get("logical_flow"); video_obj.summary = analysis_results.get("summary")
            db.session.commit(); print(f"API: Video {video_id} and its data (re-)saved to database.")
            response_data = {"message": "Video processed successfully.", "video_id": video_obj.video_id, "video_url": video_obj.video_url, "title": video_obj.title, "transcript_text": video_obj.transcript_text, "segments": video_obj.transcript_segments, "analysis": analysis_results }; status_code = 200 # Changed from 201 for simplicity, or check if new_video was added
        except Exception as e: db.session.rollback(); print(f"API: Database error for {video_id}: {str(e)}"); return jsonify({"error": "Database error after processing video.", "details": str(e)}), 500
    return jsonify(response_data), status_code

# --- MODIFIED ENDPOINT FOR CUSTOM TRANSCRIPT WITH ENHANCED TIMESTAMP PARSING ---
@main_bp.route('/process_video_with_custom_transcript', methods=['POST', 'OPTIONS'])
def process_video_with_custom_transcript_route():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    data = request.get_json()
    if not data or not all(k in data for k in ['video_id', 'video_url', 'custom_transcript_text']):
        return jsonify({"error": "Missing required fields: video_id, video_url, or custom_transcript_text"}), 400

    video_id = data['video_id']
    video_url = data['video_url'] 
    custom_transcript_text = data['custom_transcript_text']
    custom_title = data.get('title') 

    print(f"API: Received custom transcript for video_id: {video_id}. Text length: {len(custom_transcript_text)}")

    parsed_segments = []
    lines = custom_transcript_text.splitlines()
    
    # Regex to capture timestamps like [00:00], 00:00, 0:00:00, [0:00:00.123] etc. at the START of a line.
    # It captures hours (optional, group 2), minutes (group 3), seconds (group 4), and optionally milliseconds (group 5).
    # Group 6 captures the text after the timestamp.
    # Adjusted to be more robust for common YouTube transcript formats.
    timestamp_pattern = re.compile(
        r"^\s*(?:\[)?((?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?:[\.,](\d{1,3}))?)(?:\])?\s*(.*)"
    )
    # Groups: 1:FullTime, 2:Hours(opt), 3:Minutes, 4:Seconds, 5:Millis(opt), 6:Text

    current_segment_text_parts = []
    last_segment_start_time = 0.0 # For text before the first timestamp

    for line_number, line_text in enumerate(lines):
        original_line = line_text # Keep original for non-timestamp lines
        line_text = line_text.strip() # Work with stripped line for matching

        match = timestamp_pattern.match(line_text)
        
        if match:
            # A new timestamp is found. Finalize the previous segment if it had text.
            if current_segment_text_parts:
                segment_text_to_add = " ".join(current_segment_text_parts).strip()
                if segment_text_to_add: # Only add if there's actual text
                    parsed_segments.append({
                        "text": segment_text_to_add,
                        "start": last_segment_start_time, # Start time of this collected text
                        "duration": 0.0 # Placeholder, calculated later
                    })
                current_segment_text_parts = [] # Reset for the new segment

            # Extract time components for the NEW current segment
            full_time_str, hr_str, min_str, sec_str, ms_str, text_after_timestamp = match.groups()
            
            hours = int(hr_str) if hr_str else 0
            minutes = int(min_str) # Minutes should always be present if matched
            seconds = int(sec_str)
            milliseconds = int(ms_str.ljust(3, '0')) if ms_str else 0

            current_start_time_seconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000.0)
            last_segment_start_time = current_start_time_seconds # Update for the next block of text

            # Add the text part from the timestamped line
            if text_after_timestamp.strip():
                current_segment_text_parts.append(text_after_timestamp.strip())
            
            # If it's the very last line and it's a timestamped line, ensure it gets added
            if line_number == len(lines) - 1 and current_segment_text_parts:
                segment_text_to_add = " ".join(current_segment_text_parts).strip()
                if segment_text_to_add:
                    parsed_segments.append({
                        "text": segment_text_to_add,
                        "start": last_segment_start_time,
                        "duration": 0.0 
                    })
                current_segment_text_parts = []


        elif line_text: # Not a timestamp line, but has content
            current_segment_text_parts.append(original_line.strip()) # Use original_line to preserve internal spacing before stripping ends

    # After loop, if there's any remaining text in current_segments_buffer, it's part of the last segment
    if current_segment_text_parts:
        segment_text_to_add = " ".join(current_segment_text_parts).strip()
        if segment_text_to_add:
            if not parsed_segments: # Entire text had no timestamps
                 parsed_segments.append({"text": segment_text_to_add, "start": 0.0, "duration": 0.0})
            else: # Append to the last segment that had a timestamp
                 # This assumes the last segment created was the correct one to append to
                 parsed_segments[-1]["text"] += " " + segment_text_to_add 
                 parsed_segments[-1]["text"] = parsed_segments[-1]["text"].strip()


    # Calculate durations (start of next segment - start of current)
    if parsed_segments:
        for i in range(len(parsed_segments)):
            if i + 1 < len(parsed_segments): # If there's a next segment
                duration = parsed_segments[i+1]["start"] - parsed_segments[i]["start"]
                parsed_segments[i]["duration"] = max(0.1, duration) # Min duration 0.1s, ensure not negative
            else: # Last segment
                # Estimate duration based on text length (e.g., 5 words per second, avg word length 5 chars)
                # Or a fixed sensible default if text is very short
                num_chars = len(parsed_segments[i]["text"])
                estimated_duration = max(2.0, num_chars / 15.0) # At least 2 seconds, or ~15 chars/sec
                parsed_segments[i]["duration"] = round(estimated_duration, 1)
        
        # If the very first segment had no timestamp (start 0) and there's a second segment,
        # its duration should be up to the start of the second segment.
        if len(parsed_segments) > 1 and parsed_segments[0]["start"] == 0.0 and parsed_segments[0]["duration"] == 0.0 :
            parsed_segments[0]["duration"] = max(0.1, parsed_segments[1]["start"])


    if not parsed_segments and custom_transcript_text: # Ultimate fallback if all parsing fails
         parsed_segments.append({"text": custom_transcript_text, "start": 0, "duration": 600}) # Whole text as one segment

    print(f"API: Parsed {len(parsed_segments)} segments from custom transcript.")
    # for seg in parsed_segments[:5]: print(seg) # For debugging parsed segments
    
    analysis_results = process_video_for_llm_analysis(video_id, custom_transcript_text) # LLM still gets the full raw text

    try:
        video_obj = Video.query.filter_by(video_id=video_id).first()
        if not video_obj:
            print(f"API: Video {video_id} not found for custom transcript. Creating new entry.")
            video_obj = Video(video_id=video_id, video_url=video_url, title=custom_title or f"Video: {video_id} (custom transcript)")
            db.session.add(video_obj)
        else:
            print(f"API: Updating video {video_id} with custom transcript.")
            if custom_title and (not video_obj.title or "custom transcript" not in video_obj.title): 
                video_obj.title = custom_title # Prefer user's custom title for this text

        video_obj.transcript_text = custom_transcript_text 
        video_obj.transcript_segments = parsed_segments 
        video_obj.table_of_contents = analysis_results.get("table_of_contents")
        # ... (rest of analysis fields update) ...
        video_obj.key_terms = analysis_results.get("key_terms")
        video_obj.logical_flow = analysis_results.get("logical_flow")
        video_obj.summary = analysis_results.get("summary")
        
        db.session.commit()
        print(f"API: Video {video_id} updated/created with custom transcript and analysis.")
        
        response_data = {
            "message": "Custom transcript processed successfully.",
            "video_id": video_obj.video_id,
            "video_url": video_obj.video_url,
            "title": video_obj.title,
            "transcript_text": video_obj.transcript_text,
            "segments": video_obj.transcript_segments, 
            "analysis": analysis_results
        }
        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        print(f"API: Database error for {video_id} with custom transcript: {str(e)}")
        # import traceback; traceback.print_exc(); # For more detailed error
        return jsonify({"error": "Database error processing custom transcript.", "details": str(e)}), 500

@main_bp.route('/explain_text', methods=['POST', 'OPTIONS'])
def explain_text_route():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    data = request.get_json()
    if not data or 'selected_text' not in data:
        return jsonify({"error": "Missing 'selected_text' in request"}), 400

    selected_text = data['selected_text']
    video_id_context = data.get('current_video_id') # Optional: get video_id for context

    print(f"API: Received request to explain text: '{selected_text[:100]}...', context video_id: {video_id_context}")

    if not selected_text.strip():
        return jsonify({"error": "Selected text cannot be empty"}), 400

    # Call the (mock) LLM service function
    # In the future, this would call a real LLM for explanation
    mock_explanation_data = explain_selected_text_mock(selected_text, video_id_context)

    if mock_explanation_data and "explanation" in mock_explanation_data:
        return jsonify({
            "message": "Explanation generated (mock).",
            "explanation": mock_explanation_data["explanation"],
            "original_text": selected_text # Echo back the original text for context if needed
        }), 200
    else:
        return jsonify({"error": "Failed to generate mock explanation"}), 500

# ... (your _build_cors_preflight_response and hello functions) ...
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
    response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS")
    return response

@main_bp.route('/hello', methods=['GET']) 
def hello():
    return jsonify({"message": "Hello from Flask API!"})