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


#### Sending a job
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

#### Receiving the output
Once your request has be run successfully, you should get the following result:
```json
{
  "delayTime": ...,      // Time in queue (ms)
  "executionTime": ..., // Processing time (ms)
  "id": ...,
  "output": [{...}],
  "status": "COMPLETED"
}
```

Where the field containing the result is `output` and contains a field for each output image, where the key is the path of the image from the ComfyUI output directory and the value is the base64-encoded image. 

If after running the ComfyUI workflow the output directory contains:
```
img02.jpg
Flux.1/
├── flux01.png
└── flux02.png
```

The `output` value will be the following.
```json
[{
  "img02.jpg": ...,
  "Flux.1/flux01.png": ...,
  "Flux.1/flux02.png": ...,
}]
```

You can then easily extract all images or reconstruct the output directory locally using the keys as save paths.

#### Using the CLI to call the API
A basic CLI allowing you to test your endpoint is available: [clientside/client.py](./clientside/call_api.py).

For instance, if you want to run the [clientside/flux_txt2img.json](./clientside/flux_txt2img.json) workflow to generate 4 images using Flux.1 \[dev\] with the prompt "A cute kitty in Game of Thrones", set the `RUNPOD_KEY` environment variable to your Runpod API key (create one [here](https://www.runpod.io/console/user/settings)) or create a `.env` file. You can then run the following commands:
```bash
cd clientside
python call_api.py --endpoint YOUR_ENDPOINT_ID --workflow_path flux_txt2img.json --inputs "prompt=A cute kitty in Game of Thrones"
```
Replace `YOUR_ENDPOINT_ID` by the ID of the Runpod serverless endpoint you deployed.


> [!WARNING]
> Image Preview and other "preview" nodes that only display outputs in the UI without saving images to files will not output images and you'll get nothing out of them, they are just... for preview in you local ComfyUI setup.

## Roadmap
The following list outlines the planned development roadmap. Changes to this roadmap might happen.
- [x] Working endpoint: send a JSON, inputs, and get the result images back
- [ ] Support uploading images as links
- [ ] Support non-string parameter types (e.g. integers for seed)
- [ ] Support non-image output types (most importantly text)
- [ ] Allow the user to provide custom models to download as model name, model URL pairs
- [ ] Better configuration options through environment variables
- [ ] Support uploading results to an S3 bucket instead of returning them