import argparse
import json
import os
import time

import requests
from dotenv import load_dotenv

from helpers import save_b64_image

POLL_INTERVAL_MS = 5000  # milliseconds between each status poll


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--endpoint",
        type=str,
        required=True,
        help="ID of the Runpod serverless endpoint. Get it from the Runpod console.",
    )
    parser.add_argument(
        "--workflow_path",
        type=str,
        default="workflow.json",
        help="Path to the workflow under the API JSON format, straight from ComfyUI.",
    )
    parser.add_argument(
        "--inputs",
        type=str,
        nargs="*",
        help="Workflow inputs to replace the placeholders in the workflow JSON. Formated as a list of key=value elements.",
    )

    args = parser.parse_args()

    # parse input key=value pairs
    if args.inputs is not None:
        inputs = {}
        for input in args.inputs:
            if "=" not in input:
                raise ValueError(f'Invalid input format {input}. Please format the inputs as "key=value".')
            k, v = input.split("=")
            inputs[k] = v
        args.inputs = inputs

    # open workflow
    with open(args.workflow_path) as f:
        args.workflow = json.load(f)

    return args


def send_workflow(api_key: str, endpoint_id: str, workflow: dict, inputs: dict = None) -> requests.Response:
    """
    Sends a request to the Runpod ComfyUI endpoint to run a new workflow with inputs.

    Args:
        api_key (str)
        endpoint_id (str): ID of the serverless endpoint.
        workflow (dict): ComfyUI workflow under the API JSON format.
        inputs (dict): optional inputs for the ComfyUI workflow. Defaults to None.

    Returns:
        requests.Response
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "input": {
            "workflow": workflow,
            "workflow_inputs": inputs,
        }
    }
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    return requests.post(url, headers=headers, json=data)


def wait_for_completion(api_key: str, endpoint_id: str, job_id: str, poll_interval_ms: int = 500) -> dict:
    """
    Poll job status continuously until completion and returns the job result when the job is completed.

    Args:
        api_key (str)
        endpoint_id (str): ID of the serverless endpoint.
        job_id (str): ID of the job.
        poll_interval_ms (int): milliseconds between each status poll. Defaults to 500.

    Returns:
        dict: the JSON returned by the Runpod enpoint after job completion.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"

    poll_count = 0
    while True:
        poll_count += 1
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            poll_json = response.json()
            status = poll_json.get("status")
            if str(status).lower() in ["in_queue", "in_progress"]:
                time.sleep(poll_interval_ms / 1000)
            elif str(status).lower() in ["completed", "success"]:
                print(f"Job completed successfully in {poll_count * poll_interval_ms / 1000:.0f}s.")
                return poll_json
            elif str(status).lower() in ["failed", "error"]:
                raise Exception(f"Job failed: {poll_json}")
        else:
            raise Exception(f"Failed to poll job status {response.status_code}: {response.text}")


if __name__ == "__main__":
    args = get_args()

    load_dotenv()
    API_KEY = os.getenv("RUNPOD_KEY")
    if API_KEY is None:
        raise EnvironmentError(
            'Please set the "RUNPOD_KEY" environment variable or set its values in the .env file. You can create a new Runpod API key in Account > Settings > API Keys.'
        )

    print("Sending workflow...")
    response = send_workflow(API_KEY, args.endpoint, args.workflow, args.inputs)
    if response.status_code != 200:
        raise Exception(f"Failed to send workflow with code {response.status_code}: {response.text}")

    job_id = response.json().get("id")
    print("Waiting for completion...")
    result = wait_for_completion(API_KEY, args.endpoint, job_id, POLL_INTERVAL_MS)

    output_images = result.get("output")
    print(f"Saving {len(output_images)} image(s) to the disk...")
    for image_path, b64_image in output_images.items():
        save_path = os.path.join("./", image_path.lstrip("/"))
        save_b64_image(b64_image, save_path)

    print("Done.")
