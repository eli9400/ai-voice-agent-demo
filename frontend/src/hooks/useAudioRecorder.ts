import { useEffect, useRef, useState } from 'react'

type UseAudioRecorderResult = {
  isRecording: boolean
  recorderError: string
  isRecorderSupported: boolean
  startRecording: () => Promise<void>
  stopRecording: () => Promise<Blob>
}

const DEFAULT_AUDIO_MIME_TYPE = 'audio/webm'

function getPreferredRecorderMimeType(): string | undefined {
  if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) {
    return undefined
  }

  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus',
    'audio/ogg',
  ]

  return candidates.find((mimeType) => MediaRecorder.isTypeSupported(mimeType))
}

export function useAudioRecorder(): UseAudioRecorderResult {
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [recorderError, setRecorderError] = useState<string>('')

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  const isRecorderSupported =
    typeof window !== 'undefined' &&
    typeof navigator !== 'undefined' &&
    !!navigator.mediaDevices?.getUserMedia &&
    typeof MediaRecorder !== 'undefined'

  const stopTracks = () => {
    const stream = mediaStreamRef.current
    if (!stream) {
      return
    }
    stream.getTracks().forEach((track) => track.stop())
    mediaStreamRef.current = null
  }

  const resetRecorder = () => {
    mediaRecorderRef.current = null
    chunksRef.current = []
    setIsRecording(false)
    stopTracks()
  }

  const startRecording = async () => {
    setRecorderError('')
    if (!isRecorderSupported) {
      setRecorderError('Audio recording is not supported in this browser.')
      return
    }

    if (isRecording) {
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream
      chunksRef.current = []

      const preferredMimeType = getPreferredRecorderMimeType()
      const recorder = preferredMimeType
        ? new MediaRecorder(stream, { mimeType: preferredMimeType })
        : new MediaRecorder(stream)

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      recorder.onerror = () => {
        setRecorderError('Recording failed. Please try again.')
        resetRecorder()
      }

      mediaRecorderRef.current = recorder
      recorder.start()
      setIsRecording(true)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown microphone error'
      setRecorderError(`Unable to start recording: ${message}`)
      resetRecorder()
    }
  }

  const stopRecording = async () => {
    const recorder = mediaRecorderRef.current
    if (!recorder || recorder.state === 'inactive') {
      throw new Error('No active recording in progress.')
    }

    return await new Promise<Blob>((resolve, reject) => {
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || DEFAULT_AUDIO_MIME_TYPE,
        })
        resetRecorder()
        resolve(blob)
      }

      recorder.onerror = () => {
        setRecorderError('Recording failed while stopping.')
        resetRecorder()
        reject(new Error('Recording failed while stopping.'))
      }

      recorder.stop()
    })
  }

  useEffect(() => {
    return () => {
      try {
        const recorder = mediaRecorderRef.current
        if (recorder && recorder.state !== 'inactive') {
          recorder.stop()
        }
      } catch {
        // no-op cleanup safeguard
      }
      stopTracks()
    }
  }, [])

  return {
    isRecording,
    recorderError,
    isRecorderSupported,
    startRecording,
    stopRecording,
  }
}
