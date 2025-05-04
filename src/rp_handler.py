import os
import time

import runpod

from comfy_handler import comfyui_server_ready, get_prompt_history, queue_workflow
from rp_io import parse_job_input, replace_workflow_inputs

COMFY_URL = "http://127.0.0.1:8188"
COMFY_MAX_RETRIES = 100
COMFY_RETRIES_INTERVAL_MS = 100
COMFY_MAX_POLLING_RETRIES = os.getenv("COMFY_MAX_POLLING_RETRIES", 250)
COMFY_POLLING_INTERVAL_MS = os.getenv("COMFY_POLLING_INTERVAL_MS", 500)


def handler(job):
    """
    The main function that handles a job of generating an image.

    This function validates the input, sends a prompt to ComfyUI for processing,
    polls ComfyUI for result, and retrieves generated images.

    Args:
        job (dict): A dictionary containing job details and input parameters.

    Returns:
        dict: A dictionary containing either an error message or a success status with generated images.
    """
    # 1. get and prepare job inputs
    job_input = job["input"]
    try:
        workflow, workflow_inputs = parse_job_input(job_input)
    except ValueError as e:
        return {
            "error": f"Could not parse input, ensure that you are providing valid workflow (required) and workflow inputs (optional): {e}"
        }
    if workflow_inputs is not None:
        if len(workflow_inputs) == 0:
            print('A value was provided for the field "workflow_inputs", but it does not contain any input.')
        try:
            workflow_with_values = replace_workflow_inputs(workflow, workflow_inputs)
        except ValueError as e:
            return {"error": f"Could not replace placeholders in the provided workflow: {e}"}
    else:
        workflow_with_values = workflow
    print(f"Inputs properly processed. The final workflow is:\n{workflow_with_values}")

    # 2. send workflow to ComfyUI server
    if not comfyui_server_ready(COMFY_URL, COMFY_MAX_RETRIES, COMFY_RETRIES_INTERVAL_MS):
        return {
            "error": f"The ComfyUI server did not respond in {COMFY_MAX_RETRIES * COMFY_RETRIES_INTERVAL_MS / 100:.2f}s. Please try again or fix the "
        }
    try:
        queued_workflow = queue_workflow(COMFY_URL, workflow_with_values)
        prompt_id = queued_workflow["prompt_id"]  # ID associated to the queued workflow
        print(f"Successfully queued workflow. Job ID: {prompt_id}")
    except Exception as e:
        return {"error": f"Failed to queue workflow: {e}"}

    # 3. poll ComfyUI server state for completion
    for retry in range(COMFY_MAX_POLLING_RETRIES):
        try:
            history = get_prompt_history(COMFY_URL, prompt_id)
            if prompt_id in history:
                prompt_outputs = history[prompt_id].get("outputs")
                if prompt_outputs:
                    break
        except Exception as e:
            return {
                "error": f"Failed to poll ComfyUI status during generation after {retry} retries ({retry * COMFY_POLLING_INTERVAL_MS}ms.): {e}"
            }
        time.sleep(COMFY_POLLING_INTERVAL_MS / 1000)

    # 4. handle ComfyUI output
    # TODO

    return ...


if __name__ == "__main__":
    # See Runpod documentation:
    # https://docs.runpod.io/serverless/workers/handlers/overview
    runpod.serverless.start({"handler": handler})
