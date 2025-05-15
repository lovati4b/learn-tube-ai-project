from flask import Blueprint, request, jsonify
import json # For converting string to dict and vice-versa
from .services.llm_service import get_llm_completion 
from .services.video_processing_service import get_youtube_transcript, extract_video_id_from_url # Added extract_video_id
from . import db # Import db instance
from .models import Video # Import Video model

main_bp = Blueprint('main', __name__)

SYSTEM_PROMPT_VIDEO_ANALYSIS = """
You are an expert AI assistant specializing in analyzing educational video transcripts.
Your task is to extract key information and structure it as a valid JSON object.
The JSON object must have the following top-level keys: "table_of_contents", "key_terms", "logical_flow".

- "table_of_contents": An array of objects, where each object has "title" (string, concise segment title) and "timestamp_seconds" (integer, approximate start time in seconds for that segment). Derive timestamps from the context if not explicitly stated.
- "key_terms": An array of objects, where each object has "term" (string, the key term or concept) and "definition" (string, a concise definition relevant to the transcript's context).
- "logical_flow": A string containing a hierarchical outline or a paragraph summarizing the main topics and their progression in the video. Use markdown for simple formatting if helpful (e.g., bullet points).

Ensure the entire output is a single, valid JSON object. Do not include any explanatory text outside of the JSON structure itself.
"""

@main_bp.route('/api/process_video', methods=['POST'])
def process_video():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"error": "Missing 'video_url' in request"}), 400

    print(f"Received video URL: {video_url}")
    video_id = extract_video_id_from_url(video_url)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL or could not extract video ID"}), 400

    # --- Step 1: Check cache (Database) ---
    cached_video = Video.query.get(video_id)
    if cached_video and cached_video.llm_analysis_json and cached_video.processing_status == 'completed':
        print(f"Found cached and completed analysis for video ID: {video_id}")
        return jsonify({
            "message": "Analysis retrieved from cache.",
            "video_url": video_url,
            "video_id": video_id,
            "status": "cached",
            "analysis": cached_video.get_llm_analysis() # Use the model's helper method
        }), 200
    elif cached_video and cached_video.processing_status in ['pending', 'processing_transcript', 'processing_llm']:
         print(f"Processing already in progress for video ID: {video_id} (status: {cached_video.processing_status})")
         return jsonify({
            "message": "Video processing is already in progress or pending.",
            "video_url": video_url,
            "video_id": video_id,
            "status": cached_video.processing_status
         }), 202 # Accepted
    # ------------------------------------
    
    # If not cached or not complete, or failed previously, try processing:
    current_video_entry = cached_video
    if not current_video_entry:
        current_video_entry = Video(id=video_id, processing_status='pending')
        db.session.add(current_video_entry)
        # Commit early to establish the row if it's new and status is pending
        try:
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"DB Error on initial save for {video_id}: {e}")
            return jsonify({"error": "Database error during initial video save", "details": str(e)}), 500


    # --- Step 2: Get the transcript ---
    current_video_entry.processing_status = 'processing_transcript'
    current_video_entry.last_processing_error = None # Clear previous errors
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback() # Rollback status change if commit fails
        print(f"DB Error updating status to processing_transcript for {video_id}: {e}")
        return jsonify({"error": "Database error updating video status", "details": str(e)}), 500

    print(f"Attempting to fetch transcript for: {video_url}")
    actual_transcript_text, transcript_error_message = get_youtube_transcript(video_url) # video_url or video_id

    if transcript_error_message:
        print(f"Transcript fetching error for {video_id}: {transcript_error_message}")
        current_video_entry.processing_status = 'failed_transcript'
        current_video_entry.last_processing_error = transcript_error_message
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"DB Error on saving transcript failure for {video_id}: {e}")
        return jsonify({"error": "Failed to fetch transcript", "details": transcript_error_message}), 422

    current_video_entry.transcript_text = actual_transcript_text
    print(f"Transcript fetched successfully for {video_id} (first 100 chars): {actual_transcript_text[:100]}...")
    # -------------------------------------

    # --- Step 3: Call LLM service ---
    current_video_entry.processing_status = 'processing_llm'
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"DB Error updating status to processing_llm for {video_id}: {e}")
        return jsonify({"error": "Database error updating video status", "details": str(e)}), 500
        
    print(f"Calling LLM service for analysis with actual transcript for {video_id}...")
    try:
        user_prompt_for_analysis = f"""
        Analyze the following video transcript and generate the requested information.
        Make sure your response strictly follows the JSON format specified in the system instructions.

        Transcript:
        ---
        {actual_transcript_text}
        ---
        """
        llm_analysis_dict = get_llm_completion( # This will be a dict if successful
            prompt=user_prompt_for_analysis,
            system_prompt=SYSTEM_PROMPT_VIDEO_ANALYSIS,
            is_json_output=True
        )

        if not llm_analysis_dict: # Should not happen if get_llm_completion raises error on failure
            raise ValueError("LLM returned empty or None analysis")

        print(f"LLM Analysis Results for {video_id} (type: {type(llm_analysis_dict)}): {str(llm_analysis_dict)[:200]}...")
        
        # Save to DB
        current_video_entry.set_llm_analysis(llm_analysis_dict) # Use the model's helper
        current_video_entry.processing_status = 'completed'
        current_video_entry.last_processing_error = None
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"DB Error on final save for {video_id}: {e}")
            # Still return results to user if LLM was successful but DB save failed
            # Or decide to return an error
            return jsonify({"error": "Database error saving analysis", "details": str(e)}), 500


        return jsonify({
            "message": "Video analysis completed and saved.",
            "video_url": video_url,
            "video_id": video_id,
            "status": "processed_and_saved",
            "analysis": llm_analysis_dict
        }), 200

    except ValueError as ve: # Catch specific error from LLM if JSON parsing fails or other value error
        print(f"ValueError during LLM processing for {video_id}: {str(ve)}")
        current_video_entry.processing_status = 'failed_llm'
        current_video_entry.last_processing_error = f"LLM Value Error: {str(ve)}"
        db.session.commit() # Save error state
        return jsonify({"error": "LLM processing error (ValueError)", "details": str(ve)}), 500
    except Exception as e:
        print(f"Generic error during LLM processing for {video_id}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        current_video_entry.processing_status = 'failed_llm'
        current_video_entry.last_processing_error = f"LLM Generic Error: {str(e)}"
        db.session.commit() # Save error state
        return jsonify({"error": "Failed to process video with LLM", "details": str(e)}), 500