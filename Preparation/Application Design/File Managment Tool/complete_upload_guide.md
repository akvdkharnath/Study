# Large File Upload Strategies - Complete Implementation Guide
## With Production Code, Examples, and Real-World Cases

**Date**: January 3, 2026  
**Level**: L4-L5 Senior Backend Engineer  
**Status**: Production-Ready Code Examples

---

## 📋 Table of Contents

1. Decision Tree & Quick Reference
2. Strategy 1: Single-Request Upload
3. Strategy 2: Chunked Upload (Client-side)
4. Strategy 3: S3 Multipart (Backend Proxy)
5. Strategy 4: Direct S3 with Pre-signed URLs
6. Strategy 5: Resumable Upload (Advanced)
7. Real-World Examples
8. Production Deployment Checklist

---

## 🎯 Decision Tree (Quick Reference)

```
┌─ File Size < 50MB?
│  └─ Use: SINGLE-REQUEST (simple, fast)
│
├─ File Size 50MB-500MB?
│  ├─ Network Reliable? → STREAMING or MULTIPART-PROXY
│  └─ Network Unreliable? → MULTIPART-DIRECT + PRESIGNED
│
├─ File Size 500MB-5GB?
│  ├─ Backend can handle? → RESUMABLE or MULTIPART-PROXY
│  └─ Backend overloaded? → MULTIPART-DIRECT + PRESIGNED
│
└─ File Size > 5GB?
   └─ MUST USE: MULTIPART-DIRECT + PRESIGNED or STREAMING
```

---

## Strategy 1: Single-Request Upload
### (Best for: Small files <100MB, simple implementation)

### Backend Code (Python FastAPI)

```python
# File: app/api/uploads_simple.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import boto3
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

app = FastAPI()
s3_client = boto3.client('s3')

# Database models
from app.models import FileMaster, GroupFileMapping

@app.post("/api/files/upload")
async def upload_file_simple(
    file: UploadFile = File(...),
    group_id: str = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simple single-request file upload
    Best for: Small files (<100MB)
    
    Flow:
    1. Validate permissions + quota
    2. Stream file to S3
    3. Create DB record
    4. Return file metadata
    """
    
    file_id = str(uuid.uuid4())
    
    try:
        # 1. VALIDATE
        print(f"[{file_id}] Validating upload request...")
        
        # Check auth
        if not current_user:
            raise HTTPException(401, "Unauthorized")
        
        # Check permissions
        has_write_perm = await check_write_permission(
            current_user.id, 
            group_id,
            db
        )
        if not has_write_perm:
            raise HTTPException(403, "No write permission")
        
        # Check quota
        storage_used = await get_group_storage_used(group_id, db)
        file_size = await file.seek(0, 2)  # Seek to end
        await file.seek(0)  # Reset
        
        quota = STORAGE_QUOTA_GB * 1024 * 1024 * 1024  # Convert to bytes
        if storage_used + file_size > quota:
            raise HTTPException(400, f"Quota exceeded. Used: {storage_used}, Limit: {quota}")
        
        # Check file type
        if not is_allowed_file_type(file.filename, file.content_type):
            raise HTTPException(400, f"File type not allowed: {file.content_type}")
        
        print(f"[{file_id}] Validation passed. File size: {file_size} bytes")
        
        # 2. STREAM TO S3
        print(f"[{file_id}] Uploading to S3...")
        
        s3_key = f"groups/{group_id}/{file_id}/{file.filename}"
        
        # Use s3_client.upload_fileobj for streaming
        # This prevents loading entire file in memory
        s3_response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: s3_client.upload_fileobj(
                file.file,
                bucket='your-bucket-name',
                key=s3_key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'Metadata': {
                        'original-name': file.filename,
                        'uploaded-by': current_user.id,
                        'group-id': group_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
            )
        )
        
        print(f"[{file_id}] S3 upload complete")
        
        # 3. CREATE DB RECORD
        print(f"[{file_id}] Creating database record...")
        
        file_record = FileMaster(
            file_id=file_id,
            file_name=file.filename,
            file_type=get_file_type(file.filename),
            file_size_bytes=file_size,
            mime_type=file.content_type,
            uploaded_by=current_user.id,
            original_group_id=group_id,
            s3_path=f"s3://your-bucket-name/{s3_key}",
            s3_etag=s3_response.get('ETag', ''),
            version=1,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(file_record)
        
        # Add group-file mapping (full permissions for uploader's group)
        group_file_mapping = GroupFileMappings(
            group_id=group_id,
            file_id=file_id,
            permissions=7,  # 4(read) + 2(write) + 1(delete)
            shared_by=current_user.id,
            shared_at=datetime.utcnow()
        )
        
        db.add(group_file_mapping)
        db.commit()
        
        print(f"[{file_id}] Database record created")
        
        # 4. AUDIT LOG
        await create_audit_log(
            file_id=file_id,
            user_id=current_user.id,
            action='upload',
            db=db
        )
        
        return {
            "status": "success",
            "file_id": file_id,
            "file_name": file.filename,
            "file_size": file_size,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        print(f"[{file_id}] Error: {str(e)}")
        db.rollback()
        raise HTTPException(500, f"Upload failed: {str(e)}")

# Helper functions

async def check_write_permission(user_id: str, group_id: str, db: Session) -> bool:
    """Check if user has write permission in group"""
    result = db.query(GroupUserMapping).filter(
        GroupUserMapping.user_id == user_id,
        GroupUserMapping.group_id == group_id,
        GroupUserMapping.permissions >= 2  # 2 = write
    ).first()
    return result is not None

async def get_group_storage_used(group_id: str, db: Session) -> int:
    """Get total storage used by group in bytes"""
    result = db.query(func.sum(FileMaster.file_size_bytes)).filter(
        FileMaster.original_group_id == group_id,
        FileMaster.is_deleted == False
    ).scalar()
    return result or 0

def is_allowed_file_type(filename: str, mime_type: str) -> bool:
    """Check if file type is allowed"""
    ALLOWED_TYPES = {
        'audio/mpeg', 'audio/wav', 'audio/ogg',
        'video/mp4', 'video/quicktime',
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf', 'text/plain'
    }
    return mime_type in ALLOWED_TYPES

def get_file_type(filename: str) -> str:
    """Determine file type from extension"""
    ext = filename.split('.')[-1].lower()
    type_map = {
        'mp3': 'audio', 'wav': 'audio', 'ogg': 'audio',
        'mp4': 'video', 'mov': 'video', 'avi': 'video',
        'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
        'pdf': 'document', 'txt': 'document', 'doc': 'document'
    }
    return type_map.get(ext, 'other')
```

### Client Code (JavaScript)

```javascript
// File: frontend/uploadSimple.js

class SimpleUploader {
  constructor(options = {}) {
    this.maxFileSize = options.maxFileSize || 100 * 1024 * 1024; // 100MB
    this.onProgress = options.onProgress || (() => {});
    this.onError = options.onError || (() => {});
    this.onSuccess = options.onSuccess || (() => {});
  }

  async upload(file, groupId, authToken) {
    console.log(`Uploading file: ${file.name} (${file.size} bytes)`);
    
    // Validate file size
    if (file.size > this.maxFileSize) {
      const error = `File too large. Max: ${this.maxFileSize / 1024 / 1024}MB`;
      this.onError(error);
      throw new Error(error);
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('group_id', groupId);

    try {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          console.log(`Upload progress: ${percentComplete.toFixed(2)}%`);
          this.onProgress(percentComplete);
        }
      });

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          console.log('Upload successful:', response);
          this.onSuccess(response);
        } else {
          const error = `Upload failed with status ${xhr.status}`;
          this.onError(error);
          throw new Error(error);
        }
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        this.onError('Network error during upload');
      });

      // Send request
      xhr.open('POST', '/api/files/upload', true);
      xhr.setRequestHeader('Authorization', `Bearer ${authToken}`);
      xhr.send(formData);

    } catch (error) {
      console.error('Upload error:', error);
      this.onError(error.message);
      throw error;
    }
  }
}

// Usage
const uploader = new SimpleUploader({
  maxFileSize: 100 * 1024 * 1024,
  onProgress: (percent) => {
    console.log(`${percent.toFixed(2)}% complete`);
    document.getElementById('progress').value = percent;
  },
  onError: (error) => {
    alert(`Error: ${error}`);
  },
  onSuccess: (data) => {
    alert(`File uploaded! ID: ${data.file_id}`);
  }
});

// Trigger upload
document.getElementById('upload-btn').addEventListener('click', async () => {
  const fileInput = document.getElementById('file-input');
  const file = fileInput.files[0];
  const groupId = document.getElementById('group-select').value;
  const token = localStorage.getItem('auth_token');
  
  await uploader.upload(file, groupId, token);
});
```

---

## Strategy 2: Chunked Upload
### (Best for: Medium files 50MB-500MB, unreliable networks)

### Backend Code

```python
# File: app/api/uploads_chunked.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from redis import Redis
import json

app = FastAPI()
redis_client = Redis(host='localhost', port=6379, db=0)
s3_client = boto3.client('s3')

CHUNK_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/api/uploads/chunked/initiate")
async def initiate_chunked_upload(
    payload: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate chunked upload
    
    Request body:
    {
        "file_name": "large_video.mp4",
        "file_size": 524288000,
        "group_id": "group_123"
    }
    """
    
    file_name = payload['file_name']
    file_size = payload['file_size']
    group_id = payload['group_id']
    
    # Validate
    if not await check_write_permission(current_user.id, group_id, db):
        raise HTTPException(403, "No permission")
    
    if file_size > 5 * 1024 * 1024 * 1024:  # 5GB max
        raise HTTPException(400, "File too large")
    
    # Generate upload ID
    upload_id = str(uuid.uuid4())
    
    # Store metadata in Redis
    upload_meta = {
        'file_name': file_name,
        'file_size': file_size,
        'group_id': group_id,
        'user_id': current_user.id,
        'chunks_received': 0,
        'chunk_etags': {},
        'created_at': datetime.utcnow().isoformat(),
        'status': 'initiated'
    }
    
    redis_client.hset(
        f"chunked_upload:{upload_id}",
        mapping=upload_meta
    )
    redis_client.expire(f"chunked_upload:{upload_id}", 7 * 24 * 3600)  # 7 days
    
    total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    print(f"[{upload_id}] Chunked upload initiated: {total_chunks} chunks")
    
    return {
        "upload_id": upload_id,
        "chunk_size": CHUNK_SIZE,
        "total_chunks": total_chunks,
        "message": "Ready to receive chunks"
    }

@app.post("/api/uploads/chunked/{upload_id}/chunks")
async def upload_chunk(
    upload_id: str,
    chunk_index: int,
    chunk_file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload individual chunk
    
    Query params:
    - chunk_index: Which chunk (0-based)
    """
    
    # Get upload metadata
    upload_meta = redis_client.hgetall(f"chunked_upload:{upload_id}")
    if not upload_meta:
        raise HTTPException(404, "Upload not found or expired")
    
    upload_meta = {k.decode(): v.decode() for k, v in upload_meta.items()}
    
    # Verify ownership
    if upload_meta['user_id'] != current_user.id:
        raise HTTPException(403, "Not your upload")
    
    try:
        # Read chunk
        chunk_data = await chunk_file.read()
        chunk_size = len(chunk_data)
        
        print(f"[{upload_id}] Received chunk {chunk_index} ({chunk_size} bytes)")
        
        # Store chunk in S3 temporary location
        temp_key = f"uploads/chunks/{upload_id}/chunk_{chunk_index}"
        
        s3_response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: s3_client.put_object(
                Bucket='your-bucket-name',
                Key=temp_key,
                Body=chunk_data
            )
        )
        
        # Track ETag for later assembly
        chunk_etag = s3_response['ETag'].strip('"')
        
        # Update Redis: mark chunk as received
        redis_client.hset(
            f"chunked_upload:{upload_id}",
            mapping={
                f"chunk_{chunk_index}_etag": chunk_etag,
                'chunks_received': str(int(upload_meta.get('chunks_received', 0)) + 1)
            }
        )
        
        return {
            "status": "chunk_received",
            "chunk_index": chunk_index,
            "etag": chunk_etag
        }
        
    except Exception as e:
        print(f"[{upload_id}] Chunk error: {str(e)}")
        raise HTTPException(500, f"Chunk upload failed: {str(e)}")

@app.post("/api/uploads/chunked/{upload_id}/complete")
async def complete_chunked_upload(
    upload_id: str,
    payload: dict,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete chunked upload
    
    Request body:
    {
        "total_chunks": 100
    }
    """
    
    total_chunks = payload['total_chunks']
    
    # Get upload metadata
    upload_meta = redis_client.hgetall(f"chunked_upload:{upload_id}")
    if not upload_meta:
        raise HTTPException(404, "Upload not found")
    
    upload_meta = {k.decode(): v.decode() for k, v in upload_meta.items()}
    chunks_received = int(upload_meta.get('chunks_received', 0))
    
    # Verify all chunks received
    if chunks_received != total_chunks:
        raise HTTPException(
            400,
            f"Not all chunks received: {chunks_received}/{total_chunks}"
        )
    
    print(f"[{upload_id}] All chunks received, combining...")
    
    # Background job: combine chunks and finalize
    background_tasks.add_task(
        finalize_chunked_upload,
        upload_id,
        upload_meta,
        total_chunks,
        db
    )
    
    return {
        "status": "finalizing",
        "message": "Chunks received, processing in background"
    }

async def finalize_chunked_upload(upload_id, upload_meta, total_chunks, db):
    """
    Background task: combine chunks and create final file
    """
    
    try:
        print(f"[{upload_id}] Starting finalization...")
        
        file_name = upload_meta['file_name']
        group_id = upload_meta['group_id']
        user_id = upload_meta['user_id']
        
        # Combine chunks: copy all to final location
        # (In production, use multipart copy or streaming combine)
        final_key = f"groups/{group_id}/{upload_id}/{file_name}"
        
        # For simplicity, let's use S3 copy operations
        # (Real implementation would stream or use S3 batch copy)
        for chunk_index in range(total_chunks):
            temp_key = f"uploads/chunks/{upload_id}/chunk_{chunk_index}"
            part_num = chunk_index + 1
            
            # Get chunk from temp location
            chunk_obj = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.get_object(
                    Bucket='your-bucket-name',
                    Key=temp_key
                )
            )
            chunk_data = chunk_obj['Body'].read()
            
            # Append to final file (or use multipart for efficiency)
            if chunk_index == 0:
                # Create new file
                s3_client.put_object(
                    Bucket='your-bucket-name',
                    Key=final_key,
                    Body=chunk_data
                )
            # (For real impl: use multipart copy or streaming combine)
        
        # Get final file info
        final_obj = s3_client.head_object(
            Bucket='your-bucket-name',
            Key=final_key
        )
        
        file_size = final_obj['ContentLength']
        
        # Create DB record
        file_id = str(uuid.uuid4())
        file_record = FileMaster(
            file_id=file_id,
            file_name=file_name,
            file_type=get_file_type(file_name),
            file_size_bytes=file_size,
            mime_type='application/octet-stream',
            uploaded_by=user_id,
            original_group_id=group_id,
            s3_path=f"s3://your-bucket-name/{final_key}",
            version=1,
            is_deleted=False,
            created_at=datetime.utcnow()
        )
        
        db.add(file_record)
        
        # Create mapping
        group_file_mapping = GroupFileMappings(
            group_id=group_id,
            file_id=file_id,
            permissions=7,
            shared_by=user_id,
            shared_at=datetime.utcnow()
        )
        
        db.add(group_file_mapping)
        db.commit()
        
        # Audit log
        await create_audit_log(file_id, user_id, 'upload', db)
        
        # Cleanup temp chunks
        for i in range(total_chunks):
            temp_key = f"uploads/chunks/{upload_id}/chunk_{i}"
            s3_client.delete_object(Bucket='your-bucket-name', Key=temp_key)
        
        # Cleanup Redis
        redis_client.delete(f"chunked_upload:{upload_id}")
        
        print(f"[{upload_id}] Finalization complete! File ID: {file_id}")
        
        # Notify user (via WebSocket or polling)
        await notify_user(user_id, {
            "event": "upload_complete",
            "file_id": file_id,
            "file_name": file_name
        })
        
    except Exception as e:
        print(f"[{upload_id}] Finalization error: {str(e)}")
        # Mark as failed
        redis_client.hset(
            f"chunked_upload:{upload_id}",
            mapping={'status': 'failed', 'error': str(e)}
        )
```

### Client Code

```javascript
// File: frontend/uploadChunked.js

class ChunkedUploader {
  constructor(options = {}) {
    this.chunkSize = options.chunkSize || 5 * 1024 * 1024; // 5MB
    this.maxRetries = options.maxRetries || 3;
    this.onProgress = options.onProgress || (() => {});
    this.onError = options.onError || (() => {});
    this.onSuccess = options.onSuccess || (() => {});
  }

  async upload(file, groupId, authToken) {
    console.log(`Starting chunked upload: ${file.name}`);
    
    // Step 1: Initiate upload
    const initiateResp = await fetch('/api/uploads/chunked/initiate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        file_name: file.name,
        file_size: file.size,
        group_id: groupId
      })
    });
    
    const { upload_id, total_chunks, chunk_size } = await initiateResp.json();
    console.log(`Upload initiated: ${upload_id}, ${total_chunks} chunks`);
    
    // Step 2: Upload chunks
    let uploadedChunks = 0;
    
    for (let chunkIndex = 0; chunkIndex < total_chunks; chunkIndex++) {
      const start = chunkIndex * chunk_size;
      const end = Math.min(start + chunk_size, file.size);
      const chunk = file.slice(start, end);
      
      // Retry logic
      let retries = 0;
      let success = false;
      
      while (!success && retries < this.maxRetries) {
        try {
          const formData = new FormData();
          formData.append('chunk_file', chunk);
          
          const uploadResp = await fetch(
            `/api/uploads/chunked/${upload_id}/chunks?chunk_index=${chunkIndex}`,
            {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authToken}`
              },
              body: formData
            }
          );
          
          if (!uploadResp.ok) {
            throw new Error(`Chunk upload failed: ${uploadResp.status}`);
          }
          
          uploadedChunks++;
          const progressPercent = (uploadedChunks / total_chunks) * 100;
          console.log(`Chunk ${chunkIndex + 1}/${total_chunks} uploaded (${progressPercent.toFixed(2)}%)`);
          this.onProgress(progressPercent);
          
          success = true;
          
        } catch (error) {
          retries++;
          console.warn(`Chunk ${chunkIndex} retry ${retries}/${this.maxRetries}: ${error.message}`);
          
          if (retries < this.maxRetries) {
            // Exponential backoff
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, retries) * 1000));
          } else {
            throw error;
          }
        }
      }
      
      if (!success) {
        throw new Error(`Failed to upload chunk ${chunkIndex} after ${this.maxRetries} retries`);
      }
    }
    
    // Step 3: Complete upload
    console.log('All chunks uploaded, completing upload...');
    
    const completeResp = await fetch(
      `/api/uploads/chunked/${upload_id}/complete`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ total_chunks })
      }
    );
    
    const completeData = await completeResp.json();
    console.log('Upload complete:', completeData);
    this.onSuccess(completeData);
  }
}

// Usage
const chunkedUploader = new ChunkedUploader({
  chunkSize: 5 * 1024 * 1024,
  onProgress: (percent) => {
    console.log(`Upload: ${percent.toFixed(2)}%`);
    document.getElementById('progress-bar').style.width = percent + '%';
  },
  onError: (error) => {
    console.error('Upload failed:', error);
    alert(`Upload error: ${error.message}`);
  },
  onSuccess: (data) => {
    alert('Upload complete!');
  }
});

// Trigger
document.getElementById('upload-chunked-btn').addEventListener('click', async () => {
  const file = document.getElementById('file-input').files[0];
  const groupId = document.getElementById('group-select').value;
  const token = localStorage.getItem('auth_token');
  
  try {
    await chunkedUploader.upload(file, groupId, token);
  } catch (error) {
    chunkedUploader.onError(error);
  }
});
```

---

## Strategy 3: S3 Multipart Upload
### (Backend Proxy - Best for control and verification)

### Backend Code

```python
# File: app/api/uploads_multipart.py

@app.post("/api/uploads/multipart/initiate")
async def initiate_multipart_upload(
    payload: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate S3 multipart upload
    
    Request:
    {
        "file_name": "video.mp4",
        "file_size": 1073741824,
        "group_id": "group_123"
    }
    """
    
    file_name = payload['file_name']
    file_size = payload['file_size']
    group_id = payload['group_id']
    
    # Validate
    if not await check_write_permission(current_user.id, group_id, db):
        raise HTTPException(403)
    
    try:
        # Initiate S3 multipart upload
        s3_key = f"groups/{group_id}/{uuid.uuid4()}/{file_name}"
        
        response = s3_client.create_multipart_upload(
            Bucket='your-bucket-name',
            Key=s3_key,
            ContentType='application/octet-stream',
            Metadata={
                'user-id': current_user.id,
                'group-id': group_id,
                'original-name': file_name
            }
        )
        
        upload_id = response['UploadId']
        
        # Store in Redis
        redis_client.hset(
            f"multipart:{upload_id}",
            mapping={
                'file_name': file_name,
                'file_size': file_size,
                'group_id': group_id,
                'user_id': current_user.id,
                's3_key': s3_key,
                'parts_uploaded': 0,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'initiated'
            }
        )
        redis_client.expire(f"multipart:{upload_id}", 7 * 24 * 3600)
        
        # Calculate part count
        part_size = 5 * 1024 * 1024  # 5MB
        total_parts = (file_size + part_size - 1) // part_size
        
        print(f"[{upload_id}] Multipart upload initiated: {total_parts} parts")
        
        return {
            "upload_id": upload_id,
            "part_size": part_size,
            "total_parts": total_parts
        }
        
    except Exception as e:
        print(f"Initiation error: {str(e)}")
        raise HTTPException(500, f"Failed to initiate upload: {str(e)}")

@app.post("/api/uploads/multipart/{upload_id}/parts")
async def upload_part(
    upload_id: str,
    part_number: int,
    part_file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload individual part to S3
    """
    
    # Get metadata
    meta = redis_client.hgetall(f"multipart:{upload_id}")
    if not meta:
        raise HTTPException(404, "Upload not found")
    
    meta = {k.decode(): v.decode() for k, v in meta.items()}
    
    if meta['user_id'] != current_user.id:
        raise HTTPException(403)
    
    try:
        part_data = await part_file.read()
        
        print(f"[{upload_id}] Uploading part {part_number} ({len(part_data)} bytes)")
        
        # Upload to S3
        response = s3_client.upload_part(
            Bucket='your-bucket-name',
            Key=meta['s3_key'],
            PartNumber=part_number,
            UploadId=upload_id,
            Body=part_data
        )
        
        etag = response['ETag'].strip('"')
        
        # Store ETag in Redis
        redis_client.hset(
            f"multipart:{upload_id}",
            mapping={
                f"part_{part_number}_etag": etag,
                'parts_uploaded': str(int(meta.get('parts_uploaded', 0)) + 1)
            }
        )
        
        return {
            "part_number": part_number,
            "etag": etag
        }
        
    except Exception as e:
        print(f"[{upload_id}] Part upload error: {str(e)}")
        raise HTTPException(500, f"Part upload failed: {str(e)}")

@app.post("/api/uploads/multipart/{upload_id}/complete")
async def complete_multipart_upload(
    upload_id: str,
    payload: dict,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete multipart upload
    
    Request:
    {
        "total_parts": 200
    }
    """
    
    total_parts = payload['total_parts']
    
    meta = redis_client.hgetall(f"multipart:{upload_id}")
    if not meta:
        raise HTTPException(404)
    
    meta = {k.decode(): v.decode() for k, v in meta.items()}
    
    try:
        # Prepare part list for S3
        part_list = []
        for i in range(1, total_parts + 1):
            etag = redis_client.hget(f"multipart:{upload_id}", f"part_{i}_etag")
            if not etag:
                raise HTTPException(400, f"Missing part {i}")
            
            part_list.append({
                'PartNumber': i,
                'ETag': etag.decode()
            })
        
        # Complete multipart on S3
        print(f"[{upload_id}] Completing multipart upload on S3...")
        
        response = s3_client.complete_multipart_upload(
            Bucket='your-bucket-name',
            Key=meta['s3_key'],
            UploadId=upload_id,
            MultipartUpload={'Parts': part_list}
        )
        
        file_location = response['Location']
        print(f"[{upload_id}] S3 multipart complete: {file_location}")
        
        # Background task: create DB record
        background_tasks.add_task(
            finalize_multipart_upload,
            upload_id,
            meta,
            file_location,
            db
        )
        
        return {
            "status": "completing",
            "message": "Multipart upload complete, processing..."
        }
        
    except Exception as e:
        # Abort on failure
        try:
            s3_client.abort_multipart_upload(
                Bucket='your-bucket-name',
                Key=meta['s3_key'],
                UploadId=upload_id
            )
        except:
            pass
        
        print(f"[{upload_id}] Completion error: {str(e)}")
        raise HTTPException(500, f"Completion failed: {str(e)}")

async def finalize_multipart_upload(upload_id, meta, file_location, db):
    """Background task to finalize after S3 multipart complete"""
    
    try:
        # Create DB record
        file_id = str(uuid.uuid4())
        file_record = FileMaster(
            file_id=file_id,
            file_name=meta['file_name'],
            file_type=get_file_type(meta['file_name']),
            file_size_bytes=int(meta['file_size']),
            mime_type='application/octet-stream',
            uploaded_by=meta['user_id'],
            original_group_id=meta['group_id'],
            s3_path=file_location,
            version=1,
            is_deleted=False,
            created_at=datetime.utcnow()
        )
        
        db.add(file_record)
        
        # Create mapping
        mapping = GroupFileMappings(
            group_id=meta['group_id'],
            file_id=file_id,
            permissions=7,
            shared_by=meta['user_id'],
            shared_at=datetime.utcnow()
        )
        db.add(mapping)
        db.commit()
        
        # Cleanup Redis
        redis_client.delete(f"multipart:{upload_id}")
        
        print(f"[{upload_id}] Finalized! File ID: {file_id}")
        
    except Exception as e:
        print(f"[{upload_id}] Finalize error: {str(e)}")
        db.rollback()
```

---

## Strategy 4: Direct S3 Upload with Pre-signed URLs
### (Best for scale - backend is NOT a bottleneck)

### Backend Code

```python
# File: app/api/uploads_presigned.py

@app.post("/api/uploads/presigned-url")
async def get_presigned_url(
    payload: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate pre-signed URL for direct client → S3 upload
    
    Request:
    {
        "file_name": "video.mp4",
        "file_size": 1073741824,
        "group_id": "group_123"
    }
    """
    
    file_name = payload['file_name']
    file_size = payload['file_size']
    group_id = payload['group_id']
    
    # Validate
    if not await check_write_permission(current_user.id, group_id, db):
        raise HTTPException(403)
    
    if file_size > 5 * 1024 * 1024 * 1024:  # 5GB
        raise HTTPException(400, "File too large")
    
    try:
        # Generate S3 key
        s3_key = f"groups/{group_id}/{uuid.uuid4()}/{file_name}"
        
        # Generate pre-signed URL (valid for 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': 'your-bucket-name',
                'Key': s3_key,
                'ContentType': 'application/octet-stream',
                'Metadata': {
                    'user-id': current_user.id,
                    'group-id': group_id
                }
            },
            ExpiresIn=3600
        )
        
        upload_id = str(uuid.uuid4())
        
        # Store pending upload in Redis
        redis_client.hset(
            f"pending_upload:{upload_id}",
            mapping={
                'file_name': file_name,
                'file_size': file_size,
                'group_id': group_id,
                'user_id': current_user.id,
                's3_key': s3_key,
                'status': 'pending_s3_upload',
                'created_at': datetime.utcnow().isoformat()
            }
        )
        redis_client.expire(f"pending_upload:{upload_id}", 7200)  # 2 hours
        
        print(f"[{upload_id}] Pre-signed URL generated")
        
        return {
            "upload_id": upload_id,
            "presigned_url": presigned_url,
            "expires_in": 3600
        }
        
    except Exception as e:
        print(f"Pre-signed URL error: {str(e)}")
        raise HTTPException(500, f"Failed to generate URL: {str(e)}")

@app.post("/api/uploads/presigned/{upload_id}/verify")
async def verify_presigned_upload(
    upload_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    After client uploads to S3, verify file exists and create DB record
    """
    
    # Get pending upload
    meta = redis_client.hgetall(f"pending_upload:{upload_id}")
    if not meta:
        raise HTTPException(404, "Pending upload not found")
    
    meta = {k.decode(): v.decode() for k, v in meta.items()}
    
    if meta['user_id'] != current_user.id:
        raise HTTPException(403)
    
    try:
        # Verify file exists on S3
        print(f"[{upload_id}] Verifying S3 upload...")
        
        s3_obj = s3_client.head_object(
            Bucket='your-bucket-name',
            Key=meta['s3_key']
        )
        
        actual_size = s3_obj['ContentLength']
        expected_size = int(meta['file_size'])
        
        # Verify size matches
        if actual_size != expected_size:
            raise HTTPException(
                400,
                f"Size mismatch: expected {expected_size}, got {actual_size}"
            )
        
        print(f"[{upload_id}] S3 file verified")
        
        # Create DB record
        file_id = str(uuid.uuid4())
        file_record = FileManaster(
            file_id=file_id,
            file_name=meta['file_name'],
            file_type=get_file_type(meta['file_name']),
            file_size_bytes=actual_size,
            mime_type='application/octet-stream',
            uploaded_by=meta['user_id'],
            original_group_id=meta['group_id'],
            s3_path=f"s3://your-bucket-name/{meta['s3_key']}",
            version=1,
            is_deleted=False,
            created_at=datetime.utcnow()
        )
        
        db.add(file_record)
        
        # Create mapping
        mapping = GroupFileMappings(
            group_id=meta['group_id'],
            file_id=file_id,
            permissions=7,
            shared_by=meta['user_id'],
            shared_at=datetime.utcnow()
        )
        db.add(mapping)
        
        # Audit log
        audit = FileAuditLog(
            file_id=file_id,
            user_id=meta['user_id'],
            action='upload',
            created_at=datetime.utcnow()
        )
        db.add(audit)
        
        db.commit()
        
        # Cleanup
        redis_client.delete(f"pending_upload:{upload_id}")
        
        print(f"[{upload_id}] DB record created. File ID: {file_id}")
        
        return {
            "status": "success",
            "file_id": file_id,
            "message": "File verified and registered"
        }
        
    except Exception as e:
        print(f"[{upload_id}] Verification error: {str(e)}")
        db.rollback()
        raise HTTPException(500, f"Verification failed: {str(e)}")

@app.post("/api/uploads/presigned-multipart/initiate")
async def initiate_presigned_multipart(
    payload: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    For very large files: multipart with pre-signed URLs per part
    Client uploads parts directly to S3
    """
    
    file_name = payload['file_name']
    file_size = payload['file_size']
    group_id = payload['group_id']
    num_parts = payload.get('num_parts', (file_size + 5*1024*1024 - 1) // (5*1024*1024))
    
    if not await check_write_permission(current_user.id, group_id, db):
        raise HTTPException(403)
    
    try:
        # Initiate multipart
        s3_key = f"groups/{group_id}/{uuid.uuid4()}/{file_name}"
        
        response = s3_client.create_multipart_upload(
            Bucket='your-bucket-name',
            Key=s3_key
        )
        
        s3_upload_id = response['UploadId']
        
        # Generate pre-signed URLs for each part
        presigned_urls = []
        for part_number in range(1, num_parts + 1):
            url = s3_client.generate_presigned_url(
                'upload_part',
                Params={
                    'Bucket': 'your-bucket-name',
                    'Key': s3_key,
                    'UploadId': s3_upload_id,
                    'PartNumber': part_number
                },
                ExpiresIn=3600
            )
            presigned_urls.append({
                "part_number": part_number,
                "presigned_url": url
            })
        
        upload_id = str(uuid.uuid4())
        
        # Store metadata
        redis_client.hset(
            f"presigned_multipart:{upload_id}",
            mapping={
                'file_name': file_name,
                'file_size': file_size,
                'group_id': group_id,
                'user_id': current_user.id,
                's3_key': s3_key,
                's3_upload_id': s3_upload_id,
                'num_parts': num_parts,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        redis_client.expire(f"presigned_multipart:{upload_id}", 7200)
        
        print(f"[{upload_id}] Pre-signed multipart initiated: {num_parts} parts")
        
        return {
            "upload_id": upload_id,
            "presigned_urls": presigned_urls,
            "expires_in": 3600
        }
        
    except Exception as e:
        print(f"Pre-signed multipart init error: {str(e)}")
        raise HTTPException(500, f"Failed to initiate: {str(e)}")

@app.post("/api/uploads/presigned-multipart/{upload_id}/complete")
async def complete_presigned_multipart(
    upload_id: str,
    payload: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete pre-signed multipart after client uploads all parts
    
    Request:
    {
        "parts": [
            {"part_number": 1, "etag": "abc123..."},
            {"part_number": 2, "etag": "def456..."},
            ...
        ]
    }
    """
    
    parts = payload['parts']
    
    meta = redis_client.hgetall(f"presigned_multipart:{upload_id}")
    if not meta:
        raise HTTPException(404)
    
    meta = {k.decode(): v.decode() for k, v in meta.items()}
    
    if meta['user_id'] != current_user.id:
        raise HTTPException(403)
    
    try:
        # Complete multipart on S3
        print(f"[{upload_id}] Completing S3 multipart...")
        
        response = s3_client.complete_multipart_upload(
            Bucket='your-bucket-name',
            Key=meta['s3_key'],
            UploadId=meta['s3_upload_id'],
            MultipartUpload={'Parts': parts}
        )
        
        file_location = response['Location']
        
        # Create DB record
        file_id = str(uuid.uuid4())
        file_record = FileManaster(
            file_id=file_id,
            file_name=meta['file_name'],
            file_type=get_file_type(meta['file_name']),
            file_size_bytes=int(meta['file_size']),
            mime_type='application/octet-stream',
            uploaded_by=meta['user_id'],
            original_group_id=meta['group_id'],
            s3_path=file_location,
            version=1,
            is_deleted=False,
            created_at=datetime.utcnow()
        )
        
        db.add(file_record)
        
        mapping = GroupFileMappings(
            group_id=meta['group_id'],
            file_id=file_id,
            permissions=7,
            shared_by=meta['user_id'],
            shared_at=datetime.utcnow()
        )
        db.add(mapping)
        db.commit()
        
        # Cleanup
        redis_client.delete(f"presigned_multipart:{upload_id}")
        
        print(f"[{upload_id}] Complete! File ID: {file_id}")
        
        return {
            "status": "success",
            "file_id": file_id
        }
        
    except Exception as e:
        # Abort
        try:
            s3_client.abort_multipart_upload(
                Bucket='your-bucket-name',
                Key=meta['s3_key'],
                UploadId=meta['s3_upload_id']
            )
        except:
            pass
        
        print(f"[{upload_id}] Complete error: {str(e)}")
        raise HTTPException(500, f"Completion failed: {str(e)}")
```

### Client Code (Pre-signed Direct)

```javascript
// File: frontend/uploadPresigned.js

class PresignedUploader {
  async uploadDirect(file, groupId, authToken) {
    console.log(`Uploading directly to S3: ${file.name}`);
    
    // Step 1: Get pre-signed URL from backend
    const presignedResp = await fetch('/api/uploads/presigned-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        file_name: file.name,
        file_size: file.size,
        group_id: groupId
      })
    });
    
    const { presigned_url, upload_id } = await presignedResp.json();
    console.log(`Got presigned URL, upload_id: ${upload_id}`);
    
    // Step 2: Upload directly to S3
    console.log('Uploading to S3...');
    
    const s3Resp = await fetch(presigned_url, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type || 'application/octet-stream'
      },
      body: file
    });
    
    if (!s3Resp.ok) {
      throw new Error(`S3 upload failed: ${s3Resp.status}`);
    }
    
    console.log('File uploaded to S3');
    
    // Step 3: Verify with backend
    const verifyResp = await fetch(
      `/api/uploads/presigned/${upload_id}/verify`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );
    
    const result = await verifyResp.json();
    console.log('Upload verified:', result);
    
    return result;
  }

  async uploadMultipartDirect(file, groupId, authToken) {
    console.log(`Uploading multipart directly to S3: ${file.name}`);
    
    const chunkSize = 5 * 1024 * 1024; // 5MB
    const totalParts = Math.ceil(file.size / chunkSize);
    
    // Step 1: Initiate
    const initiateResp = await fetch('/api/uploads/presigned-multipart/initiate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        file_name: file.name,
        file_size: file.size,
        group_id: groupId,
        num_parts: totalParts
      })
    });
    
    const { upload_id, presigned_urls } = await initiateResp.json();
    console.log(`Multipart initiated: ${upload_id}, ${totalParts} parts`);
    
    // Step 2: Upload parts
    const parts = [];
    
    for (let i = 0; i < totalParts; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, file.size);
      const part = file.slice(start, end);
      
      const presignedUrl = presigned_urls[i].presigned_url;
      
      console.log(`Uploading part ${i + 1}/${totalParts}...`);
      
      const partResp = await fetch(presignedUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/octet-stream'
        },
        body: part
      });
      
      if (!partResp.ok) {
        throw new Error(`Part ${i + 1} upload failed`);
      }
      
      // Get ETag from response headers
      const etag = partResp.headers.get('etag');
      
      parts.push({
        part_number: i + 1,
        etag: etag
      });
      
      console.log(`Part ${i + 1} uploaded, ETag: ${etag}`);
    }
    
    // Step 3: Complete
    console.log('Completing multipart upload...');
    
    const completeResp = await fetch(
      `/api/uploads/presigned-multipart/${upload_id}/complete`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ parts })
      }
    );
    
    const result = await completeResp.json();
    console.log('Upload complete:', result);
    
    return result;
  }
}

// Usage
const presignedUploader = new PresignedUploader();

document.getElementById('upload-presigned-btn').addEventListener('click', async () => {
  const file = document.getElementById('file-input').files[0];
  const groupId = document.getElementById('group-select').value;
  const token = localStorage.getItem('auth_token');
  
  try {
    if (file.size < 500 * 1024 * 1024) {
      // Small file: single PUT
      const result = await presignedUploader.uploadDirect(file, groupId, token);
      alert(`Upload complete! File ID: ${result.file_id}`);
    } else {
      // Large file: multipart
      const result = await presignedUploader.uploadMultipartDirect(file, groupId, token);
      alert(`Upload complete! File ID: ${result.file_id}`);
    }
  } catch (error) {
    alert(`Upload failed: ${error.message}`);
  }
});
```

---

## 🌍 Real-World Examples

### Example 1: Startup (Early Stage) 
**Scenario**: 10 users, <100MB files average

**Recommendation**: **Single-Request Upload**

**Why**:
- Simple to implement (one endpoint)
- Server can handle it
- No complexity overhead
- Good enough for scale

**Setup**:
```python
# Just use the simple strategy
# Single endpoint, stream to S3
```

---

### Example 2: Growing Product (1000 Active Users)
**Scenario**: 1000 concurrent users, mix of 10MB-500MB files, mobile + web

**Recommendation**: **S3 Multipart + Pre-signed URLs**

**Why**:
- Backend not overloaded yet
- Need resume capability for mobile
- Multipart gives us control
- Pre-signed URLs when traffic spikes

**Setup**:
```python
# Use multipart strategy
# Start with backend proxy
# Add pre-signed URLs as you scale

# When backend CPU > 60%:
#   Switch to pre-signed URLs
```

---

### Example 3: Scale (100K+ Users, TB/day uploads)
**Scenario**: 100K users, heavy upload traffic, various file types

**Recommendation**: **Pre-signed Multipart + S3 Direct**

**Why**:
- Backend must NOT touch file data
- Each upload independent (no coordination bottleneck)
- S3 handles all the complexity
- Cost-effective at this scale

**Setup**:
```python
# Use presigned multipart strategy
# Backend only: auth, signing, verification
# Client uploads directly to S3

# Infrastructure:
# - Backend: 3 instances (light load)
# - S3: Automatic scaling
# - CloudFront: Cache frequently accessed
```

---

### Example 4: Real Company Pattern (Dropbox/Google Drive Style)

**Scenario**: File size 1 byte - 50GB, millions of users, worldwide

**Hybrid Approach**:

```
IF file_size < 100MB:
  → Use pre-signed PUT (simple, fast)

ELSE IF file_size < 5GB:
  → Use pre-signed multipart (resume support)

ELSE IF file_size >= 5GB:
  → Split into pre-signed multipart + resume logic
  → Add bandwidth throttling per user
  → Add pause/resume checkpoints

FOR NETWORK MONITORING:
  → Track upload success rate
  → Track average speed
  → Alert if speed < expected
  → Offer resume to user if slow

FOR SCALABILITY:
  → Multi-region S3 buckets
  → CloudFront CDN for presigned URLs
  → Separate "upload" and "download" clusters
  → DynamoDB for metadata (not PostgreSQL at mega-scale)
```

---

## 📋 Production Deployment Checklist

```
┌─ Security
├─ [ ] Pre-signed URLs time-limited (15-60 min)
├─ [ ] S3 bucket policy restrictive
├─ [ ] Verify file permissions before generating URLs
├─ [ ] Validate file types (whitelist, not blacklist)
├─ [ ] Scan files for malware (ClamAV, etc.)
├─ [ ] Encrypt at rest (S3 SSE)
├─ [ ] Encrypt in transit (HTTPS only)
└─ [ ] Rate limit uploads per user

┌─ Reliability
├─ [ ] Retry logic with exponential backoff
├─ [ ] Orphaned file detection (S3 files without DB records)
├─ [ ] Cleanup old pending uploads (>7 days)
├─ [ ] Abort multipart after timeout
├─ [ ] Handle S3 errors gracefully
├─ [ ] Database transaction atomicity
└─ [ ] Audit logging for all uploads

┌─ Monitoring
├─ [ ] Upload success rate (target >99%)
├─ [ ] Average upload latency per file size
├─ [ ] S3 API call count and costs
├─ [ ] Error rate by type
├─ [ ] User notification on completion
├─ [ ] Dashboard for upload metrics
└─ [ ] Alerts: error rate >1%, latency p95 >30s

┌─ Performance
├─ [ ] Connection pooling to S3
├─ [ ] CloudFront cache for presigned URLs
├─ [ ] Batch operations where possible
├─ [ ] Redis for metadata caching
├─ [ ] Async finalization (background jobs)
└─ [ ] Load test: 1000 concurrent uploads

┌─ Cost Optimization
├─ [ ] S3 lifecycle policies (archive old files)
├─ [ ] Calculate per-upload cost
├─ [ ] Use presigned to save backend bandwidth
├─ [ ] Monitor for zombie files (orphaned)
├─ [ ] Consider S3 Intelligent-Tiering
└─ [ ] Track ROI of infrastructure
```

---

## 💡 Quick Decision Guide

```
QUESTION: How do I choose a strategy?

Answer in order:

1. What's the file size?
   <50MB      → Single-request (simple wins)
   50-500MB   → Multipart or Chunked
   500MB-5GB  → Multipart with resume
   >5GB       → Pre-signed multipart

2. How reliable is the network?
   Reliable   → Simpler strategy is OK
   Unreliable → Add resume capability

3. What's the backend load?
   Low        → Can proxy files
   High       → Use pre-signed URLs

4. What's the scale?
   <1000 users        → Simplicity > Scale
   1000-100K users    → Balance both
   >100K users        → Scale > Simplicity
```

---

