import { useEffect, useState } from 'react'

import type { AudioJobResult, JobStatus, JobStatusResponse } from '../types/jobs'

type UseJobPollingResult = {
  status: JobStatus
  result: AudioJobResult | null
  error: string
  isProcessing: boolean
}

const POLLING_INTERVAL_MS = 2000

function toAudioJobResult(value: unknown): AudioJobResult | null {
  if (typeof value !== 'object' || value === null) {
    return null
  }

  const record = value as Record<string, unknown>
  if (
    typeof record.original_filename !== 'string' ||
    typeof record.stored_file_path !== 'string' ||
    typeof record.transcript !== 'string' ||
    typeof record.assistant_response !== 'string' ||
    typeof record.assistant_audio_url !== 'string'
  ) {
    return null
  }

  return {
    original_filename: record.original_filename,
    stored_file_path: record.stored_file_path,
    transcript: record.transcript,
    assistant_response: record.assistant_response,
    assistant_audio_url: record.assistant_audio_url,
  }
}

export function useJobPolling(jobId: string | null): UseJobPollingResult {
  const [status, setStatus] = useState<JobStatus>('idle')
  const [result, setResult] = useState<AudioJobResult | null>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    if (!jobId) {
      setStatus('idle')
      setResult(null)
      setError('')
      return
    }

    let isActive = true
    let intervalId: number | undefined

    const stopPolling = () => {
      if (intervalId !== undefined) {
        window.clearInterval(intervalId)
        intervalId = undefined
      }
    }

    const pollJob = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/jobs/${jobId}`)
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const payload = (await response.json()) as JobStatusResponse
        if (!isActive) {
          return
        }

        if (payload.status === 'queued' || payload.status === 'processing') {
          setStatus(payload.status)
          return
        }

        if (payload.status === 'done') {
          const parsedResult = toAudioJobResult(payload.result)
          if (!parsedResult) {
            throw new Error('Job finished but result format is invalid.')
          }

          setStatus('done')
          setResult(parsedResult)
          stopPolling()
          return
        }

        if (payload.status === 'failed') {
          setStatus('failed')
          setError('Audio job failed during processing.')
          stopPolling()
          return
        }

        throw new Error(`Unknown job status: ${payload.status}`)
      } catch (err) {
        if (!isActive) {
          return
        }
        const message = err instanceof Error ? err.message : 'Unknown polling error'
        setStatus('failed')
        setError(`Failed to poll job status: ${message}`)
        stopPolling()
      }
    }

    setStatus('queued')
    setResult(null)
    setError('')
    pollJob()
    intervalId = window.setInterval(pollJob, POLLING_INTERVAL_MS)

    return () => {
      isActive = false
      stopPolling()
    }
  }, [jobId])

  return {
    status,
    result,
    error,
    isProcessing: status === 'queued' || status === 'processing',
  }
}
