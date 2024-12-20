# Ultravox Web Quickstart

This is a quickstart project for creating a web-based Voice AI Agent on Ultravox. We've tried to keep it as simple as possible to show all of the key parts in a single file.

This example depends on the `python-fasthtml` package, which is a great little project for building web apps in pure python. We need the web app to create the initial request to Ultravox to start the call.

On the client, we depend on the `ultravox-client` library (see [npm package](https://www.npmjs.com/package/ultravox-client)). To simplify the example, we load the Ultravox Client library directly from [esm.sh](https://esm.sh).

## Getting Started

1. Clone this repository
1. Install [https://fastht.ml/](https://fastht.ml/) with `pip install python-fasthtml`
1. Get an API key from [https://app.ultravox.ai](app.ultravox.ai) and either set it as an environment variable under `ULTRAVOX_API_KEY` or replace the value in `main.py`
1. Run `python main.py`
1. Open your browser to `http://localhost:5001`

## Looking for React?
If you're looking for a more advanced example using React, go here: [https://github.com/fixie-ai/ultravox-demo-template-vercel](https://github.com/fixie-ai/ultravox-demo-template-vercel).
