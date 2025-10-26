"use client";
import { useState, useRef, useEffect } from "react";
import CameraCapture from "@/components/CameraCapture";
import { MdMic } from "react-icons/md";

export default function AudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [replyAudio, setReplyAudio] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
// Ref for the MediaRecorder object
const mediaRecorderRef = useRef<MediaRecorder | null>(null);

// Ref to store the audio "chunks" (pieces)
const audioChunksRef = useRef<Blob[]>([]);

const handleStartRecording = async () => {
  try {
    // 1. Ask for permission and get the audio stream
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    setIsRecording(true);
    audioChunksRef.current = []; // Clear previous chunks

    // 2. Create the MediaRecorder instance
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;

    // 3. Save chunks as they become available
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };

    // 4. When recording stops, combine the chunks
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      setAudioBlob(blob);

      // Stop the microphone tracks (turns off the "recording" light)
      stream.getTracks().forEach((track) => track.stop());
    };

    // 5. Start recording
    mediaRecorder.start();

  } catch (error) {
    console.error("Error accessing the microphone:", error);
  }
};

const handleStopRecordingAndSend = () => {
  if (mediaRecorderRef.current && isRecording) {
    mediaRecorderRef.current.onstop = async () => {
      const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      setAudioBlob(blob);

      // Stop the microphone tracks
      mediaRecorderRef.current?.stream.getTracks().forEach(track => track.stop());

      // Immediately send the audio
      await handleSendAudio(blob);
    };

    mediaRecorderRef.current.stop();
    setIsRecording(false);
  }
};

const handleSendAudio = async (blob: Blob) => {
  const formData = new FormData();
  formData.append("audio", blob, "recording.wav");

  try {
    setIsSending(true);

    const response = await fetch("/api/upload-audio", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      alert("Error uploading the audio.");
      return;
    }

    const arrayBuffer = await response.arrayBuffer();
    const replyBlob = new Blob([arrayBuffer], { type: "audio/wav" });
    const url = URL.createObjectURL(replyBlob);
    setReplyAudio(url);
  } catch (error) {
    console.error("Error in fetch:", error);
  } finally {
    setIsSending(false);
  }
  };


  return (

    <div className="min-h-full h-screen flex flex-col justify-center items-center text-white bg-animated-gradient animate-gradient">

        <p className="bg-clip-text text-transparent 
        bg-gradient-to-r from-amber-200 via-yellow-100 to-white animate-shimmer 
        font-serif text-[90px] font-regular pb-1">
          cookingLola
        </p>
        <p className="font-serif text-lg font-light pb-4">
          Talk to Lola while you cook! 🍳
        </p>
      <div className="w-full max-w-lg">
        <button className="active:scale-95 active:translate-y-[1px] cursor-pointer w-full
        py-4 px-4
        bg-gradient-to-b from-amber-400 to-amber-600
        hover:bg-[#e1b474] hover:scale-110
        rounded-full transition-all shadow-lg"
          onClick={isRecording ? handleStopRecordingAndSend : handleStartRecording}
        >
          {isRecording ? "Listening..." : "🧑‍🍳 How can Lola help?"}
        </button>
      </div>

    {isRecording && (
      <div className="flex flex-col items-center mt-4">
        <div className="relative flex items-center justify-center">
          <div className="absolute w-8 h-8 rounded-full bg-red-500/30 animate-ping" />
          <MdMic className="text-red-500 w-8 h-8 animate-pulse" />
        </div>
        <p className="mt-2 text-sm opacity-75">Recording...</p>
      </div>
    )}

    {replyAudio && (
    <div className="flex flex-col items-center space-y-2">
      <p className="text-lg font-semibold">🎧 Lola’s Response:</p>
      <audio src={replyAudio} autoPlay />
    </div>
    )}

    <CameraCapture />

    </div>


  );

}
