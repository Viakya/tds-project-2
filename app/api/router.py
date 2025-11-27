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
import time

router = APIRouter()

@router.post("/quiz-run")
async def run_quiz(payload: QuizRequest):
    total = time.time()

    if payload.secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    quiz_url = str(payload.url)
    print(f"Starting quiz run for URL: {quiz_url}")

    render_time = time.time()

    # ---------------- STEP 1: RENDER HTML ----------------
    html = await render_page(quiz_url)

    run_folder = create_run_folder()
    save_text(run_folder, "html.txt", html)
    print(f"Run folder created at: {run_folder}")

    render_end = time.time()
    print(f"Page rendered in {render_end - render_time:.2f} seconds.")

    data_collection_time = time.time()

    # ---------------- STEP 2: DATA COLLECTION (OpenAI) ----------------
    print("Generating data collection script...")
    data_script = await generate_data_collection_script(html, quiz_url)
    save_text(run_folder, "data_collection_script.py", data_script)
    print("Running data collection script...")

    collection_result = run_data_collection_script(data_script)
    save_text(run_folder, "collector_stdout.txt", collection_result.get("stdout", ""))
    save_text(run_folder, "collector_stderr.txt", collection_result.get("stderr", ""))

    print("Data collection completed.")

    if not collection_result.get("data_folder"):
        return {
            "status": "collection_failed",
            "run_folder": run_folder,
            "error": collection_result.get("error")
        }

    scraped_folder = collection_result["data_folder"]
    save_scraped_data(scraped_folder, os.path.join(run_folder, "scraped"))
    scraped_files = os.listdir(scraped_folder)

    print(f"Scraped files: {scraped_files}")

    data_collection_end = time.time()
    print(f"Data collection took {data_collection_end - data_collection_time:.2f} seconds.")

    data_processing_time = time.time()
    # ---------------- STEP 3: DATA PROCESSING (OpenAI) ----------------
    print("Generating data processing script...")
    processing_script = await generate_data_processing_script(
        html=html,
        quiz_url=quiz_url,
        scraped_file_list=scraped_files
    )
    save_text(run_folder, "data_processing_script.py", processing_script)
    print("Running data processing script...")

    processed = run_processing_script(processing_script, scraped_folder)
    print("Data processing completed.")
    print(f"Processing output: {processed}")
    save_text(run_folder, "processor_stdout.txt", processed.get("stdout", ""))
    save_text(run_folder, "processor_stderr.txt", processed.get("stderr", ""))
    print(f"Processed files: {os.listdir(processed.get('output_folder', ''))}")

    if processed.get("output_folder"):
        save_scraped_data(processed["output_folder"], os.path.join(run_folder, "processed"))
    data_processing_end = time.time()
    print(f"Data processing took {data_processing_end - data_processing_time:.2f} seconds.")

    # ---------------- STEP 4: FINAL ANSWER FORMATTER (OpenAI) ----------------
    final_answer_time = time.time()
    print("Generating final answer...")
    processor_stdout = processed.get("stdout", "")
    final_answer = await generate_final_answer(
        processor_stdout=processor_stdout,
        html=html,
        quiz_url=quiz_url
    )
    
    print("Raw final answer:", final_answer_raw)
    
    # Extract the post URL
    post_url = final_answer_raw.get("post_url")
    
    # Create cleaned final answer object (remove post_url)
    final_answer = {"answer": final_answer_raw["answer"]}

    print(f"Final answer generated: {final_answer}")
    save_text(run_folder, "final_answer.json", str(final_answer))
    final_answer_end = time.time()
    print(f"Final answer generation took {final_answer_end - final_answer_time:.2f} seconds.")

    # ---------------- STEP 5: AUTO SUBMISSION ----------------
    submit_result = submit_answer(
        email=payload.email,
        secret=payload.secret,
        url=post_url,
        answer=final_answer
    )

    save_text(run_folder, "submit_result.txt", str(submit_result))

    total_end = time.time()
    print(f"Quiz run completed in {total_end - total:.2f} seconds.")

    # ---------------- DONE ----------------
    return {
        "status": "completed",
        "final_answer": final_answer,
        "run_folder": run_folder
    }
