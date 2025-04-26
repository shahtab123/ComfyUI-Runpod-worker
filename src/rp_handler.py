import runpod
from runpod import RunPodLogger

from comfy_handler import comfyui_server_ready
from rp_io import parse_job_input, replace_workflow_inputs

COMFY_URL = "http://127.0.0.1:8188"
COMFY_MAX_RETRIES = 100
COMFY_RETRIES_INTERVAL_MS = 100


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
    logger = RunPodLogger()

    # get and prepare job inputs
    job_input = job["input"]
    try:
        workflow, workflow_inputs = parse_job_input(job_input)
    except ValueError as e:
        return {
            "error": f"Could not parse input, ensure that you are providing valid workflow (required) and workflow inputs (optional): {e}"
        }
    logger.debug(f"Parsed job input successfully. {workflow = } | {workflow_inputs = }")
    if (not workflow_inputs is None) and len(workflow_inputs) == 0:
        logger.warn('A value was provided for the field "workflow_inputs", but it does not contain any input.')
    try:
        workflow_with_values = replace_workflow_inputs(workflow, workflow_inputs)
    except ValueError as e:
        return {"error": f"Could not replace placeholders in the provided workflow: {e}"}

    if not comfyui_server_ready(COMFY_URL, COMFY_MAX_RETRIES, COMFY_RETRIES_INTERVAL_MS):
        return {
            "error": f"The ComfyUI server did not respond in {COMFY_MAX_RETRIES * COMFY_RETRIES_INTERVAL_MS / 100:.2f}s. Please try again or fix the "
        }

    # TODO implement workflow queueing, state polling and output handling
    raise NotImplementedError


if __name__ == "__main__":
    # See Runpod documentation:
    # https://docs.runpod.io/serverless/workers/handlers/overview
    runpod.serverless.start({"handler": handler})
