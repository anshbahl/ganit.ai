import json
import os
from flask import Flask, jsonify, request, send_file, send_from_directory, Response
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")

app = Flask(__name__)


@app.route("/")
def index():
    return send_file('web/index.html')


@app.route("/api/generate", methods=["POST"])
def generate_api():
    try:
        req_body = request.get_json()
        content = req_body.get("contents")

        if not isinstance(content, list) or not content or not isinstance(content[0], dict):
            return jsonify({ "error": "Invalid contents format" }), 400

        content.append({
            "type": "text",
            "text": "If the given question is not a math question, simply say: This is not a math question. Please enter a math question. Do not say anything else. Else solve and explain."
        })

        prompt_text = "\n".join(item["text"] for item in content if item["type"] == "text")

        model = ChatGoogleGenerativeAI(model=req_body.get("model"))
        message = HumanMessage(content=prompt_text)
        response = model.stream([message])

        def stream():
            for chunk in response:
                yield f'data: {json.dumps({"text": chunk.content})}\n\n'

        return Response(stream(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
