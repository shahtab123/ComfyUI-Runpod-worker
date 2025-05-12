import time

import requests


def comfyui_server_ready(host_url: str, max_retries: int = 500, retries_interval_ms: int = 50) -> bool:
    """
    Checks that the ComfyUI server is reachable via HTTP GET request.

    Args:
        host_url (str): URL to query.
        max_retries (int): the maximum number of times to try to connect to the server. Defaults to 500.
        retries_interval_ms (int): the interval (in milliseconds) between each connection attempt. Defaults to 50.

    Returns:
        bool: True iff the server located at the input URL could be reached withing the given number of retries.
    """
    for _ in range(max_retries):
        try:
            if requests.get(host_url).status_code == 200:
                return True
        except requests.RequestException:
            time.sleep(retries_interval_ms / 1000)
    return False


def queue_workflow(host_url: str, workflow: str) -> dict:
    """
    Queues a worflow to the ComfyUI server and returns the response.

    Args:
        host_url (str): the location of the ComfyUI server.
        workflow (str): the workflow to be queued.

    Raises:
        requests.HTTPError: raised if the response from the ComfyUI server is not in the 200 range.

    Returns:
        dict: the JSON response from the ComfyUI server after processing the input workflow.
    """
    url = host_url.rstrip("/") + "/prompt"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json={"prompt": workflow}, headers=headers)
    response.raise_for_status()
    return response.json()


def get_prompt_history(host_url: str, prompt_id: str) -> dict:
    """
    Retrieves the history of a prompt using the provided ID.

    Args:
        host_url (str): the location of the ComfyUI server.
        prompt_id (str): ID of the prompt that needs to be retrieved.

    Raises:
        requests.HTTPError: raised if the response from the ComfyUI server is not in the 200 range.

    Returns:
        dict: prompt history returned by the ComfyUI server. See https://github.com/zigzagGmbH/VW-AA-ComfyUI-Workflow-Executor/blob/main/docs/COMFYUI_API.md for more info.
    """
    url = host_url.rstrip("/") + f"/history/{prompt_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
