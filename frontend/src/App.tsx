import { useEffect, useRef, useState } from 'react'

import ConversationResult from './components/ConversationResult'
import VoiceRecorder from './components/VoiceRecorder'
import { useAudioRecorder } from './hooks/useAudioRecorder'
import { useJobPolling } from './hooks/useJobPolling'
import type { AudioJobCreateResponse } from './types/jobs'
import './App.css'

function getExtensionFromMimeType(mimeType: string): string {
  const normalized = mimeType.toLowerCase()
  if (normalized.includes('wav')) {
    return 'wav'
  }
  if (normalized.includes('mpeg') || normalized.includes('mp3')) {
    return 'mp3'
  }
  if (normalized.includes('mp4') || normalized.includes('m4a')) {
    return 'm4a'
  }
  if (normalized.includes('ogg')) {
    return 'ogg'
  }
  return 'webm'
}

function App() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState<boolean>(false)
  const [uploadError, setUploadError] = useState<string>('')
  const [playbackError, setPlaybackError] = useState<string>('')
  const [recordingLabel, setRecordingLabel] = useState<string>('No recording yet')

  const {
    isRecording,
    recorderError,
    isRecorderSupported,
    startRecording,
    stopRecording,
  } = useAudioRecorder()

  const { status, result, error: pollingError, isProcessing } = useJobPolling(jobId)

  const audioPlaybackRef = useRef<HTMLAudioElement | null>(null)

  const uploadRecordedAudio = async (audioBlob: Blob) => {
    const extension = getExtensionFromMimeType(audioBlob.type)
    const filename = `recording-${Date.now()}.${extension}`
    const file = new File([audioBlob], filename, {
      type: audioBlob.type || 'audio/webm',
    })

    setIsUploading(true)
    setUploadError('')
    setPlaybackError('')
    setJobId(null)
    setRecordingLabel(filename)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/jobs/audio', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let detail = ''
        try {
          const errorPayload = (await response.json()) as { detail?: string }
          detail = errorPayload.detail ?? ''
        } catch {
          detail = ''
        }

        const suffix = detail ? `: ${detail}` : ''
        throw new Error(`HTTP ${response.status}${suffix}`)
      }

      const payload = (await response.json()) as AudioJobCreateResponse
      setJobId(payload.job_id)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setUploadError(`Failed to upload audio: ${message}`)
    } finally {
      setIsUploading(false)
    }
  }

  const handleStartRecording = async () => {
    setUploadError('')
    setPlaybackError('')
    await startRecording()
  }

  const handleStopRecording = async () => {
    setUploadError('')
    setPlaybackError('')
    try {
      const audioBlob = await stopRecording()
      await uploadRecordedAudio(audioBlob)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown recording error'
      setUploadError(`Failed to finalize recording: ${message}`)
    }
  }

  useEffect(() => {
    if (status !== 'done' || !result?.assistant_audio_url) {
      return
    }

    const audioUrl = `http://localhost:8000${result.assistant_audio_url}`
    if (audioPlaybackRef.current) {
      audioPlaybackRef.current.pause()
      audioPlaybackRef.current = null
    }

    const audio = new Audio(audioUrl)
    audioPlaybackRef.current = audio
    audio.play().catch(() => {
      setPlaybackError('Unable to autoplay AI audio. Please allow audio playback and retry.')
    })

    return () => {
      audio.pause()
    }
  }, [status, result])

  useEffect(() => {
    return () => {
      if (audioPlaybackRef.current) {
        audioPlaybackRef.current.pause()
        audioPlaybackRef.current = null
      }
    }
  }, [])

  return (
    <main className="app">
      <h1>AI Voice Agent Demo</h1>

      <VoiceRecorder
        isRecording={isRecording}
        isUploading={isUploading}
        isProcessing={isProcessing}
        isRecorderSupported={isRecorderSupported}
        recordingError={recorderError}
        recordingLabel={recordingLabel}
        onStart={handleStartRecording}
        onStop={handleStopRecording}
      />

      <ConversationResult
        jobId={jobId}
        status={status}
        result={result}
        isUploading={isUploading}
        isProcessing={isProcessing}
      />

      <section className="panel">
        <h2>Errors</h2>
        <p className="error">
          {uploadError || pollingError || playbackError || 'No errors.'}
        </p>
      </section>
    </main>
  )
}

export default App
