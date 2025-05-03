let mediaRecorder;
let audioChunks = [];
let isRecording = false;
const CHUNK_SIZE_THRESHOLD = 0.5 * 1024; // 1 MB, adjust as needed

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const status = document.getElementById('status');
const output = document.getElementById('output');

startBtn.onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    isRecording = true;

    mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
            audioChunks.push(event.data);

            // Calculate total size of audioChunks
            const totalSize = audioChunks.reduce((sum, chunk) => sum + chunk.size, 0);

            if (totalSize >= CHUNK_SIZE_THRESHOLD) {
                // Send current chunks to backend
                await sendAudioChunks(audioChunks);
                // Clear the array for new chunks
                audioChunks = [];
            }
        }
    };

    mediaRecorder.onstop = async () => {
        isRecording = false;
        // Send any remaining audio chunks
        if (audioChunks.length > 0) {
            await sendAudioChunks(audioChunks);
            audioChunks = [];
        }
        status.textContent = "Recording stopped.";
    };

    mediaRecorder.start(500); // Collect data every 500ms (adjust as needed)
    status.textContent = "Recording...";
    startBtn.disabled = true;
    stopBtn.disabled = false;
};

stopBtn.onclick = () => {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
};

async function sendAudioChunks(chunks) {
    status.textContent = "Uploading...";
    const blob = new Blob(chunks, { type: 'audio/webm' }); // or 'audio/wav' depending on your backend
    const formData = new FormData();
    formData.append('file', blob, 'audio.webm');

    try {
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        output.textContent += data.soap_note + "\n";
        status.textContent = "Recording...";
    } catch (err) {
        status.textContent = "Upload failed!";
        console.error(err);
    }
}