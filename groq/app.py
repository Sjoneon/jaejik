import os

from flask import Flask, jsonify, request
from groq import Groq

app = Flask(__name__, static_folder="static", static_url_path="/static")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({
            "error": "GROQ_API_KEY environment variable is not set."
        }), 500

    client = Groq()

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.6,
            max_completion_tokens=512,
            top_p=0.95,
            stream=False,
            stop=None,
        )

        reply = completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
