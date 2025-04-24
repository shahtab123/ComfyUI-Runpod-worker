# ComfyUI-Runpod-worker
Yet another Runpod template for running ComfyUI. Send a workflow JSON and associated inputs, Runpod runs it and returns the workflow outputs.

Thanks a lot to [blib-la](https://github.com/blib-la/), this repo borrows a lot from their [runpod worker for ComfyUI](https://github.com/blib-la/runpod-worker-comfy).

## Deploying on Runpod
### Set-up a serverless endpoint
1. Fork this repository to your Github account.
2. Create a Runpod account add add some credit.
3. Navigate to the "serverless" section and click on "New Endpoint".
4. Choose "Github Repo", connect to your Github account and select the fork you just made.
5. Change the configuration of your worker(s) (default settings should work for most use cases).

Once that's done, the image should start building, it will be deployed to your worker(s) once done. Check that at least one worker is ready before calling the API you've just set up.

### Calling the API
Once you've deployed a Runpod serverless endpoint following the steps of the [previous section](#set-up-a-worker), you're ready to use it through the Runpod API.

The basics (endpoint specification, etc.) are covered in the [Runpod documentation](https://docs.runpod.io/serverless/endpoints/operations). In this section, we will thus focus on the payload you need to send to the endpoint you've deployed — and what will be returned.

In your `run` / `runsync` POST request, you will need to send a JSON dict with the following format:
```json
{
  "input": {
    "workflow": "...",
    "workflow_inputs": {
        "wf_input_1": "...",
        "wf_input_2": "...",
        ...
    }
  }
}
```
The `input` field is a JSON object containing:
- a `workflow` string, which corresponds to the ComfyUI workflow you want to run, under the API JSON format. The workflow input can either be embedded in this string, or left as placeholders that will be replaced by the values provided in `workflow_inputs` field. Placeholders must be formated as `{{wf_input_name}}`.
- another object `workflow_inputs` where each field corresponds to a placeholder in the `workflow` string, that will be replaced by the corresponding value.

Once your request has been run successfuly, the result will be a list of all the images saved to the `ComfyUI/output/` directory by your workflow.

> [!WARNING]
> Image Preview and other "preview" nodes that only display outputs in the UI without saving imges to files will not output images and you'll get nothing out of them, they are just... for preview in you local ComfyUI setup.

## Development
TODO