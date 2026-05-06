import type { ChangeEvent } from 'react'

type AudioUploaderProps = {
  selectedFile: File | null
  isUploading: boolean
  isProcessing: boolean
  onFileChange: (file: File | null) => void
  onUpload: () => void
}

function AudioUploader({
  selectedFile,
  isUploading,
  isProcessing,
  onFileChange,
  onUpload,
}: AudioUploaderProps) {
  const handleFileInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0] ?? null
    onFileChange(file)
  }

  return (
    <section className="panel">
      <h2>Audio Upload</h2>
      <input
        type="file"
        accept="audio/*,.mp3,.wav,.m4a,.webm,.ogg"
        onChange={handleFileInputChange}
      />
      <p className="meta">
        Selected file: {selectedFile ? selectedFile.name : 'No file selected'}
      </p>
      <button
        type="button"
        onClick={onUpload}
        disabled={!selectedFile || isUploading || isProcessing}
      >
        {isUploading ? 'Uploading...' : 'Upload Audio'}
      </button>
    </section>
  )
}

export default AudioUploader
