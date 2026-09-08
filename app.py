import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from agent.alerting import send_alert
from agent.decision import decide_action
from agent.perception import analyze_image
from agent.safety import check_safety


app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def inspect_site(image_path):
    perception = analyze_image(image_path)

    severity = perception["severity"]
    action = decide_action(severity)
    safety = check_safety(severity, action)

    result = {
        "image_path": image_path,
        "description": perception["description"],
        "anomalies": perception["anomalies"],
        "severity": severity,
        "action": action,
        "safety": safety,
    }

    if action == "send_alert" and safety["approved"]:
        alert_message = (
            f"Site inspection alert: {perception['description']} "
            f"Severity: {severity}."
        )
        result["alert"] = send_alert(alert_message)

    return result


@app.route("/", methods=["GET", "POST"])
def dashboard():
    result = None

    if request.method == "POST":
        image = request.files.get("image")

        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename,
            )

            image.save(image_path)
            result = inspect_site(image_path)

    return render_template("dashboard.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
