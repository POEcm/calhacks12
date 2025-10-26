export {}; // make it a module

declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
  interface SpeechRecognitionEvent extends Event {
    results: {
      [index: number]: { [index: number]: { transcript: string } };
    };
  }
  
  interface SpeechRecognitionErrorEvent extends Event {
    error: string;
  }
  
}
