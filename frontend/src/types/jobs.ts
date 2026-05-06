export type JobStatus = 'idle' | 'queued' | 'processing' | 'done' | 'failed'

export type AudioJobCreateResponse = {
  job_id: string
  status: string
  filename: string
}

export type AudioJobResult = {
  original_filename: string
  stored_file_path: string
  transcript: string
  assistant_response: string
}

export type JobStatusResponse = {
  job_id: string
  status: string
  result: unknown | null
}
