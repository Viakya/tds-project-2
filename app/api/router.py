from fastapi import APIRouter, HTTPException
from app.api.schemas import QuizRequest
from app.core.config import SECRET
from app.services.renderer import render_page
from app.services.openai_orchestrator import generate_data_collection_script
from app.services.executor import run_data_collection_script
from app.services.openai_processor import generate_data_processing_script
from app.services.executor_processing import run_processing_script
from app.services.openai_final_answer import generate_final_answer
from app.services.submitter import submit_answer
from app.services.run_saver import (
    create_run_folder,
    save_text,
    save_scraped_data
)
import os

router = APIRouter()

@router.post("/quiz-run")
async def run_quiz(payload: QuizRequest):

    if payload.secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    quiz_url = str(payload.url)

    # ---------------- STEP 1: RENDER HTML ----------------
    html = await render_page(quiz_url)

    run_folder = create_run_folder()
    save_text(run_folder, "html.txt", html)

    # ---------------- STEP 2: DATA COLLECTION (OpenAI) ----------------
    data_script = await generate_data_collection_script(html, quiz_url)
    save_text(run_folder, "data_collection_script.py", data_script)

    collection_result = run_data_collection_script(data_script)
    save_text(run_folder, "collector_stdout.txt", collection_result.get("stdout", ""))
    save_text(run_folder, "collector_stderr.txt", collection_result.get("stderr", ""))

    if not collection_result.get("data_folder"):
        return {
            "status": "collection_failed",
            "run_folder": run_folder,
            "error": collection_result.get("error")
        }

    scraped_folder = collection_result["data_folder"]
    save_scraped_data(scraped_folder, os.path.join(run_folder, "scraped"))
    scraped_files = os.listdir(scraped_folder)

    # ---------------- STEP 3: DATA PROCESSING (OpenAI) ----------------
    processing_script = await generate_data_processing_script(
        html=html,
        quiz_url=quiz_url,
        scraped_file_list=scraped_files
    )
    save_text(run_folder, "data_processing_script.py", processing_script)

    processed = run_processing_script(processing_script, scraped_folder)
    save_text(run_folder, "processor_stdout.txt", processed.get("stdout", ""))
    save_text(run_folder, "processor_stderr.txt", processed.get("stderr", ""))

    if processed.get("output_folder"):
        save_scraped_data(processed["output_folder"], os.path.join(run_folder, "processed"))

    # ---------------- STEP 4: FINAL ANSWER FORMATTER (OpenAI) ----------------
    processor_stdout = processed.get("stdout", "")
    final_answer = await generate_final_answer(
        processor_stdout=processor_stdout,
        html=html,
        quiz_url=quiz_url
    )
    save_text(run_folder, "final_answer.json", str(final_answer))

    # ---------------- STEP 5: AUTO SUBMISSION ----------------
    submit_result = submit_answer(
        email=payload.email,
        secret=payload.secret,
        url=quiz_url,
        answer=final_answer
    )
    save_text(run_folder, "submit_result.txt", str(submit_result))

    # ---------------- DONE ----------------
    return {
        "status": "completed",
        "final_answer": final_answer,
        "submit_response": submit_result,
        "run_folder": run_folder
    }
