![logo](chat/static/chat/images/ChatGPDB-icon.png)

Welcome to the source code repository for ChatGPDB!
Here you'll see how the sausage is made. We use the following technology:

* Django - Implements and runs the webserver
* Websockets - Provides the snappy interface during compute-intensive, slow (relative to a typical request lifetime) model inference.
* Huggingface - Provides the Python library (transformers) and model repository to download and use pre-trained machine learning models like GPT.

## Local setup

Think ChatGPDB is cool? Want to set it up yourself? Read the instructions below to find out how.

1. Clone the GPT2-Large pretrained model by OpenAI. The model is available at [HuggingFace](https://huggingface.co/gpt2-large).
   Use the following command inside this repository:
```shell
$ git clone https://huggingface.co/gpt2-large
```
2. Use `git lfs` to download the model files (you may have to install this git extension if the command fails). This may take awhile as `git-lfs` needs to download about 15 GB of model files (depending on how git is configured, LFS may be invoked as part of step 1).
```shell
$ cd gpt2-large
$ git lfs pull
```
3. Create the conda environment with the necessary packages. Note that this environment builds packages capable of accelerating GPT2 inference using NVidia GPUs in a CUDA environment. It is known to work on Linux, but does not work as-is on Mac. Create the environment with:
```shell
$ conda env create -f environment.yaml
```
4. Activate the new environment using `conda activate chatgpdb-dev`
5. Launch the server using `python manage.py runserver` and off you go!

## GPU support

Have an NVidia GPU capable of accelerating PyTorch model inference? Great! The default configuration is already set up to take advantage.

Don't have an NVidia GPU but want to try it out, anyway? Change the `RUN_CUDA` variable inside `chatgpdb/settings.py` file to `False`.

Note that many LLMs are large (many millions to many billions of parameters), meaning that large memory GPUs are often required for inference.

## Response length

Want a longer or shorter response from GPT? Longer responses take longer to generate (unsurprisingly), but may also be more entertaining. To tune how long of a sequence the model should generate, set the `CHATGPDB_RESPONSE_WORD_COUNT` environment variable to the desired integer value and launch the web server.

# Have fun!

Brought to you by Jason Swails and Thomas Watson
