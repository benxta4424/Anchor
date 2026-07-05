import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import EmergencyPopup from './EmergencyPopup';

// SVG Icons
const MicIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" x2="12" y1="19" y2="22" />
  </svg>
);

const StopIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <rect x="4" y="4" width="16" height="16" rx="2" />
  </svg>
);

const PlayIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <polygon points="6 3 20 12 6 21 6 3" />
  </svg>
);

const PauseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <rect x="14" y="4" width="4" height="16" rx="1" />
    <rect x="6" y="4" width="4" height="16" rx="1" />
  </svg>
);

const ChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <line x1="18" x2="18" y1="20" y2="10" />
    <line x1="12" x2="12" y1="20" y2="4" />
    <line x1="6" x2="6" y1="20" y2="14" />
  </svg>
);

const ChatIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const TrendUpIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon inline-icon error-text">
    <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
    <polyline points="16 7 22 7 22 13" />
  </svg>
);

const TrendDownIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon inline-icon success-text">
    <polyline points="22 17 13.5 8.5 8.5 13.5 2 7" />
    <polyline points="16 17 22 17 22 11" />
  </svg>
);

const TrendConstantIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon inline-icon">
    <line x1="5" x2="19" y1="12" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

const CalendarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" x2="16" y1="2" y2="6" />
    <line x1="8" x2="8" y1="2" y2="6" />
    <line x1="3" x2="21" y1="10" y2="10" />
  </svg>
);

const LightbulbIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5 5 0 0 0 8 8c0 1 .3 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
    <line x1="9" x2="15" y1="18" y2="18" />
    <line x1="10" x2="14" y1="22" y2="22" />
  </svg>
);

const WarningIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon inline-icon error-text">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
    <line x1="12" x2="12" y1="9" y2="13" />
    <line x1="12" x2="12.01" y1="17" y2="17" />
  </svg>
);

const InfoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon inline-icon info-text">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" x2="12" y1="16" y2="12" />
    <line x1="12" x2="12.01" y1="8" y2="8" />
  </svg>
);

const CheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon inline-icon success-text">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const CrossIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <line x1="18" x2="6" y1="6" y2="18" />
    <line x1="6" x2="18" y1="6" y2="18" />
  </svg>
);

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon btn-svg-icon">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" x2="12" y1="3" y2="15" />
  </svg>
);

const DeleteIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    <line x1="10" x2="10" y1="11" y2="17" />
    <line x1="14" x2="14" y1="11" y2="17" />
  </svg>
);

// WAV Encoders
const writeString = (view, offset, string) => {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
};

const floatTo16BitPCM = (output, offset, input) => {
  for (let i = 0; i < input.length; i++, offset += 2) {
    let s = Math.max(-1, Math.min(1, input[i]));
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
};

const encodeWAV = (samples, sampleRate) => {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, 'data');
  view.setUint32(40, samples.length * 2, true);

  floatTo16BitPCM(view, 44, samples);

  return new Blob([view], { type: 'audio/wav' });
};

const EnhancedVoiceComponent = ({ chatId }) => {
  const [currentChatId, setCurrentChatId] = useState(() => {
    const storedChatId = localStorage.getItem("activeChatId");
    const parsedChatId = storedChatId ? parseInt(storedChatId, 10) : null;
    return (parsedChatId && !isNaN(parsedChatId)) ? parsedChatId : (chatId || 1);
  });

  const [chatName, setChatName] = useState("");
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [voiceHistory, setVoiceHistory] = useState([]);
  const [voiceStats, setVoiceStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentPlayingId, setCurrentPlayingId] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [toast, setToast] = useState({ show: false, type: 'success', message: '' });
  const [showEmergencyPopup, setShowEmergencyPopup] = useState(false);
  const [criticalScore, setCriticalScore] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [isClinicalMode] = useState(true);

  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [pendingAudio, setPendingAudio] = useState(null);

  const scriptProcessorRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const voiceChunksRef = useRef([]);
  const recordingIntervalRef = useRef(null);
  const canvasRef = useRef(null);
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const fileInputRef = useRef(null);

  // Sync currentChatId with localStorage activeChatId updates
  useEffect(() => {
    const handleChatsUpdated = () => {
      const storedChatId = localStorage.getItem("activeChatId");
      const parsedChatId = storedChatId ? parseInt(storedChatId, 10) : null;
      const nextChatId = (parsedChatId && !isNaN(parsedChatId)) ? parsedChatId : (chatId || 1);
      setCurrentChatId(nextChatId);
    };

    window.addEventListener("chats-updated", handleChatsUpdated);
    return () => window.removeEventListener("chats-updated", handleChatsUpdated);
  }, [chatId]);

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
        audioCtxRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (currentChatId) {
      // Clear previous analysis session states when switching chats
      setAnalysisResult(null);
      setRecordedAudio(null);
      setUploadedFileName('');

      loadVoiceHistory();
      loadVoiceStats();
      loadDashboardStats();

      const fetchChatName = async () => {
        try {
          const response = await fetch("http://localhost:5000/get-chats");
          const data = await response.json();
          const active = data.find(c => c.id === currentChatId);
          if (active) {
            setChatName(active.nume_persoana);
          } else {
            setChatName(`Sesiune #${currentChatId}`);
          }
        } catch (error) {
          console.error("Error fetching chat name:", error);
          setChatName(`Sesiune #${currentChatId}`);
        }
      };
      fetchChatName();
    }
  }, [currentChatId]);

  useEffect(() => {
    const handleSyncStats = () => {
      loadDashboardStats();
    };
    window.addEventListener("chats-updated", handleSyncStats);
    return () => window.removeEventListener("chats-updated", handleSyncStats);
  }, [currentChatId]);

  const triggerToast = (type, message) => {
    setToast({ show: true, type, message });
    setTimeout(() => {
      setToast({ show: false, type: 'success', message: '' });
    }, 4000);
  };

  const loadVoiceHistory = async () => {
    try {
      const response = await fetch(`http://localhost:5000/get-voice-history/${currentChatId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setVoiceHistory(data.history || []);
      }
    } catch (error) {
      console.error('Error loading voice history:', error);
    }
  };

  const loadVoiceStats = async () => {
    try {
      const response = await fetch(`http://localhost:5000/get-voice-stats/${currentChatId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setVoiceStats(data.stats);
      }
    } catch (error) {
      console.error('Error loading voice stats:', error);
    }
  };

  const deleteVoiceHistory = async () => {
    if (window.confirm("Sigur dorești să ștergi tot istoricul înregistrărilor vocale? Această acțiune este ireversibilă.")) {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/delete-voice-history/${currentChatId}`, {
          method: 'DELETE'
        });
        const data = await response.json();
        if (data.status === 'success') {
          triggerToast('success', 'Istoricul înregistrărilor vocale a fost șters cu succes.');
          setAnalysisResult(null);
          setVoiceHistory([]);
          setVoiceStats(null);
          // Notify other components (like MiniDashboard) of state change
          window.dispatchEvent(new Event("chats-updated"));
        } else {
          triggerToast('error', 'Ștergerea a eșuat: ' + data.error);
        }
      } catch (error) {
        triggerToast('error', 'Eroare la ștergerea istoricului: ' + error.message);
      } finally {
        setLoading(false);
      }
    }
  };

  // Start recording using Web Audio API and ScriptProcessorNode for true mono PCM WAV
  const startRecording = async () => {
    try {
      setUploadedFileName('');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      setRecordingTime(0);

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioCtxRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);

      // Web Audio API hooks for Visualizer
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      // ScriptProcessorNode mono buffer recording (buffer size 4096)
      const bufferSize = 4096;
      const scriptProcessor = audioContext.createScriptProcessor(bufferSize, 1, 1);
      source.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);
      scriptProcessorRef.current = scriptProcessor;

      voiceChunksRef.current = [];

      scriptProcessor.onaudioprocess = (event) => {
        const inputBuffer = event.inputBuffer.getChannelData(0);
        voiceChunksRef.current.push(new Float32Array(inputBuffer));
      };

      setIsRecording(true);

      // Let component mount the canvas first, then start loop
      setTimeout(() => {
        drawLiveWaveform();
      }, 100);

      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      triggerToast('error', 'Acces microfon refuzat: ' + error.message);
    }
  };

  const drawLiveWaveform = () => {
    if (!canvasRef.current || !analyserRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!canvasRef.current || !analyserRef.current) return;
      animationFrameRef.current = requestAnimationFrame(draw);
      analyserRef.current.getByteTimeDomainData(dataArray);

      // Dynamic color query
      const computedStyle = getComputedStyle(document.documentElement);
      const primaryColor = computedStyle.getPropertyValue('--primary').trim() || 'hsl(260, 60%, 62%)';

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.lineWidth = 3;
      ctx.strokeStyle = primaryColor;
      ctx.beginPath();

      const sliceWidth = canvas.width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };
    draw();
  };

  // Stop recording, close context, and compile WAV
  const stopRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      clearInterval(recordingIntervalRef.current);

      if (scriptProcessorRef.current) {
        scriptProcessorRef.current.disconnect();
        scriptProcessorRef.current.onaudioprocess = null;
        scriptProcessorRef.current = null;
      }

      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      const sampleRate = audioCtxRef.current ? audioCtxRef.current.sampleRate : 44100;

      if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
        audioCtxRef.current.close();
      }
      audioCtxRef.current = null;
      analyserRef.current = null;

      // Concatenate Float32Array chunks
      const chunks = voiceChunksRef.current;
      let totalLength = 0;
      for (let i = 0; i < chunks.length; i++) {
        totalLength += chunks[i].length;
      }
      const mergedSamples = new Float32Array(totalLength);
      let offset = 0;
      for (let i = 0; i < chunks.length; i++) {
        mergedSamples.set(chunks[i], offset);
        offset += chunks[i].length;
      }

      // Encode to WAV
      const audioBlob = encodeWAV(mergedSamples, sampleRate);
      const audioUrl = URL.createObjectURL(audioBlob);
      setPendingAudio({ blob: audioBlob, url: audioUrl, isUpload: false });
      setShowConfirmModal(true);
      triggerToast('info', 'Înregistrare finalizată. Confirmă trimiterea pentru analiză.');
    }
  };

  const loadDashboardStats = async () => {
    if (!currentChatId) return;
    try {
      const response = await fetch(`http://localhost:5000/get-multimodal-stats/${currentChatId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          setDashboardStats(data.stats);
        }
      }
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  };

  // Analyze audio using reader.readAsDataURL for base64 (avoids stack limits)
  const analyzeVoice = async (audioBlob = null) => {
    const targetBlob = audioBlob || recordedAudio?.blob;
    if (!targetBlob) {
      triggerToast('error', 'Înregistrarea nu este disponibilă.');
      return;
    }

    setLoading(true);
    try {
      const base64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const dataUrl = reader.result;
          resolve(dataUrl.split(',')[1]);
        };
        reader.onerror = reject;
        reader.readAsDataURL(targetBlob);
      });

      const response = await fetch('http://localhost:5000/analyze-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio: base64,
          chat_id: currentChatId,
          language: 'auto',
          trigger_diagnosis: 'true'
        }),
      });

      const result = await response.json();
      if (result.status === 'success') {
        setAnalysisResult(result);
        triggerToast('success', 'Analiza vocală a fost finalizată!');
        
        const combinedScore = result.combined_analysis?.voice_depression_indicator || result.voice_analysis?.overall_voice_indicator || 0;
        if (combinedScore >= 80 || (result.text_analysis && result.text_analysis.score >= 80)) {
          setCriticalScore(Math.max(combinedScore, result.text_analysis?.score || 0));
          setShowEmergencyPopup(true);
        }
        
        await loadVoiceHistory();
        await loadVoiceStats();
        await loadDashboardStats();
        // Notify other components of state change
        window.dispatchEvent(new Event("chats-updated"));
      } else {
        triggerToast('error', 'Analiză eșuată: ' + result.error);
      }
    } catch (error) {
      triggerToast('error', 'Eroare: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Play audio
  const playAudio = (audioUrl, id) => {
    if (currentPlayingId === id) {
      setCurrentPlayingId(null);
    } else {
      const audio = new Audio(audioUrl);
      audio.play();
      setCurrentPlayingId(id);
      audio.onended = () => setCurrentPlayingId(null);
    }
  };

  // Upload audio file
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      const audioUrl = URL.createObjectURL(file);
      setPendingAudio({ blob: file, url: audioUrl, isUpload: true, name: file.name });
      setUploadedFileName(file.name);
      setShowConfirmModal(true);
      triggerToast('info', 'Fișier audio încărcat. Confirmă trimiterea pentru analiză.');
    } else {
      triggerToast('error', 'Vă rugăm selectați un fișier audio valid.');
    }
  };

  const confirmAudioAnalysis = () => {
    if (pendingAudio) {
      console.log('[Operation] User confirmed audio submission');
      setRecordedAudio({ blob: pendingAudio.blob, url: pendingAudio.url });
      if (pendingAudio.isUpload) {
        setUploadedFileName(pendingAudio.name);
      } else {
        setUploadedFileName('');
      }
      setShowConfirmModal(false);
      analyzeVoice(pendingAudio.blob);
      setPendingAudio(null);
    }
  };

  const cancelAudioAnalysis = () => {
    console.log('[Operation] User cancelled audio submission');
    setShowConfirmModal(false);
    setPendingAudio(null);
    setUploadedFileName('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    triggerToast('info', 'Fișierul/Înregistrarea audio a fost anulată.');
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="voice-container enhanced-voice">
      <div className="voice-header">
        <h2><MicIcon /> Analiză Vocală Avansată {chatName && ` - ${chatName}`}</h2>
        <p>Înregistrează sau încarcă fișiere audio pentru analiza semnelor de depresie vocală</p>
      </div>

      {/* Definiție Gradient pentru Inelul de Progres Circular */}
      <svg width="0" height="0" style={{ position: 'absolute' }}>
        <defs>
          <linearGradient id="ec-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#ffb347" />
            <stop offset="100%" stopColor="#ff6b6b" />
          </linearGradient>
        </defs>
      </svg>

      {/* Card Diagnoză Context Vocal Extins — mereu vizibil */}
      <div className="ec-diag-card-container">
        <div className="ec-diag-card" style={{
          background: 'linear-gradient(135deg, rgba(30, 30, 47, 0.6) 0%, rgba(21, 21, 34, 0.6) 100%)',
          border: '1px solid rgba(168, 85, 247, 0.15)',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.25), inset 0 0 15px rgba(168, 85, 247, 0.05)',
          borderRadius: '16px',
          padding: '16px 20px'
        }}>
          <div className="ec-diag-left-section">
            <div 
              className="ec-diag-circle-container" 
              onClick={() => setShowReportModal(true)} 
              style={{ cursor: 'pointer' }}
            >
              <svg className="ec-diag-progress-svg" viewBox="0 0 100 100">
                <circle className="ec-diag-progress-bg" cx="50" cy="50" r="42" stroke="rgba(255,255,255,0.03)" strokeWidth="6" />
                <circle 
                  className="ec-diag-progress-bar" 
                  cx="50" 
                  cy="50" 
                  r="42" 
                  style={{
                    strokeDasharray: `${2 * Math.PI * 42}`,
                    strokeDashoffset: `${2 * Math.PI * 42 * (1 - (dashboardStats ? dashboardStats.voice_average : 0) / 100)}`,
                    stroke: 'url(#ec-grad)',
                    strokeWidth: '6',
                    strokeLinecap: 'round'
                  }}
                />
              </svg>
              <div className="ec-diag-score-value" style={{ fontWeight: '800', color: '#fff' }}>
                {dashboardStats ? `${Math.round(dashboardStats.voice_average)}%` : '0%'}
              </div>
            </div>
            <div className="ec-diag-card-info">
              <h4 className="ec-diag-card-title" style={{ color: '#bb9af7', fontWeight: '700', fontSize: '14px' }}>Context Vocal Extins</h4>
              <p className="ec-diag-card-desc" style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                Nivel de alertă determinat din istoricul evoluției tonalității și acusticii vocale.
              </p>
            </div>
          </div>
          
          <div className="ec-diag-actions">
            <button className="ec-diag-btn" onClick={() => setShowReportModal(true)} style={{
              background: 'linear-gradient(135deg, #bb9af7, #7aa2f7)',
              boxShadow: '0 4px 12px rgba(187, 154, 247, 0.25)',
              fontWeight: '600'
            }}>
              Vizualizează Detalii
            </button>
          </div>
        </div>
      </div>

      {/* Sectiune Inregistrare */}
      <div className="voice-recording-section">
        <div className="recording-controls-wrapper">
          <div className="recording-controls">
            {!isRecording ? (
              <button className="btn btn-primary" onClick={startRecording}>
                <MicIcon /> Începe Înregistrarea
              </button>
            ) : (
              <>
                <button className="btn btn-danger" onClick={stopRecording}>
                  <StopIcon /> Oprește ({formatTime(recordingTime)})
                </button>
                <span className="recording-indicator">● În direct...</span>
              </>
            )}
          </div>
          {isRecording && (
            <div className="waveform-visualizer-container">
              <canvas ref={canvasRef} width="400" height="80" className="waveform-canvas" />
            </div>
          )}
        </div>

        {recordedAudio && (
          <div className="audio-preview">
            <div className="audio-player">
              <button
                className="btn-play"
                onClick={() => playAudio(recordedAudio.url, 'current')}
              >
                {currentPlayingId === 'current' ? <PauseIcon /> : <PlayIcon />}
              </button>
              <span>
                {uploadedFileName ? `Fișier: ${uploadedFileName}` : `Audio înregistrat (${recordingTime}s)`}
              </span>
            </div>
            {loading && (
              <div style={{ marginTop: '15px', color: 'var(--primary)', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                <span className="cleanSpinner"></span>
                <span>Se analizeaza..</span>
              </div>
            )}
          </div>
        )}

        <div className="file-upload">
          <span className="upload-label">Sau încarcă un fișier audio:</span>
          <label htmlFor="audio-upload" className="custom-file-upload">
            <UploadIcon />
            <span>{uploadedFileName ? `Selectat: ${uploadedFileName}` : 'Alege un fișier audio...'}</span>
          </label>
          <input
            id="audio-upload"
            type="file"
            accept="audio/*"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
        </div>
      </div>

      {/* Rezultatele Analizei Curente */}
      {analysisResult && (
        <div className="analysis-result">
          <h3><ChartIcon /> Rezultatul Analizei</h3>

          <div className="transcript-section">
            <h4>Transcript:</h4>
            <p className="transcript">{analysisResult.transcript}</p>
          </div>

          {isClinicalMode && analysisResult.text_analysis?.feedback && (
            <div className="feedback-section" style={{
              marginBottom: '20px',
              padding: '16px',
              borderRadius: '10px',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderLeft: `4px solid ${analysisResult.text_analysis?.score !== null && analysisResult.text_analysis?.score !== undefined ? 'var(--primary)' : 'var(--success)'}`,
              textAlign: 'left'
            }}>
              <h4 style={{
                margin: '0 0 8px 0',
                fontSize: '13px',
                color: analysisResult.text_analysis?.score !== null && analysisResult.text_analysis?.score !== undefined ? 'var(--primary)' : 'var(--success)',
                fontFamily: 'var(--font-display)',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                fontWeight: '700'
              }}>
                {analysisResult.text_analysis?.score !== null && analysisResult.text_analysis?.score !== undefined ? '📋 Raport Analiză Vocală' : '💬 Răspuns Conversațional'}
              </h4>
              <p style={{
                margin: 0,
                fontFamily: 'var(--font-body)',
                fontSize: '13.5px',
                color: 'var(--text)',
                lineHeight: '1.6',
                whiteSpace: 'pre-line'
              }}>
                {analysisResult.text_analysis.feedback}
              </p>
            </div>
          )}

          {analysisResult.voice_analysis?.overall_voice_indicator !== null && 
           analysisResult.voice_analysis?.overall_voice_indicator !== undefined && (
            <>
              <div className="voice-analysis-grid">
                <div className="analysis-card">
                  <h5>Scor General Voce</h5>
                  <div className="score-display">
                    <div className="score-value">{analysisResult.voice_analysis?.overall_voice_indicator || 0}%</div>
                    <div className="score-bar">
                      <div
                        className="score-fill"
                        style={{
                          width: `${analysisResult.voice_analysis?.overall_voice_indicator || 0}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="analysis-card">
                  <h5>Energie</h5>
                  <div className="metric-display">
                    <span className="metric-value">
                      {analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.energy_score || 0) : 0}%
                    </span>
                    <span className="metric-label">Nivel energie</span>
                  </div>
                </div>

                <div className="analysis-card">
                  <h5>Ritm Vorbire</h5>
                  <div className="metric-display">
                    <span className="metric-value">
                      {analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.pace_score || 0) : 0}%
                    </span>
                    <span className="metric-label">Viteză vorbire</span>
                  </div>
                </div>

                <div className="analysis-card">
                  <h5>Claritate</h5>
                  <div className="metric-display">
                    <span className="metric-value">
                      {analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.clarity_score || 0) : 0}%
                    </span>
                    <span className="metric-label">Articulație</span>
                  </div>
                </div>

                <div className="analysis-card">
                  <h5>Ton Voce</h5>
                  <div className="metric-display">
                    <span className="metric-value">
                      {analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.tone_score || 0) : 0}%
                    </span>
                    <span className="metric-label">Variație tonală</span>
                  </div>
                </div>
              </div>

              {analysisResult.voice_analysis?.descriptions && (
                <div className="descriptions-section">
                  <h4>Observații Vocale:</h4>
                  <ul className="descriptions-list">
                    {analysisResult.voice_analysis.descriptions.map((desc, i) => (
                      <li key={i}>{desc}</li>
                    ))}
                  </ul>
                </div>
              )}

              {isClinicalMode && analysisResult.text_analysis && analysisResult.text_analysis.score !== null && (
                <div className="text-analysis-sub-section" style={{ marginTop: '20px', padding: '15px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: 'var(--primary)' }}>Analiză Semnificație Verbală (Text):</h4>
                  <p style={{ margin: '0 0 8px 0', fontStyle: 'italic', fontSize: '13px' }}>
                    "{analysisResult.transcript}"
                  </p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
                    <span>Risc de conținut: <strong style={{ color: analysisResult.text_analysis.score >= 75 ? '#f7768e' : '#73daca' }}>{analysisResult.text_analysis.score}%</strong></span>
                    <span>•</span>
                    <span>Categorie: <strong>{analysisResult.text_analysis.category}</strong></span>
                  </div>
                </div>
              )}

              {/* Recomandari */}
              {isClinicalMode && (
                <div className="recommendations">
                  <h3><LightbulbIcon /> Recomandări</h3>
                  <div className="recommendation-content">
                    {analysisResult.voice_analysis?.overall_voice_indicator > 70 ? (
                      <div className="recommendation-item warning">
                        <p>
                          <strong><WarningIcon /> Semne de îngrijorare:</strong> Analiza vocii indică posimize semne de depresie vocală ridicată.
                          Vă recomandăm cu tărie să consultați un specialist pentru evaluare medicală completă.
                        </p>
                      </div>
                    ) : analysisResult.voice_analysis?.overall_voice_indicator > 40 ? (
                      <div className="recommendation-item info">
                        <p>
                          <strong><InfoIcon /> Observație:</strong> Anumiți indicatori sugerează o stare emoțională ușor diminuată sau fatigabilitate.
                          Încercați să mențineți legătura cu persoane apropiate și să vă odihniți corespunzător.
                        </p>
                      </div>
                    ) : (
                      <div className="recommendation-item success">
                        <p>
                          <strong><CheckIcon /> Stare Optimă:</strong> Vocea dumneavoastră sună echilibrat, cu modulație tonală stabilă. Continuți să mențineți o stare activă și pozitivă.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Statistici Vocale */}
      {voiceStats && (
        <div className="voice-statistics">
          <h3><ChartIcon /> Statistici Vocale</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Total Înregistrări</div>
              <div className="stat-value">{voiceStats.total_recordings}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Scor Mediu</div>
              <div className="stat-value">{voiceStats.average_score?.toFixed(1)}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Scor Maxim</div>
              <div className="stat-value">{voiceStats.max_score}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Tendință</div>
              <div className={`stat-value ${voiceStats.trend > 0 ? 'positive' : voiceStats.trend < 0 ? 'negative' : ''}`}>
                {voiceStats.trend > 0 ? <TrendUpIcon /> : voiceStats.trend < 0 ? <TrendDownIcon /> : <TrendConstantIcon />}
                <span style={{ marginLeft: '4px' }}>
                  {voiceStats.trend > 0 ? 'Risc Ridicat' : voiceStats.trend < 0 ? 'Îmbunătățit' : 'Constant'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Istoricul Vocilor */}
      <div className="voice-history">
        <div className="history-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
          <h3 style={{ margin: 0 }}><CalendarIcon /> Istoricul Analizelor Vocale</h3>
          {voiceHistory.length > 0 && (
            <button 
              className="btn btn-danger delete-history-btn" 
              onClick={deleteVoiceHistory} 
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                fontSize: '12px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              <DeleteIcon /> Șterge Istoricul
            </button>
          )}
        </div>
        {voiceHistory.length > 0 ? (
          <div className="history-list">
            {voiceHistory.map((item, i) => (
              <div key={i} className="history-item">
                <div className="history-time">
                  {new Date(item.timestamp).toLocaleDateString('ro-RO', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
                <div className="history-content">
                  <div className="history-score">
                    Scor Risc: <strong>{item.voice_score !== null && item.voice_score !== undefined ? `${item.voice_score}%` : 'Conversație'}</strong>
                  </div>
                  <div className="history-transcript">{item.transcript?.substring(0, 120)}...</div>
                  <button
                    className="btn-small"
                    onClick={() => playAudio(item.audio_url, `history-${i}`)}
                  >
                    {currentPlayingId === `history-${i}` ? <PauseIcon /> : <PlayIcon />}
                    <span style={{ marginLeft: '6px' }}>
                      {currentPlayingId === `history-${i}` ? 'Oprește' : 'Reluare'}
                    </span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">Nu sunt înregistrări anterioare</p>
        )}
      </div>

      {/* POPUP URGENȚĂ */}
      {showEmergencyPopup && (
        <EmergencyPopup 
          score={criticalScore} 
          onClose={() => setShowEmergencyPopup(false)} 
        />
      )}

      {/* Modal Confirmare Trimitere Audio */}
      {showConfirmModal && pendingAudio && (
        <div className="ec-modal-overlay" onClick={cancelAudioAnalysis} style={{ backgroundColor: 'rgba(10, 10, 15, 0.85)', backdropFilter: 'blur(12px)', zIndex: 9999 }}>
          <div className="ec-modal-content central-popup" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '420px', background: 'linear-gradient(135deg, #181824 0%, #0f0f18 100%)', border: '1px solid rgba(187, 154, 247, 0.25)', boxShadow: '0 25px 60px rgba(0, 0, 0, 0.6)', borderRadius: '24px' }}>
            <div className="ec-modal-header" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', padding: '18px 24px' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '16px', fontWeight: '700', color: '#bb9af7' }}><MicIcon /> Confirmare Audio</h3>
              <button className="ec-modal-close-btn" onClick={cancelAudioAnalysis} style={{ fontSize: '22px' }}>&times;</button>
            </div>
            <div className="ec-modal-body" style={{ textAlign: 'center', padding: '24px' }}>
              <div style={{ marginBottom: '20px', padding: '15px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <audio src={pendingAudio.url} controls style={{ width: '100%' }} />
              </div>
              <p style={{ margin: '0 0 20px 0', fontSize: '14px', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                {pendingAudio.isUpload 
                  ? `Dorești să trimiți fișierul "${pendingAudio.name}" pentru analiză vocală?` 
                  : 'Dorești să trimiți înregistrarea audio pentru analiză vocală?'}
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button 
                  className="btn btn-success" 
                  onClick={confirmAudioAnalysis}
                  style={{ padding: '10px 28px', fontSize: '14px', fontWeight: '600' }}
                >
                  <CheckIcon /> Trimite pentru Analiză
                </button>
                <button 
                  className="btn btn-danger" 
                  onClick={cancelAudioAnalysis}
                  style={{ padding: '10px 28px', fontSize: '14px', fontWeight: '600' }}
                >
                  <CrossIcon /> Renunță
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Custom Toast Alert Overlay */}
      {toast.show && (
        <div className={`toast-alert ${toast.type}`}>
          <div className="toast-icon">{toast.type === 'success' ? <CheckIcon /> : <CrossIcon />}</div>
          <div className="toast-message">{toast.message}</div>
        </div>
      )}

      {/* Modal / Popup Centrat pentru Context Vocal Extins */}
      {showReportModal && dashboardStats && createPortal(
        <div className="ec-modal-overlay" onClick={() => setShowReportModal(false)} style={{ backgroundColor: 'rgba(10, 10, 15, 0.85)', backdropFilter: 'blur(12px)' }}>
          <div className="ec-modal-content central-popup" onClick={(e) => e.stopPropagation()} style={{
            background: 'linear-gradient(135deg, #181824 0%, #0f0f18 100%)',
            border: '1px solid rgba(187, 154, 247, 0.25)',
            boxShadow: '0 25px 60px rgba(0, 0, 0, 0.6), inset 0 0 30px rgba(187, 154, 247, 0.05)',
            borderRadius: '24px',
            maxWidth: '560px'
          }}>
            <div className="ec-modal-header" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', padding: '18px 24px' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '16px', fontWeight: '700', color: '#bb9af7' }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                Context Vocal Extins
              </h3>
              <button className="ec-modal-close-btn" onClick={() => setShowReportModal(false)} style={{ fontSize: '22px' }}>&times;</button>
            </div>
            
            <div className="ec-modal-body text-center" style={{ textAlign: 'center', padding: '24px' }}>
              <div className="central-score-gauge" style={{ position: 'relative', width: '130px', height: '130px', margin: '0 auto 15px auto' }}>
                <svg className="central-radial-svg" width="130" height="130" viewBox="0 0 130 130">
                  <circle className="central-track" cx="65" cy="65" r="54" fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth="8" />
                  <circle 
                    className="central-progress" 
                    cx="65" 
                    cy="65" 
                    r="54" 
                    fill="none"
                    strokeWidth="8" 
                    stroke={
                      dashboardStats.voice_average >= 70 
                        ? '#f7768e' 
                        : dashboardStats.voice_average >= 40 
                        ? '#ff9f43' 
                        : '#73daca'
                    }
                    strokeDasharray={`${2 * Math.PI * 54}`}
                    strokeDashoffset={`${2 * Math.PI * 54 * (1 - dashboardStats.voice_average / 100)}`}
                    transform="rotate(-90 65 65)"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="central-gauge-score" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: '800', fontSize: '28px', color: '#fff', letterSpacing: '-0.02em' }}>
                  {Math.round(dashboardStats.voice_average)}%
                </div>
              </div>
              
              <div className="ec-modal-risk-badge" style={{
                background: dashboardStats.voice_average >= 70 ? 'rgba(247, 118, 142, 0.12)' : dashboardStats.voice_average >= 40 ? 'rgba(255, 159, 67, 0.12)' : 'rgba(115, 218, 202, 0.12)',
                color: dashboardStats.voice_average >= 70 ? '#f7768e' : dashboardStats.voice_average >= 40 ? '#ff9f43' : '#73daca',
                border: `1px solid ${dashboardStats.voice_average >= 70 ? 'rgba(247, 118, 142, 0.25)' : dashboardStats.voice_average >= 40 ? 'rgba(255, 159, 67, 0.25)' : 'rgba(115, 218, 202, 0.25)'}`,
                display: 'inline-block',
                margin: '5px auto 20px auto',
                padding: '6px 18px',
                borderRadius: '30px',
                fontWeight: '700',
                fontSize: '12px',
                letterSpacing: '0.5px'
              }}>
                {dashboardStats.voice_average >= 70 ? 'NIVEL DE ALERTĂ RIDICAT' : dashboardStats.voice_average >= 40 ? 'NIVEL DE ALERTĂ MODERAT' : 'NIVEL DE ALERTĂ SCĂZUT'}
              </div>

              <div className="ec-breakdown-details" style={{ marginTop: '20px', padding: '20px', background: 'rgba(255,255,255,0.01)', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.04)', textAlign: 'left' }}>
                <h4 style={{ margin: '0 0 18px 0', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '1px', color: '#bb9af7', fontWeight: '700' }}>Dimensiuni Acustice Vocale</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  {/* Energie */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Energie</span>
                      <strong style={{ color: '#73daca' }}>{analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.energy_score || 0) : 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.energy_score || 0) : 0}%`, background: '#73daca', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  {/* Ritm Vorbire */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Ritm Vorbire</span>
                      <strong style={{ color: '#ff9f43' }}>{analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.pace_score || 0) : 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.pace_score || 0) : 0}%`, background: '#ff9f43', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  {/* Claritate Articulație */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Claritate Articulație</span>
                      <strong style={{ color: '#7aa2f7' }}>{analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.clarity_score || 0) : 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.clarity_score || 0) : 0}%`, background: '#7aa2f7', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  {/* Ton Voce */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Ton Voce</span>
                      <strong style={{ color: '#bb9af7' }}>{analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.tone_score || 0) : 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.voice_analysis ? 100 - (analysisResult.voice_analysis.tone_score || 0) : 0}%`, background: '#bb9af7', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="ec-modal-report-text" style={{ marginTop: '25px', textAlign: 'left' }}>
                <h4 style={{ fontSize: '13px', color: '#ffb86c', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '700' }}>Evaluare Acustică Vocală</h4>
                <div style={{
                  padding: '16px 20px',
                  background: 'rgba(255,255,255,0.01)',
                  border: '1px solid rgba(255,255,255,0.03)',
                  borderLeft: `4px solid ${
                    dashboardStats.voice_average >= 70 
                      ? '#f7768e' 
                      : dashboardStats.voice_average >= 40 
                      ? '#ff9f43' 
                      : '#73daca'
                  }`,
                  borderRadius: '0 12px 12px 0'
                }}>
                  <p style={{ margin: 0, fontSize: '13.5px', lineHeight: '1.7', color: 'rgba(255, 255, 255, 0.8)' }}>
                    {(() => {
                      const voiceAvg = Math.round(dashboardStats.voice_average);
                      const energy = analysisResult?.voice_analysis?.energy_score || 0;
                      const pace = analysisResult?.voice_analysis?.pace_score || 0;
                      const clarity = analysisResult?.voice_analysis?.clarity_score || 0;
                      const tone = analysisResult?.voice_analysis?.tone_score || 0;
                      
                      const isApropiat = dashboardStats.tip_detectie === 'apropiat';
                      
                      if (isApropiat) {
                        if (voiceAvg < 20) {
                          return `Parametrii acustici ai vocii persoanei apropiate sunt stabili și normali. Ritmul, energia și intonația indică un ton dinamic, fără semne acustice de oboseală sau aplatizare vocală.`;
                        } else if (voiceAvg < 35) {
                          return `Se remarcă o stare acustică stabilă la persoana apropiată. Există doar mici variații nesemnificative de oboseală acustică (${energy}%) sau o ușoară încetinire a ritmului vorbirii (${pace}%).`;
                        } else if (voiceAvg < 50) {
                          return `Se observă o oboseală vocală moderată la persoana apropiată. Acest lucru se datorează în mod special ${energy >= Math.max(pace, clarity, tone) ? `unei scăderi a energiei vocale (${energy}%)` : pace >= Math.max(clarity, tone) ? `ritmului încetinit al vorbirii (${pace}%)` : clarity >= tone ? `scăderii clarității articulării cuvintelor (${clarity}%)` : `monotoniei tonului vocii (${tone}%)`}. Parametrii arată un efort vocal crescut.`;
                        } else if (voiceAvg < 70) {
                          return `Parametrii vocali ai persoanei apropiate indică o stare avansată de letargie și oboseală emoțională. Analiza relevă ${energy >= Math.max(pace, clarity, tone) ? `o energie vocală extrem de scăzută (${energy}%)` : pace >= Math.max(clarity, tone) ? `vorbire lentă și letargică, specifică încetinirii psihomotorii (${pace}%)` : clarity >= tone ? `pronunție neclară, mormăită și obosită (${clarity}%)` : `lipsă totală de intonație și aplatizare vocală accentuată (${tone}%)`}.`;
                        } else {
                          return `Risc acustic extrem de ridicat identificat la persoana apropiată. Vocea este profund letargică, plată și monotonă (ritm=${pace}%, energie=${energy}%, intonație=${tone}%), reflectând o epuizare emoțională profundă sau o stare severă de tristețe.`;
                        }
                      } else {
                        if (voiceAvg < 20) {
                          return `Vocea ta sună minunat de caldă, energică și plină de viață! Parametrii arată o exprimare clară și un ritm natural. Menține-ți această energie frumoasă!`;
                        } else if (voiceAvg < 35) {
                          return `Vocea ta sună în general stabilă și liniștită. Am remarcat doar mici urme discrete de oboseală vocală (${energy}%) sau o ușoară ezitare în vorbire (${pace}%), probabil din cauza oboselii de peste zi. Fii blând cu tine și oferă-ți puțin repaus.`;
                        } else if (voiceAvg < 50) {
                          return `Se simte o mică oboseală sau lipsă de energie în vocea ta. Această stare este vizibilă prin ${energy >= Math.max(pace, clarity, tone) ? `o energie a vocii ceva mai scăzută (${energy}%)` : pace >= Math.max(clarity, tone) ? `un ritm de vorbire puțin mai lent și domol (${pace}%)` : clarity >= tone ? `o articulare mai puțin fermă a cuvintelor (${clarity}%)` : `un ton mai puțin modulat și plat (${tone}%)`}. Ai grijă de tine, oferă-ți timp să te odihnești și bea un ceai cald.`;
                        } else if (voiceAvg < 70) {
                          return `Vocea ta transmite o stare destul de pronunțată de oboseală emoțională și lipsă de putere. Parametrii arată ${energy >= Math.max(pace, clarity, tone) ? `o energie vocală foarte redusă (${energy}%)` : pace >= Math.max(clarity, tone) ? `un ritm de vorbire lent și obosit (${pace}%)` : clarity >= tone ? `cuvinte rostite mai greu și cu mai puțină claritate (${clarity}%)` : `o monotonie a tonului, fără prea multă intonație (${tone}%)`}. Încearcă să faci o pauză, să nu te suprasoliți și să discuți deschis cu cineva apropiat care te înțelege.`;
                        } else {
                          return `Se aude o oboseală extrem de profundă și o suferință intensă în vocea ta în acest moment. Tonul tău este extrem de plat, lent și cu energie scăzută (ritm=${pace}%, energie=${energy}%, intonație=${tone}%). Te rugăm să îți permiți să fii vulnerabil și să ceri sprijinul sau pur și simplu prezența caldă a unei persoane dragi care te poate asculta și susține.`;
                        }
                      }
                    })()}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="ec-modal-footer" style={{ borderTop: '1px solid rgba(255,255,255,0.04)', padding: '16px 24px', background: 'rgba(0,0,0,0.05)' }}>
              <button className="btn btn-primary ec-modal-close-action" onClick={() => setShowReportModal(false)} style={{
                background: 'linear-gradient(135deg, #bb9af7, #7aa2f7)',
                border: 'none',
                fontWeight: '600'
              }}>Închide</button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default EnhancedVoiceComponent;
