from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from threading import Lock
import logging
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SignalingData:
    def __init__(self):
        self.lock = Lock()
        self.offer = None
        self.answer = None
        self.unity_ice_candidates = []
        self.browser_ice_candidates = []
        self.connection_attempts = 0
        self.last_activity = datetime.now()

signaling_data = SignalingData()

@app.route("/send")
def index():
    return render_template("sender.html")

@app.route("/rec", methods=['GET'])
def index2():
    return render_template("reciver.html")

@app.route('/offer', methods=['POST', 'GET'])
def handle_offer():
    if request.method == 'POST':
            data = request.get_json()
            logger.info(f"📨 recived offer from unity {data}")
            with signaling_data.lock:
                signaling_data.offer = data
            return jsonify(data)
    
    else:
        with signaling_data.lock:
            offer = signaling_data.offer
        if offer:
            logger.info(f"📤 Sending offer to browser ")
            return jsonify(offer)
    return jsonify()

@app.route('/answer', methods=['POST', 'GET'])
def handle_answer():
    if request.method == 'POST':
        data = request.get_json()
        logger.info(f"📨 Received ANSWER from Browser {data}")
        with signaling_data.lock:
            signaling_data.answer = data

    else:
        with signaling_data.lock:
            answer = signaling_data.answer
        if answer:
            logger.info(f"📤 Sending answer to Unity ")
            return jsonify(answer)
    return jsonify()

@app.route('/icebrowser', methods=['POST', 'GET'])
def handle_ice_browser():

    if request.method == 'POST':
        data = request.get_json()
        logger.info(f"📨 Received ICE from Browser {data}")
        with signaling_data.lock:
            signaling_data.browser_ice_candidates.append(data)

    else:
        with signaling_data.lock:
            ICE = signaling_data.unity_ice_candidates
        if ICE:
            logger.info(f"📤 Sending Unity ICE to Browser {ICE}")
            return jsonify(ICE)
    return jsonify()

@app.route('/iceunity', methods=['POST', 'GET'])
def handle_ice_unity():

    if request.method == 'POST':
        data = request.get_json()
        logger.info(f"📨 Received ICE from Unity {data}")
        with signaling_data.lock:
            signaling_data.unity_ice_candidates.append(data)

    else:
        with signaling_data.lock:
            ICE = signaling_data.browser_ice_candidates
        if ICE:
            logger.info(f"📤 Sending Browser ICE to Unity")
            return jsonify(ICE)
    return jsonify()




#ngrok authtoken 30mzsGdp4CSnbX2sOTw7tAetFMu_2qJBRLhkBWoJMRBYuAbh5
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok", 
        "service": "webrtc-signaling-server",
        "uptime": str(datetime.now() - signaling_data.last_activity)
    })


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    print("seder on https://192.168.1.64:5000/send")
    print("reciver on https://192.168.1.64:5000/rec")
    
    app.run(
        ssl_context=("cert.pem", "key.pem"),
        host='0.0.0.0', 
        port=5000, 
        debug=True, 
        use_reloader=False
    )
{
    "mid": "0",
    "direction": "recvonly",
    "receiver": "video",
    "sender": "none"
}
#есть подключение есть гироданные нет стрима видео в ком проблема ice/sdp тоже вроде правильные
#
#📨 recived offer from unity {'sdp': 'v=0\r\no=- 6989740719171059860 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0 1\r\na=extmap-allow-mixed\r\na=msid-semantic: WMS\r\nm=video 9 UDP/TLS/RTP/SAVPF 127 122 125 121 124 120 39 40 119 118 123\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:AKhk\r\na=ice-pwd:UiX7daUSeGMHOTGcN2a4MYJY\r\na=ice-options:trickle\r\na=fingerprint:sha-256 55:1F:98:1E:E4:82:76:08:51:3F:62:8E:58:A1:75:BF:46:ED:79:FF:71:A0:8C:9C:4B:0D:46:0C:BD:EE:78:56\r\na=setup:actpass\r\na=mid:0\r\na=extmap:1 urn:ietf:params:rtp-hdrext:toffset\r\na=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time\r\na=extmap:3 urn:3gpp:video-orientation\r\na=extmap:4 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=extmap:5 http://www.webrtc.org/experiments/rtp-hdrext/playout-delay\r\na=extmap:6 http://www.webrtc.org/experiments/rtp-hdrext/video-content-type\r\na=extmap:7 http://www.webrtc.org/experiments/rtp-hdrext/video-timing\r\na=extmap:8 http://www.webrtc.org/experiments/rtp-hdrext/color-space\r\na=extmap:9 urn:ietf:params:rtp-hdrext:sdes:mid\r\na=extmap:10 urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id\r\na=extmap:11 urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id\r\na=sendrecv\r\na=msid:- a17679f6-9fa8-49dd-9509-ab9572f932e7\r\na=rtcp-mux\r\na=rtcp-rsize\r\na=rtpmap:127 VP8/90000\r\na=rtcp-fb:127 goog-remb\r\na=rtcp-fb:127 transport-cc\r\na=rtcp-fb:127 ccm fir\r\na=rtcp-fb:127 nack\r\na=rtcp-fb:127 nack pli\r\na=fmtp:127 implementation_name=Internal\r\na=rtpmap:122 rtx/90000\r\na=fmtp:122 apt=127\r\na=rtpmap:125 VP9/90000\r\na=rtcp-fb:125 goog-remb\r\na=rtcp-fb:125 transport-cc\r\na=rtcp-fb:125 ccm fir\r\na=rtcp-fb:125 nack\r\na=rtcp-fb:125 nack pli\r\na=fmtp:125 implementation_name=Internal;profile-id=0\r\na=rtpmap:121 rtx/90000\r\na=fmtp:121 apt=125\r\na=rtpmap:124 VP9/90000\r\na=rtcp-fb:124 goog-remb\r\na=rtcp-fb:124 transport-cc\r\na=rtcp-fb:124 ccm fir\r\na=rtcp-fb:124 nack\r\na=rtcp-fb:124 nack pli\r\na=fmtp:124 implementation_name=Internal;profile-id=2\r\na=rtpmap:120 rtx/90000\r\na=fmtp:120 apt=124\r\na=rtpmap:39 AV1/90000\r\na=rtcp-fb:39 goog-remb\r\na=rtcp-fb:39 transport-cc\r\na=rtcp-fb:39 ccm fir\r\na=rtcp-fb:39 nack\r\na=rtcp-fb:39 nack pli\r\na=fmtp:39 implementation_name=Internal\r\na=rtpmap:40 rtx/90000\r\na=fmtp:40 apt=39\r\na=rtpmap:119 red/90000\r\na=rtpmap:118 rtx/90000\r\na=fmtp:118 
#apt=119\r\na=rtpmap:123 ulpfec/90000\r\na=ssrc-group:FID 3453960567 3537388881\r\na=ssrc:3453960567 cname:le4oH7At2uzBqvey\r\na=ssrc:3453960567 msid:- a17679f6-9fa8-49dd-9509-ab9572f932e7\r\na=ssrc:3537388881 cname:le4oH7At2uzBqvey\r\na=ssrc:3537388881 msid:- a17679f6-9fa8-49dd-9509-ab9572f932e7\r\nm=application 9 UDP/DTLS/SCTP webrtc-datachannel\r\nc=IN IP4 0.0.0.0\r\na=ice-ufrag:AKhk\r\na=ice-pwd:UiX7daUSeGMHOTGcN2a4MYJY\r\na=ice-options:trickle\r\na=fingerprint:sha-256 55:1F:98:1E:E4:82:76:08:51:3F:62:8E:58:A1:75:BF:46:ED:79:FF:71:A0:8C:9C:4B:0D:46:0C:BD:EE:78:56\r\na=setup:actpass\r\na=mid:1\r\na=sctp-port:5000\r\na=max-message-size:262144\r\n', 'type': 'offer'}
#
#
#📨 Received ANSWER from Browser {'sdp': 'v=0\r\no=- 2749134460082846224 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0 1\r\na=extmap-allow-mixed\r\na=msid-semantic: WMS\r\nm=video 9 UDP/TLS/RTP/SAVPF 127 122 125 121 124 120 39 40 119 118 123\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:UbIF\r\na=ice-pwd:8JY3XhZIecUbCvjU3vz77FKk\r\na=ice-options:trickle\r\na=fingerprint:sha-256 DE:D3:8D:9D:B3:37:65:C0:1E:26:F6:D3:0B:93:42:09:C8:F0:AB:08:6C:39:21:8F:B5:9C:CB:20:9B:80:34:49\r\na=setup:active\r\na=mid:0\r\na=extmap:1 urn:ietf:params:rtp-hdrext:toffset\r\na=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time\r\na=extmap:3 urn:3gpp:video-orientation\r\na=extmap:4 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=extmap:5 http://www.webrtc.org/experiments/rtp-hdrext/playout-delay\r\na=extmap:6 http://www.webrtc.org/experiments/rtp-hdrext/video-content-type\r\na=extmap:7 http://www.webrtc.org/experiments/rtp-hdrext/video-timing\r\na=extmap:8 http://www.webrtc.org/experiments/rtp-hdrext/color-space\r\na=extmap:9 urn:ietf:params:rtp-hdrext:sdes:mid\r\na=extmap:10 urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id\r\na=extmap:11 urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id\r\na=recvonly\r\na=msid:- browser_video_stream\r\na=rtcp-mux\r\na=rtcp-rsize\r\na=rtpmap:127 VP8/90000\r\na=rtcp-fb:127 goog-remb\r\na=rtcp-fb:127 transport-cc\r\na=rtcp-fb:127 ccm fir\r\na=rtcp-fb:127 nack\r\na=rtcp-fb:127 nack pli\r\na=rtpmap:122 rtx/90000\r\na=fmtp:122 apt=127\r\na=rtpmap:125 VP9/90000\r\na=rtcp-fb:125 goog-remb\r\na=rtcp-fb:125 transport-cc\r\na=rtcp-fb:125 ccm fir\r\na=rtcp-fb:125 nack\r\na=rtcp-fb:125 nack pli\r\na=fmtp:125 profile-id=0\r\na=rtpmap:121 rtx/90000\r\na=fmtp:121 apt=125\r\na=rtpmap:124 VP9/90000\r\na=rtcp-fb:124 goog-remb\r\na=rtcp-fb:124 transport-cc\r\na=rtcp-fb:124 ccm fir\r\na=rtcp-fb:124 nack\r\na=rtcp-fb:124 nack pli\r\na=fmtp:124 profile-id=2\r\na=rtpmap:120 rtx/90000\r\na=fmtp:120 apt=124\r\na=rtpmap:39 AV1/90000\r\na=rtcp-fb:39 goog-remb\r\na=rtcp-fb:39 transport-cc\r\na=rtcp-fb:39 ccm fir\r\na=rtcp-fb:39 nack\r\na=rtcp-fb:39 nack pli\r\na=fmtp:39 level-idx=5;profile=0;tier=0\r\na=rtpmap:40 rtx/90000\r\na=fmtp:40 apt=39\r\na=rtpmap:119 red/90000\r\na=rtpmap:118 rtx/90000\r\na=fmtp:118 apt=119\r\na=rtpmap:123 ulpfec/90000\r\nm=application 9 UDP/DTLS/SCTP webrtc-datachannel\r\nc=IN IP4 0.0.0.0\r\na=ice-ufrag:UbIF\r\na=ice-pwd:8JY3XhZIecUbCvjU3vz77FKk\r\na=ice-options:trickle\r\na=fingerprint:sha-256 DE:D3:8D:9D:B3:37:65:C0:1E:26:F6:D3:0B:93:42:09:C8:F0:AB:08:6C:39:21:8F:B5:9C:CB:20:9B:80:34:49\r\na=setup:active\r\na=mid:1\r\na=sctp-port:5000\r\na=max-message-size:262144\r\n', 'type': 'answer'}
#
#
# 📨 Received ICE from Unity {'session_id': 'default', 'candidate': {'candidate': 'candidate:2749004217 1 udp 1686052607 92.222.100.35 19968 typ srflx raddr 10.255.0.1 rport 62983 generation 0 ufrag AKhk 
#network-id 1 network-cost 50', 'sdpMid': '0', 'sdpMLineIndex': 0}}
#
#
#
#📨 Received ICE from Browser {'type': 'candidate', 'candidate': {'candidate': 'candidate:3220454506 1 udp 1677729535 92.222.100.35 35709 typ srflx raddr 0.0.0.0 rport 0 generation 0 ufrag UbIF network-cost 999', 'sdpMid': '0', 'sdpMLineIndex': 0}}



#📤 Sending Unity ICE to Browser {'session_id': 'default', 'candidate': {'candidate': 'candidate:2264705725 1 udp 1677729535 162.19.19.241 57717 typ srflx raddr 0.0.0.0 rport 0 generation 0 ufrag mZOT network-cost 999', 'sdpMid': '0', 'sdpMLineIndex': 0}}
# 📨 Received ICE from Browser {'type': 'candidate', 'candidate': {'candidate': 'candidate:1728927781 1 udp 2122260223 192.168.1.54 46392 typ host generation 0 ufrag QSU/ network-id 1 network-cost 10', 'sdpMid': '0', 'sdpMLineIndex': 0, 'usernameFragment': 'QSU/'}}