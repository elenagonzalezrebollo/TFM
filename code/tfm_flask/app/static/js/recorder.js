document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file-input");
  const recordMicBtn = document.getElementById("record-mic-btn");
  const recordSystemMicBtn = document.getElementById("record-system-btn");
  const stopRecordBtn = document.getElementById("stop-record-btn");
  const prog = document.getElementById("prog");
  const recordingControls = document.getElementById("recording-controls");
  const recordButtonsContainer = document.getElementById("record-buttons-container");

  let mediaRecorder;
  let recordedChunks = [];
  let activeStream;

  function updateUIAfterRecording() {
    recordMicBtn.disabled = false;
    recordSystemMicBtn.disabled = false;
    if (recordingControls) recordingControls.style.display = "none";
    if (recordButtonsContainer) recordButtonsContainer.style.display = "block";
    if (prog) prog.style.display = "none";
    if (activeStream) {
      activeStream.getTracks().forEach(track => track.stop());
      activeStream = null;
    }
    recordedChunks = [];
    mediaRecorder = null;
  }

  function startRecording(stream, type) {
    if (!stream || stream.getAudioTracks().length === 0) {
      alert("No se pudo obtener una pista de audio para grabar");
      console.error("No se encontro la pista de audio");
      updateUIAfterRecording();
      return;
    }

    recordMicBtn.disabled = true;
    recordSystemMicBtn.disabled = true;
    if (recordingControls) recordingControls.style.display = "block";
    if (recordButtonsContainer) recordButtonsContainer.style.display = "none"; 

    activeStream = stream; 

    const options = { mimeType: "audio/webm" };
    try {
      mediaRecorder = new MediaRecorder(stream, options);
    } catch (e) {
      console.error("Error al crear el MediaRecorder:", e);
      alert("Error al iniciar la grabadora: " + e.message);
      updateUIAfterRecording();
      return;
    }

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(recordedChunks, { type: "audio/webm" });
      const fileName = `recording_${new Date().toISOString().replace(/[:.]/g, "-")}.webm`;
      const formData = new FormData();
      formData.append("file", blob, fileName);
      formData.append("source", type); 

      console.log(`Cargando ${type} grabación...`);
      
      if (window.showMainLoader) window.showMainLoader();
      await upload(formData);
      updateUIAfterRecording();
    };

    mediaRecorder.onerror = (event) => {
      console.error("MediaRecorder error:", event.error);
      alert("Error durante la grabación: " + event.error.name + " - " + event.error.message);
      if (window.hideMainLoader) window.hideMainLoader();
      updateUIAfterRecording();
    };

    recordedChunks = [];
    mediaRecorder.start();
    console.log(`Grabando ${type}.`);
  }

  if (stopRecordBtn) {
    stopRecordBtn.addEventListener("click", () => {
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        console.log("Grabación parada");
      } else {
        console.log("Tratando parar la grabación sin pista de audio");
      }
    });
  }

  if (recordMicBtn) {
    recordMicBtn.addEventListener("click", async () => {
      console.log("Record Mic button clickeado");
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("La API getUserMedia no está disponible en este navegador.");
        return;
      }
      try {
        const micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        startRecording(micStream, "microphone");
      } catch (err) {
        console.error("Error al acceder al microfono:", err);
        alert("Error al acceder al micrófono: " + err.message);
        updateUIAfterRecording();
      }
    });
  }

  if (recordSystemMicBtn) {
    recordSystemMicBtn.addEventListener("click", async () => {
      console.log("Record Mic + System button clickeado");
      if (!navigator.mediaDevices || typeof navigator.mediaDevices.getDisplayMedia !== 'function') {
        alert("La API para grabar pantalla (getDisplayMedia) no está disponible en este navegador o la página no se sirve sobre HTTPS/localhost.");
        return;
      }
      try {
        const displayStream = await navigator.mediaDevices.getDisplayMedia({ audio: true, video: true });
        const micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });

        const audioContext = new AudioContext();
        const combinedDest = audioContext.createMediaStreamDestination();
        let hasAudio = false;

        if (displayStream.getAudioTracks().length > 0) {
          const displaySource = audioContext.createMediaStreamSource(displayStream);
          displaySource.connect(combinedDest);
          hasAudio = true;
        }
        if (micStream.getAudioTracks().length > 0) {
          const micSource = audioContext.createMediaStreamSource(micStream);
          micSource.connect(combinedDest);
          hasAudio = true;
        }

        if (!hasAudio) {
          alert("No se detectaron pistas de audio ni del sistema ni del micrófono.");
          displayStream.getTracks().forEach(track => track.stop());
          micStream.getTracks().forEach(track => track.stop());
          updateUIAfterRecording();
          return;
        }
        
        const combinedAudioStream = combinedDest.stream;
        
        const finalStreamForRecorder = new MediaStream();
        combinedAudioStream.getAudioTracks().forEach(track => finalStreamForRecorder.addTrack(track));
        
        const originalStreams = [displayStream, micStream];
        const oldUpdateUIAfterRecording = updateUIAfterRecording;
        const newUpdateUIAfterRecording = () => {
            originalStreams.forEach(s => s.getTracks().forEach(t => t.stop()));
            oldUpdateUIAfterRecording(); 
        };
        
        const tempUpdateFunction = updateUIAfterRecording; 
        updateUIAfterRecording = newUpdateUIAfterRecording; 

        startRecording(finalStreamForRecorder, "system-mic");
        

      } catch (err) {
        console.error("Error accessing screen/microfono:", err);
        alert("Error al acceder a la pantalla o al micrófono: " + err.message + ". Asegúrate de conceder los permisos necesarios.");
        if (window.hideMainLoader) window.hideMainLoader();
        updateUIAfterRecording(); 
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append("file", file, file.name);
      formData.append("source", "file-upload");
      if (window.showMainLoader) window.showMainLoader();
      upload(formData);
    });
  }

  async function upload(payload, isJson = false) {
    if (prog) { prog.style.display = "block"; prog.value = 0; }

    if (window.showMainLoader) window.showMainLoader();

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    const headers = {};
    if (csrfToken) { headers["X-CSRFToken"] = csrfToken; }

    const opts = isJson
      ? { method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: payload }
      : { method: "POST", headers: headers, body: payload };
    try {
      console.log("Cargando ...");
      const res = await fetch(UPLOAD_URL, opts); 
      const data = await res.json();
      if (res.ok && data.ok) {
        console.log("Carga satisfactoria, history ID:", data.history_id);
        window.location.href = `/history/${data.history_id}`; 
      } else {
        console.error("Carga fallida:", data);
        alert(`Error: ${data.error || "Carga fallida"}`);
        if (window.hideMainLoader) window.hideMainLoader();
      }
    } catch (err) {
      console.error("Error en la subida:", err);
      alert(`Error: ${err.message || "Error en la subida"}`);
      if (window.hideMainLoader) window.hideMainLoader();
    } finally {
      if (prog) { prog.style.display = "none"; }
      updateUIAfterRecording(); 
    }
  }
});
