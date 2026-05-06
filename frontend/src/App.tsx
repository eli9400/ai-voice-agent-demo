import { useState } from 'react'

import AudioUploader from './components/AudioUploader'
import JobResult from './components/JobResult'
import { useJobPolling } from './hooks/useJobPolling'
import type { AudioJobCreateResponse } from './types/jobs'
import './App.css'

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState<boolean>(false)
  const [uploadError, setUploadError] = useState<string>('')
  const [jobId, setJobId] = useState<string | null>(null)

  const { status, result, error: pollingError, isProcessing } = useJobPolling(jobId)

  const handleUploadAudio = async () => {
    if (!selectedFile) {
      setUploadError('Please choose an audio file before uploading.')
      return
    }

    setIsUploading(true)
    setUploadError('')
    setJobId(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

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

  return (
    <main className="app">
      <h1>AI Voice Agent Demo</h1>

      <AudioUploader
        selectedFile={selectedFile}
        isUploading={isUploading}
        isProcessing={isProcessing}
        onFileChange={setSelectedFile}
        onUpload={handleUploadAudio}
      />

      <JobResult
        jobId={jobId}
        status={status}
        result={result}
        isProcessing={isProcessing}
      />

      <section className="panel">
        <h2>Errors</h2>
        <p className="error">
          {uploadError || pollingError || 'No errors.'}
        </p>
      </section>
    </main>
  )
}

export default App
