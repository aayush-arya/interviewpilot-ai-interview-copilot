/**
 * Voice interview mode: browser SpeechRecognition (STT) + speechSynthesis (TTS).
 * Tracks speaking metrics (WPM, filler words, duration) sent to the coach chain.
 *
 * Reliability notes:
 * - Mic permission is requested explicitly (getUserMedia) BEFORE starting
 *   recognition, so a denied permission surfaces as a visible `error` instead
 *   of a button that silently does nothing.
 * - Chrome ends recognition after silence; we auto-restart until the user stops.
 */
import { useCallback, useEffect, useRef, useState } from 'react';

const FILLERS = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'sort of', 'kind of'];

export interface VoiceMetrics {
  wpm: number;
  filler_count: number;
  duration_s: number;
}

interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: any) => void) | null;
  onend: (() => void) | null;
  onerror: ((event: any) => void) | null;
  start(): void;
  stop(): void;
}

function getRecognitionCtor(): (new () => SpeechRecognitionLike) | null {
  return (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition ?? null;
}

export function countFillers(text: string): number {
  const lower = ` ${text.toLowerCase()} `;
  return FILLERS.reduce((count, filler) => {
    const matches = lower.match(new RegExp(`[\\s,.]${filler}[\\s,.]`, 'g'));
    return count + (matches?.length ?? 0);
  }, 0);
}

const ERROR_MESSAGES: Record<string, string> = {
  'not-allowed': 'Microphone access was denied. Click the 🔒/🎤 icon in the address bar, allow the microphone, then try again.',
  'service-not-allowed': 'Speech recognition is blocked by the browser. Check site permissions.',
  'audio-capture': 'No microphone was found. Plug one in or check your input device settings.',
  network: 'Speech recognition needs an internet connection (the browser sends audio to its speech service).',
  aborted: '',   // user-initiated stop — not an error
  'no-speech': '', // benign; we auto-restart
};

export function useVoice() {
  const [supported] = useState(
    () => getRecognitionCtor() !== null && 'speechSynthesis' in window
  );
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const startTimeRef = useRef(0);
  const keepAliveRef = useRef(false);

  const speak = useCallback((text: string, onDone?: () => void) => {
    if (!('speechSynthesis' in window)) return onDone?.();
    window.speechSynthesis.cancel(); // interruption support
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.02;
    utterance.pitch = 1;
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => {
      setSpeaking(false);
      onDone?.();
    };
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    window.speechSynthesis?.cancel();
    setSpeaking(false);
  }, []);

  const startListening = useCallback(async () => {
    setError(null);
    const Ctor = getRecognitionCtor();
    if (!Ctor) {
      setError('Speech recognition is not supported in this browser — use Chrome or Edge.');
      return;
    }
    setStarting(true);
    stopSpeaking(); // user interrupts the interviewer by starting to talk

    // Force the permission prompt up-front so denial is visible, not silent.
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((t) => t.stop()); // only needed the permission
    } catch {
      setStarting(false);
      setError(ERROR_MESSAGES['not-allowed']);
      return;
    }

    const recognition = new Ctor();
    recognitionRef.current = recognition;
    keepAliveRef.current = true;
    startTimeRef.current = Date.now();
    setTranscript('');
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    let finalText = '';
    recognition.onresult = (event: any) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const chunk = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += chunk + ' ';
        else interim += chunk;
      }
      setTranscript((finalText + interim).trim());
    };
    recognition.onend = () => {
      // Chrome stops after silence; restart while the user hasn't clicked stop.
      if (keepAliveRef.current && recognitionRef.current === recognition) {
        try {
          recognition.start();
          return;
        } catch {
          /* fall through */
        }
      }
      setListening(false);
    };
    recognition.onerror = (event: any) => {
      const message = ERROR_MESSAGES[event?.error] ?? `Voice capture error: ${event?.error ?? 'unknown'}.`;
      if (message) {
        keepAliveRef.current = false;
        setError(message);
        setListening(false);
      }
    };
    try {
      recognition.start();
      setListening(true);
    } catch {
      setError('Could not start voice capture — another tab may be using the microphone.');
    } finally {
      setStarting(false);
    }
  }, [stopSpeaking]);

  const stopListening = useCallback((): VoiceMetrics => {
    keepAliveRef.current = false;
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    setListening(false);
    const durationS = Math.max(1, Math.round((Date.now() - startTimeRef.current) / 1000));
    const words = transcript.split(/\s+/).filter(Boolean).length;
    return {
      wpm: Math.round((words / durationS) * 60),
      filler_count: countFillers(transcript),
      duration_s: durationS,
    };
  }, [transcript]);

  useEffect(
    () => () => {
      keepAliveRef.current = false;
      recognitionRef.current?.stop();
      window.speechSynthesis?.cancel();
    },
    []
  );

  return {
    supported, listening, speaking, starting, error, transcript,
    setTranscript, speak, stopSpeaking, startListening, stopListening,
  };
}
