import React, { useState, useEffect, useRef } from 'react';
import * as faceapi from '@vladmandic/face-api';

// SVG Icons
const FaceIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <circle cx="12" cy="12" r="10" />
    <path d="M8 14s1.5 2 4 2 4-2 4-2" />
    <line x1="9" x2="9.01" y1="9" y2="9" />
    <line x1="15" x2="15.01" y1="9" y2="9" />
  </svg>
);

const CameraIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
    <circle cx="12" cy="13" r="3" />
  </svg>
);

const CaptureIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const SearchIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" x2="16.65" y1="21" y2="16.65" />
  </svg>
);

const CloseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <line x1="18" x2="6" y1="6" y2="18" />
    <line x1="6" x2="18" y1="6" y2="18" />
  </svg>
);

const ChatIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const ChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <line x1="18" x2="18" y1="20" y2="10" />
    <line x1="12" x2="12" y1="20" y2="4" />
    <line x1="6" x2="6" y1="20" y2="14" />
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
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon upload-large-icon">
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

const EnhancedFaceComponent = ({ chatId }) => {
  const [currentChatId, setCurrentChatId] = useState(() => {
    const storedChatId = localStorage.getItem("activeChatId");
    const parsedChatId = storedChatId ? parseInt(storedChatId, 10) : null;
    return (parsedChatId && !isNaN(parsedChatId)) ? parsedChatId : (chatId || 1);
  });

  const [chatName, setChatName] = useState("");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [pendingImage, setPendingImage] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [faceHistory, setFaceHistory] = useState([]);
  const [emotionStats, setEmotionStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, type: 'success', message: '' });
  const [dashboardStats, setDashboardStats] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [isClinicalMode] = useState(true);
  const cameraRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const overlayAnimationFrameRef = useRef(null);
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
    const loadModels = async () => {
      try {
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
          faceapi.nets.faceExpressionNet.loadFromUri('/models')
        ]);
        console.log('✅ Face-API models loaded successfully');
      } catch (error) {
        console.error('❌ Failed to load Face-API models:', error);
        triggerToast('error', 'Eroare la încărcarea modelelor de analiză facială.');
      }
    };
    loadModels();
  }, []);

  useEffect(() => {
    if (currentChatId) {
      // Clear previous analysis session states when switching chats
      setAnalysisResult(null);
      setUploadedImage(null);
      setUploadedFileName('');

      loadFaceHistory();
      loadEmotionStats();
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

  useEffect(() => {
    if (cameraActive && streamRef.current && cameraRef.current) {
      cameraRef.current.srcObject = streamRef.current;
    }
  }, [cameraActive]);

  useEffect(() => {
    if (cameraActive) {
      const timer = setTimeout(() => {
        drawLandmarks();
      }, 200);
      return () => clearTimeout(timer);
    } else {
      if (overlayAnimationFrameRef.current) {
        cancelAnimationFrame(overlayAnimationFrameRef.current);
      }
    }
  }, [cameraActive]);

  useEffect(() => {
    return () => {
      if (overlayAnimationFrameRef.current) {
        cancelAnimationFrame(overlayAnimationFrameRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const drawLandmarks = () => {
    if (!overlayCanvasRef.current || !cameraActive) return;
    const canvas = overlayCanvasRef.current;
    const ctx = canvas.getContext('2d');

    const draw = () => {
      if (!overlayCanvasRef.current || !cameraActive) return;
      overlayAnimationFrameRef.current = requestAnimationFrame(draw);

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const computedStyle = getComputedStyle(document.documentElement);
      const primaryColor = computedStyle.getPropertyValue('--primary').trim() || 'hsl(260, 60%, 62%)';
      const accentColor = computedStyle.getPropertyValue('--accent').trim() || 'hsl(290, 55%, 58%)';

      const width = canvas.width;
      const height = canvas.height;

      // Draw Scanner Glowing Target Corners
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 3;

      // Top-Left
      ctx.beginPath(); ctx.moveTo(20, 50); ctx.lineTo(20, 20); ctx.lineTo(50, 20); ctx.stroke();
      // Top-Right
      ctx.beginPath(); ctx.moveTo(width - 50, 20); ctx.lineTo(width - 20, 20); ctx.lineTo(width - 20, 50); ctx.stroke();
      // Bottom-Left
      ctx.beginPath(); ctx.moveTo(20, height - 50); ctx.lineTo(20, height - 20); ctx.lineTo(50, height - 20); ctx.stroke();
      // Bottom-Right
      ctx.beginPath(); ctx.moveTo(width - 50, height - 20); ctx.lineTo(width - 20, height - 20); ctx.lineTo(width - 20, height - 50); ctx.stroke();

      // Scanner pulse line
      const scanY = (height / 2) + Math.sin(Date.now() / 400) * (height / 2.5);
      const transparentPrimary = primaryColor.replace(/hsl\(([^)]+)\)/, 'hsla($1, 0.35)');
      ctx.strokeStyle = transparentPrimary.includes('hsla') ? transparentPrimary : 'rgba(102, 126, 234, 0.35)';
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(30, scanY); ctx.lineTo(width - 30, scanY); ctx.stroke();

      // Target Mesh
      const centerX = width / 2;
      const centerY = height / 2;
      const jitter = () => Math.sin(Date.now() / 150 + Math.random() * 0.05) * 1.5;

      // Face boundary ring
      const transparentAccent = accentColor.replace(/hsl\(([^)]+)\)/, 'hsla($1, 0.2)');
      ctx.strokeStyle = transparentAccent.includes('hsla') ? transparentAccent : 'rgba(118, 75, 162, 0.2)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(centerX + jitter(), centerY - 10 + jitter(), 105, 0, Math.PI * 2);
      ctx.stroke();

      const points = [
        { x: 0, y: -75 }, { x: -35, y: -65 }, { x: 35, y: -65 },
        { x: -45, y: -25 }, { x: -18, y: -30 }, { x: 18, y: -30 }, { x: 45, y: -25 },
        { x: -30, y: -5 }, { x: 30, y: -5 },
        { x: 0, y: -15 }, { x: 0, y: 15 }, { x: -12, y: 12 }, { x: 12, y: 12 },
        { x: -25, y: 40 }, { x: 25, y: 40 }, { x: 0, y: 32 }, { x: 0, y: 48 },
        { x: 0, y: 90 }, { x: -50, y: 70 }, { x: 50, y: 70 }, { x: -85, y: 25 }, { x: 85, y: 25 }
      ];

      ctx.fillStyle = primaryColor;
      const transparentPrimaryLines = primaryColor.replace(/hsl\(([^)]+)\)/, 'hsla($1, 0.25)');
      ctx.strokeStyle = transparentPrimaryLines.includes('hsla') ? transparentPrimaryLines : 'rgba(102, 126, 234, 0.25)';
      ctx.lineWidth = 1;

      ctx.beginPath();
      ctx.moveTo(centerX - 45 + jitter(), centerY - 25 + jitter());
      ctx.lineTo(centerX - 18 + jitter(), centerY - 30 + jitter());
      ctx.lineTo(centerX + jitter(), centerY - 15 + jitter());
      ctx.lineTo(centerX + 18 + jitter(), centerY - 30 + jitter());
      ctx.lineTo(centerX + 45 + jitter(), centerY - 25 + jitter());

      ctx.moveTo(centerX + jitter(), centerY - 30 + jitter());
      ctx.lineTo(centerX + jitter(), centerY - 15 + jitter());
      ctx.lineTo(centerX + jitter(), centerY + 15 + jitter());

      ctx.moveTo(centerX - 25 + jitter(), centerY + 40 + jitter());
      ctx.lineTo(centerX + jitter(), centerY + 32 + jitter());
      ctx.lineTo(centerX + 25 + jitter(), centerY + 40 + jitter());
      ctx.lineTo(centerX + jitter(), centerY + 48 + jitter());
      ctx.closePath();
      ctx.stroke();

      points.forEach(pt => {
        const px = centerX + pt.x + jitter();
        const py = centerY + pt.y + jitter();
        ctx.beginPath();
        ctx.arc(px, py, 3, 0, Math.PI * 2);
        ctx.fill();
      });
    };
    draw();
  };

  const triggerToast = (type, message) => {
    setToast({ show: true, type, message });
    setTimeout(() => {
      setToast({ show: false, type: 'success', message: '' });
    }, 4000);
  };

  // Récupérer l'historique des analyses faciales
  const loadFaceHistory = async () => {
    try {
      const response = await fetch(`http://localhost:5000/get-face-history/${currentChatId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setFaceHistory(data.history || []);
      }
    } catch (error) {
      print('Error loading face history:', error);
    }
  };

  // Récupérer les statistiques d'émotion
  const loadEmotionStats = async () => {
    try {
      const response = await fetch(`http://localhost:5000/get-emotion-stats/${currentChatId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setEmotionStats(data.stats);
      }
    } catch (error) {
      console.error('Error loading emotion stats:', error);
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

  // Activa camera
  const startCamera = async () => {
    try {
      setUploadedFileName('');
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
      streamRef.current = stream;
      setCameraActive(true);
      triggerToast('success', 'Camera video a fost activată.');
    } catch (error) {
      triggerToast('error', 'Acces cameră refuzat: ' + error.message);
    }
  };

  // Opri camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (cameraRef.current) {
      cameraRef.current.srcObject = null;
    }
    setCameraActive(false);
    triggerToast('info', 'Camera video a fost oprită.');
  };

  // Captura poza din camera
  const capturePhoto = () => {
    console.log('[Operation] Capture photo start');
    if (cameraRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      context.drawImage(cameraRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
      const imageData = canvasRef.current.toDataURL('image/jpeg');
      setPendingImage(imageData);
      setShowConfirmModal(true);
      stopCamera();
      triggerToast('info', 'Fotografie capturată. Confirmă trimiterea pentru analiză.');
      console.log('[Operation] Photo captured, awaiting confirmation');
    }
  };

  // Incarca poza
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageData = e.target.result;
        setPendingImage(imageData);
        setUploadedFileName(file.name);
        setShowConfirmModal(true);
        triggerToast('info', 'Imagine încărcată. Confirmă trimiterea pentru analiză.');
        console.log('[Operation] Image uploaded, awaiting confirmation');
      };
      reader.readAsDataURL(file);
    }
  };

  // Analizeaza poza
  const analyzeFace = async (imageSrc = null) => {
    const targetImage = imageSrc || uploadedImage;
    if (!targetImage) {
      triggerToast('error', 'Vă rugăm selectați sau capturați o fotografie mai întâi.');
      return;
    }

    setLoading(true);
    try {
      // Load image element
      const img = new Image();
      img.src = targetImage;
      await new Promise((resolve) => {
        img.onload = resolve;
      });

      // Run face detection
      const detection = await faceapi.detectSingleFace(img, new faceapi.TinyFaceDetectorOptions({ inputSize: 224, scoreThreshold: 0.4 }))
        .withFaceExpressions();

      // Prepare payload using the actual detected expressions if face is detected
      let faceDetectionPayload = null;
      if (detection) {
        faceDetectionPayload = {
          expressions: {
            neutral: detection.expressions.neutral || 0,
            happy: detection.expressions.happy || 0,
            sad: detection.expressions.sad || 0,
            angry: detection.expressions.angry || 0,
            fearful: detection.expressions.fearful || 0,
            disgusted: detection.expressions.disgusted || 0,
            surprised: detection.expressions.surprised || 0
          },
          detection: {
            score: detection.detection.score || 0.95,
            box: {
              x: detection.detection.box.x || 0,
              y: detection.detection.box.y || 0,
              width: detection.detection.box.width || 0,
              height: detection.detection.box.height || 0
            }
          }
        };
      } else {
        console.log("⚠️ Face-API local detection failed.");
      }

      const response = await fetch('http://localhost:5000/analyze-face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          face_detection: faceDetectionPayload,
          chat_id: currentChatId,
          image: targetImage,
          trigger_diagnosis: 'true'
        }),
      });

      const result = await response.json();

      if (result.status === 'success') {
        setAnalysisResult(result);
        triggerToast('success', 'Analiza facială a fost realizată cu succes!');
        setUploadedImage(null);
        setUploadedFileName('');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        await loadFaceHistory();
        await loadEmotionStats();
        await loadDashboardStats();
        // Notify other components (like MiniDashboard) of state change
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

  // Șterge istoricul recunoașterii faciale
  const deleteFaceHistory = async () => {
    if (window.confirm("Sigur dorești să ștergi tot istoricul și datele din recunoașterea facială? Această acțiune este ireversibilă.")) {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/delete-face-history/${currentChatId}`, {
          method: 'DELETE'
        });
        const data = await response.json();
        if (data.status === 'success') {
          triggerToast('success', 'Istoricul analizei faciale a fost șters cu succes.');
          setAnalysisResult(null);
          setFaceHistory([]);
          setEmotionStats(null);
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

  const getEmotionColor = (emotion, value) => {
    if (value > 0.5) return '#e74c3c';
    if (value > 0.3) return '#f39c12';
    return '#27ae60';
  };

  return (
    <div className="face-container enhanced-face">
      <div className="face-header">
        <h2><FaceIcon /> Analiză Facială Avansată {chatName && ` - ${chatName}`}</h2>
        <p>Încarcă o poză sau fă un selfie pentru analiza semnelor de depresie pe baza expresiilor faciale</p>
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

      {/* Card Diagnoză Context Facial Extins — mereu vizibil */}
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
                    strokeDashoffset: `${2 * Math.PI * 42 * (1 - (dashboardStats ? dashboardStats.face_average : 0) / 100)}`,
                    stroke: 'url(#ec-grad)',
                    strokeWidth: '6',
                    strokeLinecap: 'round'
                  }}
                />
              </svg>
              <div className="ec-diag-score-value" style={{ fontWeight: '800', color: '#fff' }}>
                {dashboardStats ? `${Math.round(dashboardStats.face_average)}%` : '0%'}
              </div>
            </div>
            <div className="ec-diag-card-info">
              <h4 className="ec-diag-card-title" style={{ color: '#bb9af7', fontWeight: '700', fontSize: '14px' }}>Context Facial Extins</h4>
              <p className="ec-diag-card-desc" style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                Nivel de alertă determinat din istoricul evoluției mimicii faciale.
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

      {/* Sectiune Camera */}
      <div className="face-camera-section">
        {cameraActive ? (
          <div className="camera-active">
            <div className="camera-feed-wrapper">
              <video ref={cameraRef} className="camera-feed" autoPlay playsInline />
              <canvas ref={overlayCanvasRef} width="640" height="480" className="camera-overlay-canvas" />
            </div>
            <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />
            <div className="camera-controls">
              <button className="btn btn-success" onClick={capturePhoto}>
                <CaptureIcon /> Captură Poza
              </button>
              <button className="btn btn-danger" onClick={stopCamera}>
                <CloseIcon /> Închide Camera
              </button>
            </div>
          </div>
        ) : (
          <div className="camera-inactive">
            <button className="btn btn-primary" onClick={startCamera}>
              <CameraIcon /> Deschide Camera
            </button>
          </div>
        )}
      </div>

      {/* Incarcare Poza */}
      <div className="file-upload-section">
        <span className="upload-label">Sau încarcă o poză:</span>
        <label htmlFor="face-upload" className="custom-image-upload">
          <UploadIcon />
          <span className="upload-text">
            {uploadedFileName ? `Selectat: ${uploadedFileName}` : 'Glisează sau alege o imagine...'}
          </span>
        </label>
        <input
          id="face-upload"
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          style={{ display: 'none' }}
        />
      </div>

      {/* Preview Poza + Stare de încarcare / analiză */}
      {loading && uploadedImage && (
        <div className="image-preview-analyzing" style={{ textAlign: 'center', padding: '20px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)', marginTop: '20px' }}>
          <img src={uploadedImage} alt="Analiză" style={{ maxWidth: '280px', maxHeight: '280px', borderRadius: '10px', filter: 'blur(1px) grayscale(30%)', objectFit: 'contain' }} />
          <div style={{ marginTop: '15px', color: 'var(--primary)', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
            <span className="cleanSpinner"></span>
            <span>Se analizeaza..</span>
          </div>
        </div>
      )}

      {/* Rezultatele Analizei */}
      {analysisResult && (
        <div className="face-analysis-result">
          <h3><ChartIcon /> Rezultatul Analizei</h3>

          <div className="emotion-grid">
            <div className="emotion-card">
              <h5>Scor Depresie Față</h5>
              <div className="score-display">
                <div className="score-value">{analysisResult.overall_face_depression_score || 0}%</div>
                <div className="score-bar">
                  <div
                    className="score-fill depression"
                    style={{
                      width: `${analysisResult.overall_face_depression_score || 0}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="emotion-breakdown">
            <h4>Emoții Detectate:</h4>
            <div className="emotions-list">
              {analysisResult.facial_features?.emotions && Object.entries(analysisResult.facial_features.emotions).map(([emotion, value]) => (
                <div key={emotion} className="emotion-item">
                  <span className="emotion-name">{emotion}</span>
                  <div className="emotion-bar">
                    <div
                      className="emotion-fill"
                      style={{
                        width: `${value * 100}%`,
                        backgroundColor: getEmotionColor(emotion, value),
                      }}
                    />
                  </div>
                  <span className="emotion-value">{(value * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>

          {analysisResult.depression_indicators && (
            <div className="depression-indicators">
              <h4 style={{ marginBottom: '20px' }}>Dimensiuni Mimico-Faciale (DSM-5):</h4>
              <div className="indicators-grid-premium" style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '15px' }}>
                
                {/* Tristețe */}
                <div className="indicator-card-premium" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '12px 15px', textAlign: 'center', minWidth: '100px', flex: '1 1 120px' }}>
                  <div className="indicator-gauge-wrapper" style={{ position: 'relative', width: '65px', height: '65px', margin: '0 auto 8px auto' }}>
                    <svg width="65" height="65" viewBox="0 0 65 65">
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="4" />
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="#7aa2f7" strokeWidth="4" 
                              strokeDasharray={`${2 * Math.PI * 28}`}
                              strokeDashoffset={`${2 * Math.PI * 28 * (1 - (analysisResult.depression_indicators.sadness || 0) / 100)}`}
                              transform="rotate(-90 32.5 32.5)" strokeLinecap="round" />
                    </svg>
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: 'bold', fontSize: '13px', color: '#7aa2f7' }}>
                      {analysisResult.depression_indicators.sadness || 0}%
                    </div>
                  </div>
                  <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: '600' }}>Tristețe</span>
                </div>

                {/* Anxietate */}
                <div className="indicator-card-premium" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '12px 15px', textAlign: 'center', minWidth: '100px', flex: '1 1 120px' }}>
                  <div className="indicator-gauge-wrapper" style={{ position: 'relative', width: '65px', height: '65px', margin: '0 auto 8px auto' }}>
                    <svg width="65" height="65" viewBox="0 0 65 65">
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="4" />
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="#bb9af7" strokeWidth="4" 
                              strokeDasharray={`${2 * Math.PI * 28}`}
                              strokeDashoffset={`${2 * Math.PI * 28 * (1 - (analysisResult.depression_indicators.anxiety || 0) / 100)}`}
                              transform="rotate(-90 32.5 32.5)" strokeLinecap="round" />
                    </svg>
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: 'bold', fontSize: '13px', color: '#bb9af7' }}>
                      {analysisResult.depression_indicators.anxiety || 0}%
                    </div>
                  </div>
                  <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: '600' }}>Anxietate</span>
                </div>

                {/* Iritabilitate */}
                <div className="indicator-card-premium" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '12px 15px', textAlign: 'center', minWidth: '100px', flex: '1 1 120px' }}>
                  <div className="indicator-gauge-wrapper" style={{ position: 'relative', width: '65px', height: '65px', margin: '0 auto 8px auto' }}>
                    <svg width="65" height="65" viewBox="0 0 65 65">
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="4" />
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="#f7768e" strokeWidth="4" 
                              strokeDasharray={`${2 * Math.PI * 28}`}
                              strokeDashoffset={`${2 * Math.PI * 28 * (1 - (analysisResult.depression_indicators.irritability || 0) / 100)}`}
                              transform="rotate(-90 32.5 32.5)" strokeLinecap="round" />
                    </svg>
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: 'bold', fontSize: '13px', color: '#f7768e' }}>
                      {analysisResult.depression_indicators.irritability || 0}%
                    </div>
                  </div>
                  <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: '600' }}>Iritabilitate</span>
                </div>

                {/* Anhedonie */}
                <div className="indicator-card-premium" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '12px 15px', textAlign: 'center', minWidth: '100px', flex: '1 1 120px' }}>
                  <div className="indicator-gauge-wrapper" style={{ position: 'relative', width: '65px', height: '65px', margin: '0 auto 8px auto' }}>
                    <svg width="65" height="65" viewBox="0 0 65 65">
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="4" />
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="#ff9f43" strokeWidth="4" 
                              strokeDasharray={`${2 * Math.PI * 28}`}
                              strokeDashoffset={`${2 * Math.PI * 28 * (1 - (analysisResult.depression_indicators.anhedonia || 0) / 100)}`}
                              transform="rotate(-90 32.5 32.5)" strokeLinecap="round" />
                    </svg>
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: 'bold', fontSize: '13px', color: '#ff9f43' }}>
                      {analysisResult.depression_indicators.anhedonia || 0}%
                    </div>
                  </div>
                  <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: '600' }}>Anhedonie</span>
                </div>

                {/* Indiferență */}
                <div className="indicator-card-premium" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '12px 15px', textAlign: 'center', minWidth: '100px', flex: '1 1 120px' }}>
                  <div className="indicator-gauge-wrapper" style={{ position: 'relative', width: '65px', height: '65px', margin: '0 auto 8px auto' }}>
                    <svg width="65" height="65" viewBox="0 0 65 65">
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="4" />
                      <circle cx="32.5" cy="32.5" r="28" fill="none" stroke="#73daca" strokeWidth="4" 
                              strokeDasharray={`${2 * Math.PI * 28}`}
                              strokeDashoffset={`${2 * Math.PI * 28 * (1 - ((analysisResult.depression_indicators.indifference !== undefined ? analysisResult.depression_indicators.indifference : analysisResult.depression_indicators.dissociation) || 0) / 100)}`}
                              transform="rotate(-90 32.5 32.5)" strokeLinecap="round" />
                    </svg>
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: 'bold', fontSize: '13px', color: '#73daca' }}>
                      {analysisResult.depression_indicators.indifference !== undefined ? analysisResult.depression_indicators.indifference : (analysisResult.depression_indicators.dissociation || 0)}%
                    </div>
                  </div>
                  <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: '600' }}>Indiferență</span>
                </div>

              </div>
            </div>
          )}

          {isClinicalMode && analysisResult.facial_features?.notes && analysisResult.facial_features.notes.length > 0 && (
            <div className="analysis-notes">
              {analysisResult.facial_features.notes.map((note, index) => (
                <div 
                  key={index} 
                  className={`note-item ${note.toLowerCase().includes('critical') || note.includes('🚨') || note.toLowerCase().includes('weapon') || note.toLowerCase().includes('head') || note.toLowerCase().includes('rope') ? 'critical-warning' : 'info-note'}`}
                >
                  {note}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Statistici Emotii */}
      {emotionStats && (
        <div className="emotion-statistics">
          <h3><ChartIcon /> Statistici Emoții</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Total Analize</div>
              <div className="stat-value">{emotionStats.total_analyses}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Emoție Dominantă</div>
              <div className="stat-value">{emotionStats.dominant_emotion}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Scor Mediu Depresie</div>
              <div className="stat-value">{emotionStats.average_depression_score?.toFixed(1)}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Tendință</div>
              <div className={`stat-value ${emotionStats.trend > 0 ? 'negative' : emotionStats.trend < 0 ? 'positive' : ''}`}>
                {emotionStats.trend > 0 ? <TrendUpIcon /> : emotionStats.trend < 0 ? <TrendDownIcon /> : <TrendConstantIcon />}
                <span style={{ marginLeft: '4px' }}>
                  {emotionStats.trend > 0 ? 'Risc Crescut' : emotionStats.trend < 0 ? 'Îmbunătățit' : 'Constant'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Istoricul Analizelor */}
      <div className="face-history">
        <div className="history-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
          <h3 style={{ margin: 0 }}><CalendarIcon /> Istoricul Analizelor Faciale</h3>
          {faceHistory.length > 0 && (
            <button 
              className="btn btn-danger delete-history-btn" 
              onClick={deleteFaceHistory} 
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
        {faceHistory.length > 0 ? (
          <div className="history-grid">
            {faceHistory.map((item, i) => (
              <div key={i} className="history-card">
                <div className="history-image">
                  <img src={item.image_url} alt="History snapshot" />
                </div>
                <div className="history-info">
                  <div className="history-time">
                    {new Date(item.timestamp).toLocaleDateString('ro-RO', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </div>
                  <div className="history-emotion">
                    <strong>Emoție:</strong> {item.dominant_emotion}
                  </div>
                  <div className="history-score">
                    <strong>Scor Risc:</strong> {item.depression_score}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">Nu sunt analize anterioare</p>
        )}
      </div>

      {/* Grafic Emotii in Timp */}
      {faceHistory.length > 3 && (
        <div className="emotion-chart">
          <h3><ChartIcon /> Evoluția Emotiilor</h3>
          <div className="chart-container">
            <div className="simple-chart">
              {faceHistory.slice(-10).map((item, i) => (
                <div key={i} className="chart-bar" title={`${item.dominant_emotion} - ${item.depression_score}`}>
                  <div
                    className="bar-fill"
                    style={{
                      height: `${item.depression_score * 2}px`,
                      backgroundColor:
                        item.depression_score > 70
                          ? '#e74c3c'
                          : item.depression_score > 40
                          ? '#f39c12'
                          : '#27ae60',
                    }}
                  />
                  <span className="bar-label">{(i + 1).toString().padStart(2, '0')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recomandari */}
      {isClinicalMode && analysisResult && (
        <div className="recommendations">
          <h3><LightbulbIcon /> Recomandări Personalizate</h3>
          <div className="recommendation-content">
            {analysisResult.overall_face_depression_score > 70 ? (
              <div className="recommendation-item warning">
                <p>
                  <strong><WarningIcon /> Atenție:</strong> Expresia facială sugerează stări emoționale negative semnificative. Vă recomandăm cu tărie să contactați un specialist în sănătate mentală.
                </p>
              </div>
            ) : analysisResult.overall_face_depression_score > 40 ? (
              <div className="recommendation-item info">
                <p>
                  <strong><InfoIcon /> Observație:</strong> Expresia facială indică unele semne de tristețe sau îngrijorare. Încercați să desfășurați activități recreative și să vorbiți cu prietenii apropiați.
                </p>
              </div>
            ) : (
              <div className="recommendation-item success">
                <p>
                  <strong><CheckIcon /> Stare Optimă:</strong> Expresia facială pare relaxată și pozitivă. Continuați să mențineți o atitudine echilibrată și un stil de viață sănătos.
                </p>
              </div>
            )}
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

      {/* Modal Confirmare Trimitere Poza */}
      {showConfirmModal && pendingImage && (
        <div className="ec-modal-overlay" onClick={() => { setShowConfirmModal(false); setPendingImage(null); setUploadedFileName(''); }}>
          <div className="ec-modal-content central-popup" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '420px' }}>
            <div className="ec-modal-header">
              <h3><CaptureIcon /> Confirmare Imagine</h3>
              <button className="ec-modal-close-btn" onClick={() => { setShowConfirmModal(false); setPendingImage(null); setUploadedFileName(''); }}>&times;</button>
            </div>
            <div className="ec-modal-body" style={{ textAlign: 'center' }}>
              <img src={pendingImage} alt="Preview" style={{ maxWidth: '100%', maxHeight: '280px', borderRadius: '10px', objectFit: 'contain', marginBottom: '15px', border: '1px solid rgba(255,255,255,0.08)' }} />
              <p style={{ margin: '0 0 20px 0', fontSize: '14px', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                Dorești să trimiți această fotografie pentru analiza facială?
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button 
                  className="btn btn-success" 
                  onClick={() => {
                    console.log('[Operation] User confirmed image submission');
                    setUploadedImage(pendingImage);
                    setShowConfirmModal(false);
                    setPendingImage(null);
                    analyzeFace(pendingImage);
                  }}
                  style={{ padding: '10px 28px', fontSize: '14px', fontWeight: '600' }}
                >
                  <CheckIcon /> Trimite pentru Analiză
                </button>
                <button 
                  className="btn btn-danger" 
                  onClick={() => {
                    console.log('[Operation] User cancelled image submission');
                    setShowConfirmModal(false);
                    setPendingImage(null);
                    setUploadedFileName('');
                    if (fileInputRef.current) fileInputRef.current.value = '';
                    triggerToast('info', 'Imaginea a fost anulată.');
                  }}
                  style={{ padding: '10px 28px', fontSize: '14px', fontWeight: '600' }}
                >
                  <CloseIcon /> Renunță
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal / Popup Centrat pentru Context Facial Extins */}
      {showReportModal && dashboardStats && (
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
                Context Facial Extins
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
                      dashboardStats.face_average >= 70 
                        ? '#f7768e' 
                        : dashboardStats.face_average >= 40 
                        ? '#ff9f43' 
                        : '#73daca'
                    }
                    strokeDasharray={`${2 * Math.PI * 54}`}
                    strokeDashoffset={`${2 * Math.PI * 54 * (1 - dashboardStats.face_average / 100)}`}
                    transform="rotate(-90 65 65)"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="central-gauge-score" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: '800', fontSize: '28px', color: '#fff', letterSpacing: '-0.02em' }}>
                  {Math.round(dashboardStats.face_average)}%
                </div>
              </div>
              
              <div className="ec-modal-risk-badge" style={{
                background: dashboardStats.face_average >= 70 ? 'rgba(247, 118, 142, 0.12)' : dashboardStats.face_average >= 40 ? 'rgba(255, 159, 67, 0.12)' : 'rgba(115, 218, 202, 0.12)',
                color: dashboardStats.face_average >= 70 ? '#f7768e' : dashboardStats.face_average >= 40 ? '#ff9f43' : '#73daca',
                border: `1px solid ${dashboardStats.face_average >= 70 ? 'rgba(247, 118, 142, 0.25)' : dashboardStats.face_average >= 40 ? 'rgba(255, 159, 67, 0.25)' : 'rgba(115, 218, 202, 0.25)'}`,
                display: 'inline-block',
                margin: '5px auto 20px auto',
                padding: '6px 18px',
                borderRadius: '30px',
                fontWeight: '700',
                fontSize: '12px',
                letterSpacing: '0.5px'
              }}>
                {dashboardStats.face_average >= 70 ? 'NIVEL DE ALERTĂ RIDICAT' : dashboardStats.face_average >= 40 ? 'NIVEL DE ALERTĂ MODERAT' : 'NIVEL DE ALERTĂ SCĂZUT'}
              </div>

              <div className="ec-breakdown-details" style={{ marginTop: '20px', padding: '20px', background: 'rgba(255,255,255,0.01)', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.04)', textAlign: 'left' }}>
                <h4 style={{ margin: '0 0 18px 0', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '1px', color: '#bb9af7', fontWeight: '700' }}>Dimensiuni Faciale</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  {/* Tristețe */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Tristețe</span>
                      <strong style={{ color: '#7aa2f7' }}>{analysisResult?.depression_indicators?.sadness || 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.depression_indicators?.sadness || 0}%`, background: '#7aa2f7', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  {/* Anxietate */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Anxietate</span>
                      <strong style={{ color: '#bb9af7' }}>{analysisResult?.depression_indicators?.anxiety || 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.depression_indicators?.anxiety || 0}%`, background: '#bb9af7', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  {/* Iritabilitate */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Iritabilitate</span>
                      <strong style={{ color: '#f7768e' }}>{analysisResult?.depression_indicators?.irritability || 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.depression_indicators?.irritability || 0}%`, background: '#f7768e', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  {/* Anhedonie */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Anhedonie</span>
                      <strong style={{ color: '#ff9f43' }}>{analysisResult?.depression_indicators?.anhedonia || 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${analysisResult?.depression_indicators?.anhedonia || 0}%`, background: '#ff9f43', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  {/* Indiferență */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12.5px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Indiferență</span>
                      <strong style={{ color: '#73daca' }}>{(analysisResult?.depression_indicators?.indifference !== undefined ? analysisResult?.depression_indicators?.indifference : analysisResult?.depression_indicators?.dissociation) || 0}%</strong>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${(analysisResult?.depression_indicators?.indifference !== undefined ? analysisResult?.depression_indicators?.indifference : analysisResult?.depression_indicators?.dissociation) || 0}%`, background: '#73daca', borderRadius: '3px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="ec-modal-report-text" style={{ marginTop: '25px', textAlign: 'left' }}>
                <h4 style={{ fontSize: '13px', color: '#ffb86c', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '700' }}>Evaluare Mimico-Facială</h4>
                <div style={{
                  padding: '16px 20px',
                  background: 'rgba(255,255,255,0.01)',
                  border: '1px solid rgba(255,255,255,0.03)',
                  borderLeft: `4px solid ${
                    dashboardStats.face_average >= 70 
                      ? '#f7768e' 
                      : dashboardStats.face_average >= 40 
                      ? '#ff9f43' 
                      : '#73daca'
                  }`,
                  borderRadius: '0 12px 12px 0'
                }}>
                  <p style={{ margin: 0, fontSize: '13.5px', lineHeight: '1.7', color: 'rgba(255, 255, 255, 0.8)' }}>
                    {(() => {
                      const faceAvg = Math.round(dashboardStats.face_average);
                      const sadness = analysisResult?.depression_indicators?.sadness || 0;
                      const anxiety = analysisResult?.depression_indicators?.anxiety || 0;
                      const irritability = analysisResult?.depression_indicators?.irritability || 0;
                      const anhedonia = analysisResult?.depression_indicators?.anhedonia || 0;
                      const indifference = (analysisResult?.depression_indicators?.indifference !== undefined ? analysisResult?.depression_indicators?.indifference : analysisResult?.depression_indicators?.dissociation) || 0;
                      
                      const isApropiat = dashboardStats.tip_detectie === 'apropiat';
                      
                      if (isApropiat) {
                        if (faceAvg < 20) {
                          return `Expresiile faciale ale persoanei apropiate indică o stare generală relaxată și pozitivă. Emoțiile pozitive sunt dominante, iar markerii de tristețe sau iritabilitate sunt extrem de reduși. Expresia mimic-facială este stabilă.`;
                        } else if (faceAvg < 35) {
                          return `Se observă o mimică facială stabilă la persoana apropiată. Totuși, am detectat mici micro-expresii izolate de tristețe (${sadness}%) sau iritabilitate (${irritability}%) în trăsăturile feței, cel mai probabil temporare.`;
                        } else if (faceAvg < 50) {
                          return `Analiza mimic-facială a persoanei apropiate relevă o încărcătură emoțională moderată. Există semne clare de ${sadness >= Math.max(irritability, anxiety, indifference) ? `tristețe (${sadness}%) în privire și colțurile gurii` : irritability >= Math.max(anxiety, indifference) ? `iritabilitate și micro-tensiune musculară (${irritability}%) în zona sprâncenelor` : anxiety >= indifference ? `anxietate și îngrijorare evidentă (${anxiety}%)` : `indiferență mimic-facială (${indifference}%)`}. Se observă o tensiune emoțională evidentă.`;
                        } else if (faceAvg < 70) {
                          return `Se observă o stare de suferință emoțională pronunțată în expresiile faciale ale persoanei apropiate. Se evidențiază semne clare de ${sadness >= Math.max(irritability, anxiety, indifference) ? `tristețe profundă și persistentă (${sadness}%)` : irritability >= Math.max(anxiety, indifference) ? `iritabilitate marcată, tensiune musculară facială și rigiditate (${irritability}%)` : anxiety >= indifference ? `anxietate severă și îngrijorare constantă (${anxiety}%)` : `aplatizare mimico-facială severă / lipsă de reacție emoțională (${indifference}%)`}.`;
                        } else {
                          return `Vulnerabilitate mimic-facială critică detectată la persoana apropiată. Indicatorul principal arată ${sadness >= Math.max(irritability, anxiety, indifference, anhedonia) ? `o tristețe profundă și intensă (${sadness}%)` : irritability >= Math.max(anxiety, indifference, anhedonia) ? `o iritabilitate extrem de ridicată și rigiditate facială (${irritability}%)` : anxiety >= indifference ? `o anxietate severă cu panică vizibilă (${anxiety}%)` : `o lipsă totală de vitalitate și anhedonie marcată (${anhedonia}%)`}. Se observă o suferință severă pe chipul său.`;
                        }
                      } else {
                        if (faceAvg < 20) {
                          return `Chipul tău transmite liniște și o stare de bine. Expresiile tale sunt deschise și relaxate, iar markerii de oboseală sau îngrijorare sunt extrem de scăzuți. Continuă să zâmbești și să ai grijă de tine!`;
                        } else if (faceAvg < 35) {
                          return `Expresia feței tale pare în general stabilă și senină. Am observat doar mici urme trecătoare de oboseală sau ușoară îngrijorare (${sadness || irritability}%), dar nimic care să îți strice echilibrul. Încearcă să îți oferi un scurt moment de respiro.`;
                        } else if (faceAvg < 50) {
                          return `Se simte o ușoară încărcătură emoțională sau oboseală pe chipul tău. Analiza feței arată o prezență a ${sadness >= Math.max(irritability, anxiety, indifference) ? `unei stări de tristețe calde (${sadness}%)` : irritability >= Math.max(anxiety, indifference) ? `unei mici tensiuni sau frustrări (${irritability}%)` : anxiety >= indifference ? `unei stări de neliniște sau îngrijorare (${anxiety}%)` : `unei stări de detașare sau lipsă de energie (${indifference}%)`}. Fii blând cu tine în aceste momente și odihnește-te.`;
                        } else if (faceAvg < 70) {
                          return `Chipul tău reflectă o perioadă mai dificilă și o oboseală emoțională destul de intensă. Se observă destul de clar semne de ${sadness >= Math.max(irritability, anxiety, indifference) ? `tristețe adâncă (${sadness}%)` : irritability >= Math.max(anxiety, indifference) ? `tensiune persistentă și încruntare (${irritability}%)` : anxiety >= indifference ? `neliniște profundă (${anxiety}%)` : `detașare emoțională și oboseală mimică (${indifference}%)`}. Meriți să te oprești puțin din tot, să respiri adânc și să vorbești cu cineva drag.`;
                        } else {
                          return `Chipul tău arată o vulnerabilitate și o suferință emoțională profundă în acest moment. Indicatorul de ${sadness >= Math.max(irritability, anxiety, indifference, anhedonia) ? `tristețe (${sadness}%)` : irritability >= Math.max(anxiety, indifference, anhedonia) ? `tensiune severă (${irritability}%)` : anxiety >= indifference ? `îngrijorare intensă (${anxiety}%)` : `lipsă de bucurie și oboseală extremă (${anhedonia}%)`} este ridicat. Te rugăm să nu treci singur prin asta; este complet în regulă să ceri o îmbrățișare sau un sfat de la cineva apropiat care te prețuiește.`;
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
        </div>
      )}
    </div>
  );
};

export default EnhancedFaceComponent;
