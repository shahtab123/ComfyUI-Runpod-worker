import json
import re


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
    # 1. validate input
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

    # 2. extract the workflow and workflow_inputs
    workflow_inputs = job_input.get("workflow_inputs")
    if isinstance(workflow_inputs, str):
        try:
            workflow_inputs = json.loads(workflow_inputs)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse workflow input as a JSON: {e}")
    return workflow, workflow_inputs


def replace_workflow_inputs(workflow: str, inputs: dict = {}) -> str:
    """
    Finds all placeholders in a workflow and replace them with the provided inputs.
    A placeholder in the original workflow is formated as "{{placeholder_name}}". If "placeholder_name" is a key in the inputs dict, it will be replaced by inputs["placeholder_name"].

    Args:
        workflow (str): the original workflow containing placeholders.
        inputs (dict): mapping of the placeholders to their values. Defaults to {} (usefull if the workflow doesn't need any input).

    Returns:
        str: a workflow where all placeholders have been replaced by their values. This workflow should be ready to be sent to the ComfyUI server.
    """

    def replacer(match):
        key = match.group(1)
        placeholders_in_workflow.add(key)
        if key in inputs:
            used_inputs.add(key)
            return str(inputs[key])
        else:
            return match.group(0)

    pattern = re.compile(r"\{\{(\w+)\}\}")
    placeholders_in_workflow = set()
    used_inputs = set()
    result = pattern.sub(replacer, workflow)
    unused_inputs = set(inputs.keys()) - used_inputs
    if unused_inputs:
        print(f"The following inputs were not found in the workflow: {unused_inputs}")
    unresolved_placeholders = placeholders_in_workflow - used_inputs
    if unresolved_placeholders:
        print(f"The following placeholders were not replaced (missing in inputs): {unresolved_placeholders}")
    return result
