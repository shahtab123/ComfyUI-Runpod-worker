import runpod


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
    raise NotImplementedError("[COMFYUI WORKER] Runpod handler is not implemented yet.")


if __name__ == "__main__":
    # See Runpod documentation:
    # https://docs.runpod.io/serverless/workers/handlers/overview
    runpod.serverless.start({"handler": handler})
