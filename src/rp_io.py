import json


def parse_job_input(job_input: dict) -> tuple:
    """
    Extracts the workflow (required) and the various workflow inputs (optional) from the job input.

    Args:
        job_input (dict): the job input, see: https://docs.runpod.io/serverless/handlers/overview#job-input

    Returns:
        tuple: (workflow, workflow_inputs) where:
            - workflow (str): a string describing the ComfyUI workflow under the API JSON format.
            - workflow_inputs (dict): each key is the name of an input in the workflow and the corresponding value is the input value. Can be None (no input provided).
    """
    if job_input is None:
        raise ValueError("No input provided, ensure you at least pass a workflow.")

    # convert string inputs to JSON
    if isinstance(job_input, str):
        try:
            job_input = json.loads(job_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse job input as a JSON: {e}")

    workflow = job_input.get("workflow")
    if workflow is None:
        raise ValueError('No workflow provided, ensure you have a non null value for the "workflow" input field.')
    if len(workflow) == 0:
        raise ValueError("The input workflow is empty, ensure you are passing a valid workflow.")

    workflow_inputs = job_input.get("workflow_inputs")
    if isinstance(workflow_inputs, str):
        try:
            workflow_inputs = json.loads(workflow_inputs)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse workflow input as a JSON: {e}")

    return workflow, workflow_inputs


def replace_workflow_inputs(workflow: str, inputs: dict) -> str:
    # TODO
    raise NotImplementedError()
