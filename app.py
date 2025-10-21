from flask import Flask, request, jsonify
from google.cloud import logging, pubsub_v1
from vertexai.preview.language_models import TextGenerationModel
import os
from utils.cleaning import clean_transcript
from utils.dq_checks import run_dq_checks
from utils.pii import mask_pii
from utils.db import insert_to_sql

app = Flask(__name__)

# Setup logging
client = logging.Client()
logger = client.logger("transcript-pipeline")

@app.route("/", methods=["POST"])
def handle_pubsub():
    """Entry point triggered by Pub/Sub event."""
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Bad Request", 400

    message = envelope["message"]
    data = message.get("data")
    transcript_id = message.get("attributes", {}).get("transcript_id", "unknown")

    # 1️⃣ Retrieve transcript text (assuming data is base64 encoded)
    import base64
    transcript_text = base64.b64decode(data).decode("utf-8")

    logger.log_text(f"Processing transcript {transcript_id}...")

    try:
        # 2️⃣ Store raw transcript (bronze)
        insert_to_sql("bronze_transcripts", transcript_id, transcript_text)

        # 3️⃣ Clean & preprocess
        cleaned = clean_transcript(transcript_text)
        masked = mask_pii(cleaned)

        # 4️⃣ Data quality checks
        dq_pass, dq_report = run_dq_checks(masked)
        if not dq_pass:
            logger.log_text(f"DQ failed for {transcript_id}: {dq_report}")
            return jsonify({"status": "DQ failed"}), 400

        # 5️⃣ Save to processed table (silver)
        insert_to_sql("silver_transcripts", transcript_id, masked)

        # 6️⃣ Generate summary with Vertex AI
        model = TextGenerationModel.from_pretrained("gemini-1.5-pro")
        summary = model.predict(
            f"Summarize this client meeting:\n\n{masked}",
            temperature=0.2,
            max_output_tokens=256
        ).text

        # 7️⃣ Save summary (gold)
        insert_to_sql("gold_summaries", transcript_id, summary)

        logger.log_text(f"Transcript {transcript_id} processed successfully.")
        return jsonify({"status": "success", "summary": summary}), 200

    except Exception as e:
        logger.log_text(f"Error processing transcript {transcript_id}: {e}", severity="ERROR")
        return jsonify({"error": str(e)}), 500
