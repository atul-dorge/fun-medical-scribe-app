let mediaRecorder;
let audioChunks = [];

document.getElementById("startBtn").onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    audioChunks = [];
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append("file", blob, "recording.wav");

        document.getElementById("status").textContent = "Uploading and transcribing...";

        const response = await fetch("/upload/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        document.getElementById("status").textContent = "Done!";
        document.getElementById("output").textContent = data.soap_note;
    };

    mediaRecorder.start();
    document.getElementById("startBtn").disabled = true;
    document.getElementById("stopBtn").disabled = false;
};

document.getElementById("stopBtn").onclick = () => {
    mediaRecorder.stop();
    document.getElementById("startBtn").disabled = false;
    document.getElementById("stopBtn").disabled = true;
};
