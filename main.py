from fasthtml.common import (
    fast_app,
    Script,
    Main,
    Div,
    Button,
    H1,
    Span,
    Img,
    Video,
    A,
    serve
)
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Add this line before using env variables

ULTRAVOX_API_KEY = os.environ.get('ULTRAVOX_API_KEY')
if not ULTRAVOX_API_KEY:
    raise ValueError("ULTRAVOX_API_KEY environment variable is not set")

app, rt = fast_app(pico=False, hdrs=(Script(src="https://cdn.tailwindcss.com"),))

def fixie_request(method, path, **kwargs):
    u = "https://api.ultravox.ai/api"
    return requests.request(
        method, u + path, headers={"X-API-Key": ULTRAVOX_API_KEY}, **kwargs
    )

EXAMPLE_TOOL = [
    {
        "temporaryTool": {
            "modelToolName": "getCatFact",
            "description": "Returns back a random cat fact",
            "http": {
                "baseUrlPattern": "https://catfact.ninja/fact",
                "httpMethod": "GET",
            },
        }
    }
]

js_on_load = """
import { UltravoxSession } from 'https://esm.sh/ultravox-client';
const debugMessages = new Set(["debug"]);
window.UVSession = new UltravoxSession({ experimentalMessages: debugMessages });
"""

TW_BUTTON = "bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2.5 px-6 rounded-lg transition duration-150 ease-in-out shadow-sm hover:shadow-md"

def client_js(callDetails):
    return f"""
    async function joinCall() {{
        // Hide default image and show initializing state when call starts
        htmx.find("#DefaultVoiceImg").style.display = "none";
        const callStatus = await window.UVSession.joinCall("{callDetails.get('joinUrl')}");
        console.log(callStatus);
    }}

    // Set initial display states
    htmx.find("#AgentVoiceImg").style.display = "none";
    htmx.find("#UserVoiceImg").style.display = "none";
    htmx.find("#DefaultVoiceImg").style.display = "block";

    window.UVSession.addEventListener('status', (e) => {{
        let statusDiv = htmx.find("#call-status")
        statusDiv.innerText = e.target._status;
        
        // Show/hide voice animations based on status
        const agentImg = htmx.find("#AgentVoiceImg");
        const userImg = htmx.find("#UserVoiceImg");
        const defaultImg = htmx.find("#DefaultVoiceImg");
        
        if (e.target._status === "speaking") {{
            agentImg.style.display = "block";
            userImg.style.display = "none";
            defaultImg.style.display = "none";
        }} else if (e.target._status === "listening") {{
            agentImg.style.display = "none";
            userImg.style.display = "block";
            defaultImg.style.display = "none";
        }} else {{
            agentImg.style.display = "none";
            userImg.style.display = "none";
            defaultImg.style.display = "none";  // Keep default hidden after call starts
        }}
    }});

    window.UVSession.addEventListener('transcripts', (e) => {{
        let transcripts = e.target._transcripts;
        transcript = htmx.find("#transcript");
        transcript.innerText = transcripts.filter(t => t && t.speaker !== "user").map(t => t ? t.text : "").join("\\n");
    }});

    window.UVSession.addEventListener('experimental_message', (msg) => {{
      console.log('Debug: ', JSON.stringify(msg));
    }});

    joinCall();

    htmx.on("#end-call", "click", async (e) => {{
        try {{
            await UVSession.leaveCall();
        }} catch (error) {{
            console.error("Error leaving call:", error);
        }}
    }})
    """

def layout(*args, **kwargs):
    return Main(
        Div(
            Div(
                # Main panel with shadow, rounded corners, and padding
                Div(*args, **kwargs,
                    cls="bg-white shadow-lg rounded-lg p-4 max-w-[350px] mx-auto border border-gray-200"  # Removed mt-10
                ),
                cls="mx-auto max-w-3xl"
            ),
            cls="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 min-h-screen bg-gray-50 py-1"
        )
    )

@rt("/")
def get():
    button = Button("Llamar/Call", hx_post="/start", hx_target="#call-mgmt", hx_swap="outerHTML", cls=TW_BUTTON)
    return layout(
        Script(js_on_load, type="module"),
        Div(
            Img(src="Logo.png", alt="Logo", cls="mx-auto max-w-[200px] w-full mb-4"),
            Div(cls="h-px bg-gray-200 w-full mb-6"),
            cls="text-center"
        ),
        Div(
            H1("Hotel Poblado Alto", cls="text-3xl font-bold mb-1 text-center text-gray-700"),
            H1("Recepción/Receptionist", cls="text-xl font-normal text-center text-gray-500"),
            cls="mb-8"
        ),
        Div(
            Div(
                Img(src="Voice.svg", alt="Default Voice Icon", cls="h-[100px] w-[100px] mx-auto block", id="DefaultVoiceImg"),
                Video(src="VoiceBlue.webm", type="video/webm", alt="Agent Voice Animation", 
                    cls="h-[125px] w-[125px] mx-auto hidden",
                    controls="false", autoplay="true", loop="true", muted="true",
                    poster="Voice.svg", id="AgentVoiceImg",
                ),
                Video(src="VoiceRed.webm", type="video/webm", alt="User Voice Animation",
                    cls="h-[125px] w-[125px] mx-auto hidden",
                     controls="false", autoplay="true", loop="true", muted="true",
                    poster="Voice.svg", id="UserVoiceImg"),
                cls="flex justify-center items-center mb-6"
            ),
            Div(button, cls="text-center mb-8"),
            Div(cls="h-px bg-gray-200 w-full mb-4"),
            Div(
                "Status: ",
                Span("Waiting", id="call-status", cls="text-blue-600"),
                cls="mb-4 text-gray-700 text-center"
            ),
            Div(
                Span("Powered by ", cls="italic"),
                Span(A("AI-Agency.dev", href="https://ai-agency.dev", cls="text-gray-400 hover:text-gray-500")),
                cls="text-center text-gray-400 text-sm mt-4"
            ),
            id="call-mgmt"
        )
    )

@rt("/start")
async def post():
    r = fixie_request("POST", "/agents/b97f376d-f229-4ae2-89f9-5ea04a2600d8/calls")
    if r.status_code == 201:
        callDetails = r.json()
        js = client_js(callDetails)
        return Div(
            Div(
                "Status: ",
                Span("Initializing", id="call-status", cls="font-bold text-blue-600"),
                cls="mb-4 text-gray-700"
            ),
            Button("Colgar/End Call", id="end-call", cls=TW_BUTTON + " bg-red-500 hover:bg-red-600", hx_get="/end", hx_swap="outerHTML"),
            Div("", id="transcript", cls="mt-6 p-4 bg-gray-50 rounded-lg text-gray-700 min-h-[100px]"),
            Script(code=js),
            cls="space-y-4"
        )
    else:
        return r.text

@rt("/end")
def get():
    return Button("Llamar/Restart", id="re-start", cls=TW_BUTTON + " bg-green-500 hover:bg-green-600", hx_get="/", hx_target="body", hx_boost="false")

serve()
