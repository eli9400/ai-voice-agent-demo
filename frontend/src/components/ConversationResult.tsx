import type { AudioJobResult, JobStatus } from '../types/jobs'

type ConversationResultProps = {
  jobId: string | null
  status: JobStatus
  result: AudioJobResult | null
  isUploading: boolean
  isProcessing: boolean
}

function ConversationResult({
  jobId,
  status,
  result,
  isUploading,
  isProcessing,
}: ConversationResultProps) {
  const statusText = (() => {
    if (isUploading) {
      return 'Uploading audio...'
    }
    if (isProcessing || status === 'queued' || status === 'processing') {
      return 'Processing...'
    }
    if (status === 'done') {
      return 'Done'
    }
    if (status === 'failed') {
      return 'Failed'
    }
    return 'Idle'
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
        <p>{result?.transcript ?? 'Transcript will appear here.'}</p>
      </section>

      <section className="panel">
        <h2>AI Response</h2>
        <p>{result?.assistant_response ?? 'Assistant response will appear here.'}</p>
      </section>
    </>
  )
}

export default ConversationResult
