import { useState, useRef, useEffect } from 'react';

export default function CameraCapture() {
  // --- State ---
  // We use "union types" (e.g., MediaStream | null) to tell TypeScript
  // that these variables can be one of several types.
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [photo, setPhoto] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);  
  const [lolaReply, setLolaReply] = useState<string | null>(null);
  // --- Refs ---
  // We provide a "generic type" to useRef to tell it what kind
  // of HTML element it will be referencing.
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // --- Effect for Cleanup ---
  useEffect(() => {
    // This cleanup function runs when the component unmounts
    return () => {
      if (stream) {
        console.log("Cleaning up camera stream...");
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]); // Re-run this effect if the 'stream' state changes

  // --- Function 1: Open Camera ---
  const openCamera = async () => {
    // Reset any previous photo or error
    setPhoto(null);
    setError(null);

    try {
      // Request camera access
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' }, // Use 'environment' for back camera
        audio: false,
      });

      // 1. Set the stream in state
      setStream(newStream);

      // 2. Link the stream to the <video> element
      // We check `videoRef.current` to make sure it's not null
      if (videoRef.current) {
        videoRef.current.srcObject = newStream;
        videoRef.current.play();
      }
    } catch (err) {
      // Handle errors (e.g., user denies permission)
      console.error("Error accessing camera:", err);
      // We type-check the error to be safe
      if (err instanceof Error) {
        if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
          setError("Camera permission was denied. Please allow camera access in your browser settings.");
        } else {
          setError(`Could not access the camera: ${err.message}`);
        }
      } else {
        setError("An unknown error occurred while accessing the camera.");
      }
    }
  };

  // --- Function 2: Take Photo ---
  const takePhoto = async () => {
    // We check our refs and the stream to make TypeScript happy
    if (!videoRef.current || !canvasRef.current || !stream) {
      console.error("Video ref, canvas ref, or stream not found");
      return;
    }

    // 1. Get the video's dimensions
    const video = videoRef.current;
    const width = video.videoWidth;
    const height = video.videoHeight;

    // 2. Set the canvas to the same dimensions
    const canvas = canvasRef.current;
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d')!; 
    context.drawImage(video, 0, 0, width, height);
    const dataUrl = canvas.toDataURL('image/png');
    setPhoto(dataUrl);
    closeCamera();

    setIsSending(true);
    setError(null);
    setLolaReply(null);

    try {
      const blob = await (await fetch(dataUrl)).blob();
      const formData = new FormData();
      formData.append('photo', blob, 'photo.png');
  
      const response = await fetch("/api/upload-image", { method: "POST", body: formData });
  
      if (!response.ok) throw new Error("Lola didn't get the photo.");
  
      const arrayBuffer = await response.arrayBuffer();
      const audioBlob = new Blob([arrayBuffer], { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(audioBlob);
      setLolaReply(audioUrl);
    } catch (err) {
      console.error("Error sending photo to Lola:", err);
      setError("There was an error sending the photo to Lola.");
    } finally {
      setIsSending(false);
    }

  };

  // --- Function 3: Close Camera (Helper) ---
  const closeCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    setStream(null);
  };

  // --- Function 4: Retake Photo ---
  const retakePhoto = () => {
    setPhoto(null);
    setError(null);
  };

  const sendToLola = async () => {
    if (!photo) return;
    setIsSending(true);
    setError(null);
    setLolaReply(null);

    try {
      const blob = await (await fetch(photo)).blob();
      const formData = new FormData();
      formData.append('photo', blob, 'photo.png');

      const response = await fetch("/api/upload-image", {
      method: "POST",
      body: formData,
    });

      if (!response.ok) { throw new Error("Lola didn't get the photo."); }
        
      const arrayBuffer = await response.arrayBuffer();
      const audioBlob = new Blob([arrayBuffer], { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(audioBlob);
      setLolaReply(audioUrl);

    } catch (err) {
      console.error("Error sending photo to Lola:", err);
      setError("There was an errror sending the photo to Lola.");
    } finally {
      setIsSending(false);
    }
  };


      

  // --- Render ---
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-[542px] p-4 mx-auto">
      
      {/* --- Error Message Display --- */}
      {error && (
        <div className="p-3 mb-4 text-red-800 bg-red-100 border border-red-400 rounded-lg" role="alert">
          <span className="font-medium">Error:</span> {error}
        </div>
      )}

      {/* --- The "Smart" Button --- */}
      <div className="w-full mb-4">
        {!photo && (
          <button
            onClick={() => {
              if (stream) {
                takePhoto();
              } else {
                openCamera();
              }
            }}
            disabled={isSending}
            className={`active:scale-95 active:translate-y-[1px] shadow-lg cursor-pointer 
              w-full px-4 py-4 text-white rounded-full shadow-lg transition-all duration-200 
              hover:scale-110 ${
              stream
                ? 'bg-red-500 hover:bg-red-600' // "Take Photo" style
                : 'bg-gradient-to-b from-amber-400 to-amber-600' // "Open Camera" style
            }`}
          >
            {stream ? '📸 Take The Photo' : '📷 Send a Photo to Lola'}
          </button>
        )}

        {photo && (
           <button
            onClick={retakePhoto}
            className="active:scale-95 active:translate-y-[1px] cursor-pointer w-full px-4 py-4 
            text-white bg-green-500 rounded-full shadow-lg transition-all duration-200 
            hover:bg-green-600"
          >
            🔄 Retake Photo
          </button>
        )}
      </div>

      {/* --- Video Feed --- */}
      <div className={`w-full overflow-hidden border-2 border-gray-300 rounded-lg shadow-md ${stream ? 'block' : 'hidden'}`}>
        <video
          ref={videoRef}
          autoPlay
          playsInline // Important for iOS
          muted     // Important to prevent audio feedback
          className="w-full h-auto"
        />
      </div>

      {/* --- Hidden Canvas --- */}
      <canvas ref={canvasRef} className="hidden" />

      {/* --- Photo Preview --- */}
      {photo && (
        <div className="mt-4">
          <h3 className="text-xl font-semibold text-center">Your Photo:</h3>
          <img
            src={photo}
            alt="Captured photo"
            className="w-full h-auto mt-2 border-4 border-green-500 rounded-lg shadow-md"
          />
        </div>
      )}

      {isSending && (
        <p className="mt-4 text-gray-600 font-medium">Sending photo to Lola...</p>
      )}

    {lolaReply && (
      <div className="mt-6 flex flex-col items-center space-y-3">
        <p className="text-lg font-semibold">🎧 Lola’s Response:</p>
        <audio src={lolaReply} autoPlay className="w-full max-w-md" />
      </div>
    )}
    </div>
  );
}