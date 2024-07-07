from flask import Flask, request, jsonify

app = Flask(__name__)

import base64

import requests

import pprint

validate_url = "https://eportal.incometax.gov.in/iec/guestservicesapi/validateOTP/"

# proxy = {
#     "http": "184.168.124.233:5402",
#     "https": "184.168.124.233:5402",
# }

validate_payload = {
    "panNumber": "",
    "fullName": "",
    "dob": "1996-07-09",
    "mobNo": "",
    "areaCd": "91",
    "otp": "299346",
    "serviceName": "verifyYourPanService",
    "formName": "FO-009-VYPAN",
    "reqId": "FOS004478380700",
}


saveEntityPayload = {
    "panNumber": "ABCDEF1234A",
    "fullName": "ABCD XYZ",
    "dob": "1993-07-02",
    "mobNo": "9999999999",
    "areaCd": "91",
    "serviceName": "verifyYourPanService",
    "formName": "FO-009-VYPAN",
}


local_session = {}


def encode_base64(input_string):
    # Convert string to bytes
    byte_data = input_string.encode("utf-8")
    # Encode bytes to Base64
    base64_encoded = base64.b64encode(byte_data)
    # Convert Base64 bytes back to string
    return base64_encoded.decode("utf-8")


@app.route("/api/validateOTP", methods=["post"])
def validateOTP():
    session = requests.Session()
    post_url = "https://eportal.incometax.gov.in/iec/guestservicesapi/validateOTP/"
    """
        {
            "otp" : "091716",
            "reqId" : "FOS004478597377"
        }
    """
    data = request.get_json()
    try:
        otp = data["otp"]
        reqId = data["reqId"]
        saved_response = local_session[reqId]
        saved_response["otp"] = otp
        # response = session.post(post_url, json=saved_response, proxies=proxy)
        response = session.post(post_url, json=saved_response)
        return response.json()
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/saveEntity", methods=["post"])
def saveEntity():
    session = requests.Session()
    post_url = "https://eportal.incometax.gov.in/iec/guestservicesapi/saveEntity/"
    """
    {
        "panNumber": "ABCDEF1234A",
        "fullName": "ABCD XYZ",
        "dob": "1993-07-02",
        "mobNo": "9999999999",
        "areaCd": "91",
        "serviceName": "verifyYourPanService",
        "formName": "FO-009-VYPAN"
    }
    """
    request_data = request.get_json()
    request_data["fullName"] = encode_base64(request_data["fullName"])
    try:
        response = session.post(post_url, json=request_data, proxies=proxy)
        response_data = response.json()
        pprint.pprint(response_data)
        # Check if reqId is present in response
        if "reqId" not in response_data:
            # Look for error message
            if "messages" in response_data:
                # loop through messages
                for message in response_data["messages"]:
                    # Check if message is of type error
                    if message["type"] == "ERROR":
                        return jsonify({"error": message["desc"]})
            return jsonify({"error": "Something went wrong"})
        reqId = response_data["reqId"]
        request_data["reqId"] = reqId
        local_session["reqId"] = request_data
        return response_data
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
