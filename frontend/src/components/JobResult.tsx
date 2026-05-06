import type { AudioJobResult, JobStatus } from '../types/jobs'

type JobResultProps = {
  jobId: string | null
  status: JobStatus
  result: AudioJobResult | null
  isProcessing: boolean
}

function JobResult({ jobId, status, result, isProcessing }: JobResultProps) {
  const statusText = (() => {
    if (!jobId) {
      return 'No active job yet.'
    }
    if (status === 'queued' || status === 'processing' || isProcessing) {
      return 'Processing...'
    }
    if (status === 'done') {
      return 'Done'
    }
    if (status === 'failed') {
      return 'Failed'
    }
    return 'Waiting'
  })()

  return (
    <>
      <section className="panel">
        <h2>Job Status</h2>
        <p className="meta">Job ID: {jobId ?? 'N/A'}</p>
        <p className="status">{statusText}</p>
      </section>

      <section className="panel">
        <h2>Transcript</h2>
        <p>{result?.transcript ?? 'Transcript will appear here when ready.'}</p>
      </section>

      <section className="panel">
        <h2>Assistant Response</h2>
        <p>
          {result?.assistant_response ??
            'Assistant response will appear here when ready.'}
        </p>
      </section>
    </>
  )
}

export default JobResult
