type VoiceRecorderProps = {
  isRecording: boolean
  isUploading: boolean
  isProcessing: boolean
  isRecorderSupported: boolean
  recordingError: string
  recordingLabel: string
  onStart: () => Promise<void>
  onStop: () => Promise<void>
}

function VoiceRecorder({
  isRecording,
  isUploading,
  isProcessing,
  isRecorderSupported,
  recordingError,
  recordingLabel,
  onStart,
  onStop,
}: VoiceRecorderProps) {
  const buttonText = isRecording ? 'Stop Recording' : 'Start Recording'
  const buttonDisabled = !isRecorderSupported || isUploading || isProcessing

  const handleToggleRecording = async () => {
    if (isRecording) {
      await onStop()
      return
    }
    await onStart()
  }

  return (
    <section className="panel">
      <h2>Voice Recorder</h2>
      <button type="button" onClick={handleToggleRecording} disabled={buttonDisabled}>
        {buttonText}
      </button>

      {isRecording ? (
        <p className="recording-indicator" role="status">
          Recording...
        </p>
      ) : null}

      <p className="meta">Last recording: {recordingLabel}</p>

      {!isRecorderSupported ? (
        <p className="error">This browser does not support microphone recording.</p>
      ) : null}

      {recordingError ? <p className="error">{recordingError}</p> : null}
    </section>
  )
}

export default VoiceRecorder
