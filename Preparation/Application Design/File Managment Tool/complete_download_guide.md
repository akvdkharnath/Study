# Large File Download Strategies - Complete Implementation Guide
## With Streaming, Resumable Downloads, and Performance Optimization

**Date**: January 3, 2026  
**Level**: L4-L5 Senior Backend Engineer  
**Companion to**: `complete_upload_guide.md`

---

## 📋 Quick Overview

**Download is easier than upload, but has different challenges:**

| Aspect | Upload | Download |
|--------|--------|----------|
| **Main Challenge** | Bandwidth from client | Bandwidth to client |
| **Failure Risk** | High (network drops mid-upload) | Medium (mostly resume-friendly) |
| **Scaling Issue** | Backend bottleneck | Bandwidth cost |
| **Solution** | Pre-signed URLs to bypass backend | CDN + HTTP Range requests |
| **Retry Strategy** | Resume from part N | Resume from byte X |

---

## 🎯 Decision Tree (Downloads)

```
┌─ File Size?
│
├─ < 50MB
│  └─ Simple streaming (no special handling)
│
├─ 50MB - 500MB
│  ├─ Is network stable?
│  │  ├─ YES → Stream from S3 via CloudFront
│  │  └─ NO → Add HTTP Range support
│  │
│
├─ 500MB - 5GB
│  └─ MUST support:
│     ├─ HTTP Range requests (resume)
│     ├─ CloudFront caching
│     ├─ Signed URLs (avoid hotlinking)
│     └─ Parallel chunk downloads (client-side)
│
└─ > 5GB
   └─ Use:
      ├─ Signed S3 URLs (redirect to S3)
      ├─ Torrent or P2P (for very large)
      └─ Streaming with progress tracking
```

---

## Strategy 1: Simple Stream (Small Files)

### Backend Code

```python
# File: app/api/downloads_simple.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
import boto3

app = FastAPI()
s3_client = boto3.client('s3')

@app.get("/api/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simple file download
    Best for: Small files (<50MB)
    
    Flow:
    1. Check permissions
    2. Stream from S3
    3. Return to client
    """
    
    print(f"[{file_id}] Download request from {current_user.id}")
    
    try:
        # Get file record
        file_record = db.query(FileMaster).filter(
            FileMaster.file_id == file_id
        ).first()
        
        if not file_record:
            raise HTTPException(404, "File not found")
        
        # Check permission
        has_read = await check_read_permission(
            current_user.id,
            file_id,
            db
        )
        
        if not has_read:
            raise HTTPException(403, "No read permission")
        
        # Get from S3
        print(f"[{file_id}] Fetching from S3: {file_record.s3_path}")
        
        # Extract bucket and key from S3 path
        # S3 path format: "s3://bucket-name/key"
        s3_path = file_record.s3_path
        bucket = s3_path.split('/')[2]
        key = '/'.join(s3_path.split('/')[3:])
        
        response = s3_client.get_object(Bucket=bucket, Key=key)
        
        # Stream body
        def stream_generator():
            """Generator to stream S3 object in chunks"""
            with response['Body'] as stream:
                for chunk in iter(lambda: stream.read(8192), b''):
                    yield chunk
        
        # Audit log
        await create_audit_log(
            file_id=file_id,
            user_id=current_user.id,
            action='download',
            db=db
        )
        
        print(f"[{file_id}] Streaming started")
        
        return StreamingResponse(
            stream_generator(),
            media_type=file_record.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{file_record.file_name}\"",
                "Content-Length": str(file_record.file_size_bytes),
                "Cache-Control": "private, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{file_id}] Download error: {str(e)}")
        raise HTTPException(500, f"Download failed: {str(e)}")
```

### Client Code

```javascript
// File: frontend/downloadSimple.js

class SimpleDownloader {
  async download(fileId, authToken) {
    console.log(`Downloading file: ${fileId}`);
    
    try {
      const response = await fetch(`/api/files/${fileId}/download`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.status}`);
      }
      
      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('content-disposition');
      const filename = this.extractFilename(contentDisposition);
      
      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      console.log('Download complete');
      
    } catch (error) {
      console.error('Download error:', error);
      throw error;
    }
  }
  
  extractFilename(contentDisposition) {
    // Parse: attachment; filename="file.mp4"
    const match = contentDisposition?.match(/filename="([^"]+)"/);
    return match ? match[1] : 'download';
  }
}

// Usage
const downloader = new SimpleDownloader();
document.getElementById('download-btn').addEventListener('click', async () => {
  const fileId = document.getElementById('file-id').value;
  const token = localStorage.getItem('auth_token');
  await downloader.download(fileId, token);
});
```

---

## Strategy 2: Stream with HTTP Range Support (Resume)

### What is HTTP Range?

HTTP Range allows a client to request specific byte ranges of a file. This enables:
- Resume interrupted downloads
- Parallel downloads (multiple ranges at once)
- Seeking in video/audio playback

**Example**:
```
GET /api/files/123/download HTTP/1.1
Range: bytes=0-1023

→ Server returns bytes 0-1023
  Status: 206 Partial Content
  Content-Range: bytes 0-1023/10485760
  Content-Length: 1024
```

### Backend Code (with Range Support)

```python
# File: app/api/downloads_range.py

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse, FileResponse
import boto3
import re

app = FastAPI()
s3_client = boto3.client('s3')

@app.get("/api/files/{file_id}/download")
async def download_file_range(
    file_id: str,
    range_header: str = Header(None),  # Range: bytes=0-1023
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download with HTTP Range support (resume, partial content)
    
    Best for:
    - Files 50MB-5GB
    - Unreliable networks
    - Video/audio streaming
    """
    
    print(f"[{file_id}] Download request, Range: {range_header}")
    
    try:
        # Get file record
        file_record = db.query(FileMaster).filter(
            FileMaster.file_id == file_id
        ).first()
        
        if not file_record:
            raise HTTPException(404, "File not found")
        
        # Check permission
        has_read = await check_read_permission(
            current_user.id,
            file_id,
            db
        )
        
        if not has_read:
            raise HTTPException(403, "No permission")
        
        # Parse S3 location
        s3_path = file_record.s3_path
        bucket = s3_path.split('/')[2]
        key = '/'.join(s3_path.split('/')[3:])
        
        file_size = file_record.file_size_bytes
        
        # Parse Range header
        if range_header:
            # Range: bytes=start-end or bytes=start- or bytes=-length
            match = re.match(r'bytes=(\d*)-(\d*)', range_header)
            
            if not match:
                raise HTTPException(416, "Invalid Range header")
            
            start_str, end_str = match.groups()
            
            # Calculate range
            if start_str and end_str:
                # bytes=100-200
                start = int(start_str)
                end = int(end_str)
            elif start_str:
                # bytes=100-
                start = int(start_str)
                end = file_size - 1
            elif end_str:
                # bytes=-100 (last 100 bytes)
                start = file_size - int(end_str)
                end = file_size - 1
            else:
                raise HTTPException(416, "Invalid Range")
            
            # Validate range
            if start < 0 or end >= file_size or start > end:
                # Return 416 Range Not Satisfiable
                return StreamingResponse(
                    status_code=416,
                    headers={
                        "Content-Range": f"bytes */{file_size}"
                    }
                )
            
            length = end - start + 1
            print(f"[{file_id}] Partial content: {start}-{end} ({length} bytes)")
            
            # Get range from S3
            response = s3_client.get_object(
                Bucket=bucket,
                Key=key,
                Range=f"bytes={start}-{end}"
            )
            
            def stream_generator():
                with response['Body'] as stream:
                    for chunk in iter(lambda: stream.read(8192), b''):
                        yield chunk
            
            return StreamingResponse(
                stream_generator(),
                status_code=206,  # Partial Content
                media_type=file_record.mime_type,
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Content-Length": str(length),
                    "Accept-Ranges": "bytes",
                    "Content-Disposition": f"attachment; filename=\"{file_record.file_name}\""
                }
            )
        
        else:
            # No range specified, return full file
            print(f"[{file_id}] Full file download")
            
            response = s3_client.get_object(Bucket=bucket, Key=key)
            
            def stream_generator():
                with response['Body'] as stream:
                    for chunk in iter(lambda: stream.read(8192), b''):
                        yield chunk
            
            # Audit log
            await create_audit_log(
                file_id=file_id,
                user_id=current_user.id,
                action='download',
                db=db
            )
            
            return StreamingResponse(
                stream_generator(),
                status_code=200,
                media_type=file_record.mime_type,
                headers={
                    "Content-Length": str(file_size),
                    "Accept-Ranges": "bytes",
                    "Content-Disposition": f"attachment; filename=\"{file_record.file_name}\""
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{file_id}] Download error: {str(e)}")
        raise HTTPException(500, f"Download failed: {str(e)}")
```

### Client Code (with Resume)

```javascript
// File: frontend/downloadResume.js

class ResumableDownloader {
  constructor(options = {}) {
    this.chunkSize = options.chunkSize || 1 * 1024 * 1024; // 1MB
    this.maxRetries = options.maxRetries || 3;
    this.onProgress = options.onProgress || (() => {});
    this.onError = options.onError || (() => {});
  }

  async download(fileId, authToken) {
    console.log(`Starting resumable download: ${fileId}`);
    
    try {
      // First request: get file info
      const infoResp = await fetch(`/api/files/${fileId}/info`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      const fileInfo = await infoResp.json();
      const fileSize = fileInfo.file_size_bytes;
      const fileName = fileInfo.file_name;
      
      console.log(`File size: ${fileSize} bytes`);
      
      // Determine if server supports ranges
      const headResp = await fetch(`/api/files/${fileId}/download`, {
        method: 'HEAD',
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      const supportsRange = headResp.headers.get('Accept-Ranges') === 'bytes';
      console.log(`Server supports ranges: ${supportsRange}`);
      
      if (!supportsRange) {
        // Fallback to simple download
        await this.simpleDownload(fileId, fileName, authToken);
        return;
      }
      
      // Download in chunks
      const chunks = [];
      const totalChunks = Math.ceil(fileSize / this.chunkSize);
      
      for (let i = 0; i < totalChunks; i++) {
        const start = i * this.chunkSize;
        const end = Math.min(start + this.chunkSize - 1, fileSize - 1);
        
        let retries = 0;
        let success = false;
        
        while (!success && retries < this.maxRetries) {
          try {
            console.log(`Downloading chunk ${i + 1}/${totalChunks} (${start}-${end})...`);
            
            const chunkResp = await fetch(`/api/files/${fileId}/download`, {
              headers: {
                'Authorization': `Bearer ${authToken}`,
                'Range': `bytes=${start}-${end}`
              }
            });
            
            if (chunkResp.status === 206 || chunkResp.status === 200) {
              const blob = await chunkResp.blob();
              chunks.push(blob);
              
              const downloadedBytes = chunks.reduce((sum, b) => sum + b.size, 0);
              const progressPercent = (downloadedBytes / fileSize) * 100;
              console.log(`Progress: ${progressPercent.toFixed(2)}%`);
              this.onProgress(progressPercent);
              
              success = true;
            } else {
              throw new Error(`Chunk download failed: ${chunkResp.status}`);
            }
            
          } catch (error) {
            retries++;
            console.warn(`Chunk ${i} retry ${retries}/${this.maxRetries}: ${error.message}`);
            
            if (retries < this.maxRetries) {
              await new Promise(r => setTimeout(r, Math.pow(2, retries) * 1000));
            } else {
              throw error;
            }
          }
        }
        
        if (!success) {
          throw new Error(`Failed to download chunk ${i} after retries`);
        }
      }
      
      // Combine chunks and save
      const fullBlob = new Blob(chunks);
      this.saveBlob(fullBlob, fileName);
      
      console.log('Download complete!');
      
    } catch (error) {
      console.error('Download error:', error);
      this.onError(error);
      throw error;
    }
  }

  async simpleDownload(fileId, fileName, authToken) {
    const resp = await fetch(`/api/files/${fileId}/download`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    const blob = await resp.blob();
    this.saveBlob(blob, fileName);
  }

  saveBlob(blob, fileName) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
}

// Usage
const resumeDownloader = new ResumableDownloader({
  chunkSize: 1 * 1024 * 1024,
  onProgress: (percent) => {
    document.getElementById('progress-bar').value = percent;
    document.getElementById('progress-text').innerText = `${percent.toFixed(2)}%`;
  },
  onError: (error) => {
    alert(`Download failed: ${error.message}`);
  }
});

document.getElementById('download-resume-btn').addEventListener('click', async () => {
  const fileId = document.getElementById('file-id').value;
  const token = localStorage.getItem('auth_token');
  await resumeDownloader.download(fileId, token);
});
```

---

## Strategy 3: Signed S3 URLs (Bypass Backend)

### Why Use Signed S3 URLs?

1. **Bandwidth**: Client downloads directly from S3, not through backend
2. **Scale**: No backend load for download traffic
3. **Speed**: S3 is optimized for this
4. **Cost**: Much cheaper than proxying

### Backend Code

```python
# File: app/api/downloads_signed.py

@app.get("/api/files/{file_id}/signed-download-url")
async def get_signed_download_url(
    file_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get signed S3 URL for direct download
    
    Flow:
    1. Verify permissions
    2. Generate signed URL (valid 1 hour)
    3. Return URL
    4. Client downloads directly from S3
    """
    
    print(f"[{file_id}] Signed URL request from {current_user.id}")
    
    try:
        # Get file record
        file_record = db.query(FileMaster).filter(
            FileMaster.file_id == file_id
        ).first()
        
        if not file_record:
            raise HTTPException(404, "File not found")
        
        # Check permission
        has_read = await check_read_permission(
            current_user.id,
            file_id,
            db
        )
        
        if not has_read:
            raise HTTPException(403, "No permission")
        
        # Extract bucket and key
        s3_path = file_record.s3_path
        bucket = s3_path.split('/')[2]
        key = '/'.join(s3_path.split('/')[3:])
        
        # Generate signed URL (valid for 1 hour)
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ResponseContentDisposition': f"attachment; filename=\"{file_record.file_name}\""
            },
            ExpiresIn=3600  # 1 hour
        )
        
        print(f"[{file_id}] Signed URL generated")
        
        # Audit log
        await create_audit_log(
            file_id=file_id,
            user_id=current_user.id,
            action='download',
            db=db
        )
        
        return {
            "signed_url": signed_url,
            "expires_in": 3600,
            "file_name": file_record.file_name,
            "file_size": file_record.file_size_bytes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{file_id}] Signed URL error: {str(e)}")
        raise HTTPException(500, f"Failed to generate URL: {str(e)}")
```

### Client Code

```javascript
// File: frontend/downloadSigned.js

class SignedUrlDownloader {
  async download(fileId, authToken) {
    console.log(`Getting signed URL for: ${fileId}`);
    
    try {
      // Get signed URL from backend
      const resp = await fetch(`/api/files/${fileId}/signed-download-url`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      const { signed_url, file_name } = await resp.json();
      console.log('Got signed URL, downloading from S3...');
      
      // Download directly from S3 (no backend involved)
      const a = document.createElement('a');
      a.href = signed_url;
      a.download = file_name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
      console.log('Download started from S3');
      
    } catch (error) {
      console.error('Error:', error);
      throw error;
    }
  }
}

// Usage
const signedDownloader = new SignedUrlDownloader();
document.getElementById('download-signed-btn').addEventListener('click', async () => {
  const fileId = document.getElementById('file-id').value;
  const token = localStorage.getItem('auth_token');
  await signedDownloader.download(fileId, token);
});
```

---

## Strategy 4: CDN + CloudFront (Ultra-Fast Global Delivery)

### Architecture

```
User in Tokyo
        │
        ├─→ CloudFront Edge (Tokyo)
        │   │
        │   ├─ Cache HIT? → Return cached file
        │   │
        │   └─ Cache MISS? → Fetch from S3 (us-east-1)
        │                     Cache it for future requests
        │
        └─ Download: ~100ms from edge cache
            vs ~500ms from origin S3
```

### Setup Code

```python
# File: app/config/cdn_setup.py

import boto3

def setup_cloudfront_distribution():
    """
    Setup CloudFront distribution pointing to S3 bucket
    
    This is typically done once during infrastructure setup
    """
    
    client = boto3.client('cloudfront')
    
    distribution_config = {
        'CallerReference': 'file-sharing-cdn',
        'Comment': 'CDN for file downloads',
        'Enabled': True,
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'myS3Origin',
                    'DomainName': 'your-bucket.s3.amazonaws.com',
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'myS3Origin',
            'ViewerProtocolPolicy': 'https-only',
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'},
                'Headers': {
                    'Quantity': 1,
                    'Items': ['Authorization']
                }
            },
            'MinTTL': 0,
            'DefaultTTL': 86400,  # 24 hours
            'MaxTTL': 31536000,   # 1 year
            'Compress': True
        }
    }
    
    response = client.create_distribution(DistributionConfig=distribution_config)
    
    distribution_id = response['Distribution']['Id']
    domain_name = response['Distribution']['DomainName']
    
    print(f"CloudFront distribution created:")
    print(f"  ID: {distribution_id}")
    print(f"  Domain: {domain_name}")
    
    return distribution_id, domain_name

# In your FastAPI app:
CLOUDFRONT_DOMAIN = "d123456.cloudfront.net"

@app.get("/api/files/{file_id}/download-cdn")
async def download_via_cdn(
    file_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get CloudFront URL for cached download
    """
    
    file_record = db.query(FileMaster).filter(
        FileMaster.file_id == file_id
    ).first()
    
    if not file_record:
        raise HTTPException(404, "Not found")
    
    if not await check_read_permission(current_user.id, file_id, db):
        raise HTTPException(403)
    
    # Extract key from S3 path
    key = '/'.join(file_record.s3_path.split('/')[3:])
    
    # CloudFront URL (public or signed depending on bucket policy)
    cdn_url = f"https://{CLOUDFRONT_DOMAIN}/{key}"
    
    return {
        "cdn_url": cdn_url,
        "file_name": file_record.file_name
    }
```

---

## Strategy 5: Parallel Downloads (Advanced)

### Idea: Download multiple ranges simultaneously for speed

```
File: 1GB (1,000,000,000 bytes)
├─ Thread 1: bytes 0-249,999,999
├─ Thread 2: bytes 250,000,000-499,999,999
├─ Thread 3: bytes 500,000,000-749,999,999
└─ Thread 4: bytes 750,000,000-999,999,999

Result: 4x faster download (on good connection)
```

### Client Code

```javascript
// File: frontend/downloadParallel.js

class ParallelDownloader {
  constructor(options = {}) {
    this.parallelStreams = options.parallelStreams || 4;
    this.onProgress = options.onProgress || (() => {});
  }

  async download(fileId, authToken) {
    console.log(`Parallel download (${this.parallelStreams} streams): ${fileId}`);
    
    try {
      // Get file info
      const infoResp = await fetch(`/api/files/${fileId}/info`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      const { file_size_bytes: fileSize, file_name: fileName } = await infoResp.json();
      
      // Calculate chunk size
      const chunkSize = Math.ceil(fileSize / this.parallelStreams);
      
      // Download all chunks in parallel
      const downloadPromises = [];
      
      for (let i = 0; i < this.parallelStreams; i++) {
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize - 1, fileSize - 1);
        
        const promise = this.downloadChunk(fileId, start, end, authToken);
        downloadPromises.push(promise);
      }
      
      const chunks = await Promise.all(downloadPromises);
      
      // Combine chunks (must be in order!)
      const sortedChunks = chunks.sort((a, b) => a.index - b.index);
      const blobs = sortedChunks.map(c => c.blob);
      
      const fullBlob = new Blob(blobs);
      
      // Save
      const url = window.URL.createObjectURL(fullBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      a.click();
      window.URL.revokeObjectURL(url);
      
      console.log('Parallel download complete!');
      
    } catch (error) {
      console.error('Error:', error);
      throw error;
    }
  }

  async downloadChunk(fileId, start, end, authToken) {
    const resp = await fetch(`/api/files/${fileId}/download`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Range': `bytes=${start}-${end}`
      }
    });
    
    const blob = await resp.blob();
    const totalSize = parseInt(resp.headers.get('Content-Range').split('/')[1]);
    const downloadedBytes = [...document.querySelectorAll('progress')].reduce((s, p) => s + p.value, 0);
    
    this.onProgress((downloadedBytes / totalSize) * 100);
    
    return {
      index: Math.floor(start / (totalSize / this.parallelStreams)),
      blob
    };
  }
}

// Usage
const parallelDownloader = new ParallelDownloader({
  parallelStreams: 4,
  onProgress: (percent) => {
    console.log(`Download: ${percent.toFixed(2)}%`);
  }
});

document.getElementById('download-parallel-btn').addEventListener('click', async () => {
  const fileId = document.getElementById('file-id').value;
  const token = localStorage.getItem('auth_token');
  await parallelDownloader.download(fileId, token);
});
```

---

## 🌍 Real-World Download Examples

### Example 1: Dropbox-Style (4GB video file, global users)

**Setup**:
```python
# User in India downloads 4GB video from US-hosted S3

# Strategy: CloudFront + Signed URLs + HTTP Range

1. User: "Give me download link"
2. Backend: 
   - Check permissions
   - Generate signed S3 URL
   - Create CloudFront signed URL
   - Return URL (valid 1 hour)
3. User: Download directly from CloudFront edge in India
   - CloudFront caches it
   - Future users in India: instant!
   
Performance:
- Direct S3: ~500ms latency, $0.085 per GB
- CloudFront edge: ~50ms latency, $0.085 per GB (same cost!)
```

### Example 2: Corporate Enterprise (Secure download, audit log)

**Setup**:
```python
# Download must be tracked and verified

# Strategy: Backend proxy + Range + Audit

1. User: GET /api/files/{id}/download
2. Backend:
   - Check permission (every time!)
   - Stream from S3 in 8KB chunks
   - Log to audit table
   - Track bytes downloaded
3. If network fails:
   - User can resume with Range header
   - Backend returns 206 Partial Content
   - Resume from exact byte N

Benefits:
- Full audit trail
- Can revoke access mid-download (401)
- Bandwidth metering
```

### Example 3: Video Streaming (Large file, seek required)

**Setup**:
```python
# Video player (HTML5) needs to seek to 30 minutes into 2-hour video

# Strategy: Signed S3 URLs + CloudFront + HTTP Range

1. Video player: "I need bytes 1GB-1.5GB"
2. Browser: Request with Range header to CloudFront
3. CloudFront:
   - Already cached (1st view by user)
   - Return 206 Partial Content
   - ~100ms latency
4. Video player: Plays seamlessly

No backend involved!

Playback:
- Seek to 30m: 5ms + ~50ms network = ~55ms
- Start from beginning: 5ms + ~50ms network = ~55ms
```

---

## 📊 Comparison: Download Strategies

| Strategy | Small Files | Large Files | Mobile | Resume | Secure | Scalable | Cost |
|----------|-----------|-----------|--------|--------|--------|----------|------|
| **Simple Stream** | ⭐⭐⭐ | ❌ | ❌ | ❌ | ✅ | ⭐ | LOW |
| **Range Support** | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | ✅ | ✅ | ⭐⭐ | LOW |
| **Signed S3 URLs** | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | Partial | ⭐⭐ | ⭐⭐⭐ | LOW |
| **CDN + CloudFront** | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | Partial | ⭐⭐⭐ | ⭐⭐⭐ | MEDIUM |
| **Parallel Chunks** | ⭐⭐ | ⭐⭐⭐ | ✅ | ✅ | ✅ | ⭐⭐ | LOW |

---

## 🎯 Quick Decision Guide (Downloads)

```
QUESTION: Which download strategy?

File < 50MB
  → Simple stream (fast enough)

File 50MB-500MB
  → Signed S3 URL (fastest)
  → IF audit needed: Range support + backend

File 500MB-5GB
  → Signed S3 URL + CloudFront
  → Add HTTP Range if users on mobile

File > 5GB
  → Signed S3 URL + CloudFront
  → MUST support Range (resume)
  → Consider parallel downloads (4+ streams)

Critical: Need to revoke access mid-download?
  → Use backend proxy + Range
  → (Sacrifice speed for control)

Critical: Performance at any cost?
  → Signed S3 URL + CloudFront + CDN edge
  → Parallel downloads (8+ streams)
```

---

## 🔒 Security Checklist (Downloads)

```
☐ Permissions checked BEFORE generating signed URL
☐ Signed URLs time-limited (1 hour max)
☐ IP restrictions on signed URLs (optional)
☐ Audit log: who downloaded what, when
☐ Rate limiting: max downloads per user
☐ HTTPS only (no HTTP)
☐ S3 bucket policy restrictive
☐ Block direct S3 access (CloudFront only)
☐ Virus scan on download (optional)
☐ Watermark files (optional, legal holds)
```

---

