# System Design Interview - Group File Sharing System
## Comprehensive Review & Recommendations

---

## 📋 Executive Summary

**What You Got Right**:
- ✅ Normalized data model (no JSON permission columns)
- ✅ Understood async patterns for scalability
- ✅ Queue-based architecture for high load
- ✅ Permission hierarchy logic
- ✅ Size-based upload strategy
- ✅ Session management (Redis + identity tools)

**What Needs Refinement**:
- ⚠️ S3 organization strategy incomplete
- ⚠️ Pre-signed URL approach not considered
- ⚠️ Failure scenarios & atomicity gaps
- ⚠️ Download/streaming design missing
- ⚠️ Caching strategy not detailed
- ⚠️ Monitoring & observability gaps

---

## 🏗️ PART 1: DATA MODEL REVIEW

### Current Schema (Good Foundation)

```sql
-- Users
user_master (
  user_id PK,
  email UNIQUE,
  password_hash,
  created_at,
  is_active
)

-- Sessions (with Redis, this becomes less critical)
session_master (
  session_id PK,
  user_id FK,
  token,
  expires_at,
  created_at
) -- RECOMMENDATION: Move to Redis entirely

-- Groups
group_master (
  group_id PK,
  name,
  description,
  created_by FK(user_id),
  created_at,
  is_active
)

-- Group Membership + Permissions
group_user_mapping (
  id PK,
  group_id FK,
  user_id FK,
  role ENUM('admin', 'member', 'viewer'),
  permissions INT (octal: 4=read, 2=write, 1=delete, 0=none),
  created_at,
  UNIQUE(group_id, user_id),
  INDEX: (group_id, user_id), (user_id, group_id)
)

-- Files Shared with Groups
group_file_mapping (
  id PK,
  group_id FK,
  file_id FK,
  permissions INT (octal),
  shared_at,
  shared_by FK(user_id),
  UNIQUE(group_id, file_id),
  INDEX: (group_id, file_id), (file_id, group_id)
)

-- Individual File Access
user_file_mapping (
  id PK,
  file_id FK,
  user_id FK,
  permissions INT (octal),
  shared_at,
  shared_by FK(user_id),
  UNIQUE(file_id, user_id),
  INDEX: (user_id, file_id), (file_id, user_id)
)

-- FILE METADATA (YOU WERE MISSING THIS)
file_master (
  file_id PK UUID,
  file_name VARCHAR,
  file_type ENUM('audio', 'video', 'document', 'image', 'other'),
  file_size_bytes BIGINT,
  mime_type VARCHAR,
  uploaded_by FK(user_id),
  original_group_id FK(group_id), -- Where file originated
  s3_path VARCHAR UNIQUE,
  s3_etag VARCHAR, -- For consistency checking
  version INT DEFAULT 1,
  is_deleted BOOLEAN DEFAULT false,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  INDEX: (uploaded_by, created_at), (file_type), (is_deleted)
)

-- FILE ACTIVITY AUDIT LOG (FOR TRACKING)
file_audit_log (
  audit_id PK,
  file_id FK,
  user_id FK,
  action ENUM('upload', 'download', 'share', 'delete', 'view'),
  created_at TIMESTAMP,
  INDEX: (file_id, created_at), (user_id, created_at)
)

-- FILE UPLOAD TRACKING (FOR ASYNC UPLOADS)
file_upload_tracker (
  upload_id PK UUID,
  file_id FK file_master (nullable until S3 completes),
  user_id FK,
  status ENUM('initiated', 'in_progress', 'completed', 'failed'),
  total_size_bytes BIGINT,
  uploaded_bytes BIGINT,
  s3_multipart_upload_id VARCHAR (for resumable uploads),
  created_at TIMESTAMP,
  completed_at TIMESTAMP (nullable),
  error_message TEXT (nullable),
  INDEX: (user_id, created_at), (upload_id), (status)
)
```

### Schema Recommendations

**1. Add Soft Delete Support**
```sql
ALTER TABLE file_master ADD COLUMN deleted_at TIMESTAMP;
-- Allows recovery, maintains referential integrity
```

**2. Add Storage Quotas**
```sql
-- User quotas
CREATE TABLE user_storage_quota (
  user_id PK FK,
  quota_bytes BIGINT,
  used_bytes BIGINT,
  updated_at TIMESTAMP
)

-- Group quotas
CREATE TABLE group_storage_quota (
  group_id PK FK,
  quota_bytes BIGINT,
  used_bytes BIGINT,
  updated_at TIMESTAMP
)
```

**3. Add File Versioning**
```sql
CREATE TABLE file_version (
  version_id PK,
  file_id FK,
  version_number INT,
  s3_path VARCHAR,
  uploaded_by FK(user_id),
  created_at,
  file_size BIGINT,
  PRIMARY KEY (file_id, version_number)
)
```

---

## 🎬 PART 2: API DESIGN & UPLOAD FLOW

### Recommended API Endpoints

```
Authentication:
  POST   /auth/login              -> JWT token + refresh token
  POST   /auth/logout
  POST   /auth/refresh

Groups:
  POST   /groups                  -> Create group
  GET    /groups/{group_id}       -> Get group details
  GET    /groups                  -> List user's groups
  POST   /groups/{group_id}/members/{user_id}  -> Add member
  DELETE /groups/{group_id}/members/{user_id}  -> Remove member

Files:
  POST   /groups/{group_id}/files/upload        -> Upload file
  POST   /files/{file_id}/presigned-url         -> Get presigned URL
  GET    /groups/{group_id}/files               -> List group files
  GET    /files/{file_id}/download              -> Download file
  GET    /files/{file_id}/stream                -> Stream file (audio/video)
  PUT    /files/{file_id}                       -> Update file metadata/permissions
  DELETE /files/{file_id}                       -> Delete file
  GET    /files/{file_id}/activity              -> Get activity/audit log

Sharing:
  POST   /files/{file_id}/share                 -> Share file with user/group
  DELETE /files/{file_id}/share/{user_id}       -> Revoke access
  GET    /files/{file_id}/permissions           -> Get who has access
```

### Upload Flow (Detailed)

**Endpoint**: `POST /groups/{group_id}/files/upload`

**Request**:
```json
{
  "file": "multipart/form-data",
  "file_name": "audio_interview.mp3",
  "description": "Q4 Planning Discussion",
  "individual_users": [
    {"user_id": "user_123", "permissions": 4}  // 4 = read-only
  ],
  "groups": [
    {"group_id": "group_456", "permissions": 5}  // 5 = read + delete
  ]
}
```

**Response (Immediate)**:
```json
{
  "upload_id": "upload_uuid_12345",
  "file_id": "file_uuid_67890",
  "status": "uploading",
  "message": "File upload initiated. Track progress with upload_id."
}
```

**Upload Flow Sequence**:

```
1. CLIENT REQUEST
   ├─ Method: POST /groups/{group_id}/files/upload
   ├─ Auth: Validate JWT token
   └─ Payload: form-data with file + metadata

2. BACKEND VALIDATION
   ├─ Verify user has WRITE permission in group
   ├─ Check user storage quota (not exceeded)
   ├─ Check group storage quota
   ├─ Validate file size (max 5GB per file)
   ├─ Check file type whitelist (if any)
   └─ REJECT if any validation fails (400 error)

3. FILE SIZE DECISION TREE
   
   IF file_size < 100MB:
   ├─ SYNC UPLOAD PATH
   ├─ Upload to S3 directly
   ├─ Update file_master
   ├─ Insert into group_file_mapping & user_file_mapping
   ├─ Update storage quotas
   └─ Return 200 OK

   ELSE (file_size >= 100MB):
   ├─ ASYNC UPLOAD PATH
   ├─ Generate file_id (UUID)
   ├─ Generate upload_id (UUID)
   ├─ Create file_master record (status='pending')
   ├─ Create file_upload_tracker record (status='initiated')
   ├─ Queue SQS message with upload task
   ├─ Return 202 Accepted (immediate response)
   └─ Background processing continues...

4. ASYNC PROCESSING (Large Files)
   
   Listener Service (Lambda or worker):
   ├─ Poll SQS queue
   ├─ Get upload task
   ├─ Update file_upload_tracker (status='in_progress')
   
   IF file_size > 500MB:
   │  ├─ Use S3 Multipart Upload (5GB parts)
   │  ├─ Store multipart_upload_id in tracker
   │  ├─ Upload chunks with progress updates
   │  └─ Complete multipart upload
   ELSE:
   │  └─ Standard S3 PutObject
   
   ├─ Verify S3 upload (check ETag)
   ├─ Update file_master:
   │  ├─ s3_path = 's3://bucket/group_{group_id}/file_{file_id}'
   │  ├─ status = 'completed'
   │  └─ updated_at = now()
   ├─ Insert into group_file_mapping
   ├─ Insert individual user_file_mapping entries
   ├─ Create file_audit_log entry (action='upload')
   ├─ Update storage quotas
   ├─ Mark file_upload_tracker (status='completed')
   └─ Send notification to user (email/push)

5. ERROR HANDLING
   
   S3 Upload Fails:
   ├─ Update file_upload_tracker (status='failed', error_message)
   ├─ Send to DLQ (Dead Letter Queue)
   ├─ Alert user via email
   └─ Retry (exponential backoff, max 3 attempts)
   
   DB Insert Fails:
   ├─ S3 file exists but DB entry missing
   ├─ Retry DB operation (max 3 times)
   ├─ If still fails:
   │  ├─ Create ticket for manual recovery
   │  ├─ Alert admin
   │  └─ Leave S3 file for manual cleanup job
   └─ User notified of partial failure
   
   Quota Exceeded:
   ├─ Reject upload (400 Bad Request)
   ├─ Return available quota info
   └─ User must delete files or upgrade

6. CLEANUP (Background Job - Daily)
   
   Find Orphaned Files:
   ├─ S3 files without file_master entries
   ├─ file_upload_tracker stuck in 'in_progress' for >2 hours
   ├─ Mark for deletion
   └─ Generate report
```

### S3 Organization Strategy (Recommended)

```
Bucket Structure:
s3://group-file-sharing-prod/
├─ groups/
│  ├─ group_{group_id}/
│  │  ├─ {file_id}/
│  │  │  ├─ original/
│  │  │  │  └─ {file_hash}_{timestamp}  # Original file
│  │  │  └─ versions/
│  │  │     ├─ v1__{file_hash}
│  │  │     ├─ v2__{file_hash}
│  │  │     └─ v3__{file_hash}
│  │  └─ {file_id}/
│  └─ group_{another_id}/
├─ temp/
│  └─ multipart-uploads/        # For resumable uploads
└─ deleted/
   └─ {file_id}__{deleted_at}   # Soft deleted files (30-day retention)

Benefits:
- Hierarchical (easy to query/organize)
- Versioning support
- Easy to apply S3 lifecycle policies
- Audit trail possible
- Delete operations reversible
```

### Pre-signed URLs (Recommended for Large Files)

```python
# For files > 500MB, use pre-signed URLs

@app.post("/files/{file_id}/presigned-url")
async def get_presigned_upload_url(file_id: str, user: User):
    # 1. Verify user has write permission
    # 2. Check quota
    # 3. Generate S3 presigned URL (15-minute expiry)
    
    s3_client = boto3.client('s3')
    presigned_url = s3_client.generate_presigned_post(
        Bucket='bucket-name',
        Key=f'groups/group_{group_id}/{file_id}/original',
        ExpiresIn=900,  # 15 minutes
        Conditions=[
            ['content-length-range', 0, 5_368_709_120]  # 5GB max
        ]
    )
    
    return {
        "upload_url": presigned_url['url'],
        "form_fields": presigned_url['fields'],
        "file_id": file_id,
        "expires_in": 900
    }

# Client uploads directly to S3
# Backend polls for completion or uses S3 event notification
```

---

## ⬇️ PART 3: DOWNLOAD/STREAMING FLOW

### Download API Design

```python
@app.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    user: User,
    request: Request
):
    """
    Handle file downloads with:
    - Permission validation
    - HTTP Range requests (pause/resume)
    - Streaming for large files
    - Audit logging
    """
    
    # 1. Check permission (from cache first)
    perm = await check_file_permission(file_id, user.id)
    if not perm or not (perm & 4):  # 4 = read permission
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 2. Get file metadata
    file = await get_file_metadata(file_id)
    
    # 3. Handle Range requests (for resume/seek)
    range_header = request.headers.get("Range")
    if range_header:
        start, end = parse_range_header(range_header, file.size)
        # Return partial content (206)
    else:
        start, end = 0, file.size - 1
    
    # 4. Stream from S3
    stream = await stream_from_s3(file.s3_path, start, end)
    
    # 5. Log download (async, don't block response)
    asyncio.create_task(log_file_access(file_id, user.id, 'download'))
    
    return StreamingResponse(
        stream,
        media_type=file.mime_type,
        headers={
            "Content-Range": f"bytes {start}-{end}/{file.size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1)
        },
        status_code=206 if range_header else 200
    )
```

### Audio Streaming Specifics

```python
@app.get("/files/{file_id}/stream")
async def stream_audio(file_id: str, user: User):
    """
    Optimized for audio streaming:
    - Range request support (seek)
    - Adaptive bitrate (optional transcoding)
    - Client-side caching hints
    """
    
    # 1. Permission check (cached)
    if not await has_read_permission(file_id, user.id):
        raise HTTPException(403)
    
    file = await get_file_metadata(file_id)
    
    # 2. For audio, enable seeking (HTTP 206 Partial Content)
    # 3. Set cache headers for better mobile experience
    
    return StreamingResponse(
        stream_audio_from_s3(file.s3_path),
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "private, max-age=3600",  # 1 hour cache
            "Content-Disposition": f'inline; filename="{file.file_name}"'
        }
    )
```

---

## 🚀 PART 4: CACHING STRATEGY (Redis)

### What to Cache

```python
# Cache Layer Architecture

CACHE_KEYS = {
    # User permissions (high hit rate)
    "user_files:{user_id}": {
        "ttl": 300,  # 5 minutes
        "invalidate_on": ["file_share", "file_delete", "permission_change"]
    },
    
    # File metadata (medium hit rate)
    "file_meta:{file_id}": {
        "ttl": 600,  # 10 minutes
        "invalidate_on": ["file_update", "file_delete"]
    },
    
    # Group info (high hit rate)
    "group:{group_id}": {
        "ttl": 1800,  # 30 minutes
        "invalidate_on": ["group_update"]
    },
    
    # Group members (medium hit rate)
    "group_members:{group_id}": {
        "ttl": 600,
        "invalidate_on": ["member_add", "member_remove"]
    },
    
    # Session tokens (critical)
    "session:{session_id}": {
        "ttl": 3600,  # 1 hour (JWT exp)
        "invalidate_on": ["logout"]
    },
    
    # File access control (high hit rate)
    "file_perms:{file_id}:{user_id}": {
        "ttl": 300,
        "invalidate_on": ["permission_change"]
    }
}
```

### Redis Implementation

```python
import redis
from typing import Optional, Dict

class CacheManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def get_file_permissions(self, file_id: str, user_id: str) -> Optional[int]:
        """Get user's permission for file (4=read, 2=write, 1=delete)"""
        cache_key = f"file_perms:{file_id}:{user_id}"
        
        # Try cache first
        cached = await self.redis.get(cache_key)
        if cached:
            return int(cached)
        
        # Cache miss - query DB
        perm = await get_permission_from_db(file_id, user_id)
        
        if perm is not None:
            # Cache for 5 minutes
            await self.redis.setex(cache_key, 300, str(perm))
        
        return perm
    
    async def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Get file metadata with caching"""
        cache_key = f"file_meta:{file_id}"
        
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        file_data = await get_file_from_db(file_id)
        
        if file_data:
            await self.redis.setex(
                cache_key,
                600,
                json.dumps(file_data, default=str)
            )
        
        return file_data
    
    async def invalidate_file_cache(self, file_id: str):
        """Invalidate all caches related to a file"""
        pattern = f"file_meta:{file_id}*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

---

## ⚙️ PART 5: SCALABILITY & HIGH AVAILABILITY

### Architecture for 100K Users, 1M Files

```
                    ┌──────────────────────┐
                    │   Users (100K)       │
                    │   Concurrent: ~5K    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  CloudFront CDN      │
                    │  (File Caching)      │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │                             │
       ┌────────▼────────┐         ┌─────────▼─────────┐
       │  ALB            │         │  S3 (File Storage)│
       │ (Load Balancer) │         │  (TB-scale)       │
       └────────┬────────┘         └───────────────────┘
                │
       ┌────────┴──────────┬─────────────┬─────────────┐
       │                   │             │             │
   ┌───▼──┐          ┌──────▼───┐  ┌───▼───┐    ┌───▼────┐
   │FastAPI│          │FastAPI   │  │FastAPI│    │FastAPI │
   │ Inst1 │          │ Inst2    │  │ Inst3 │    │ InstN  │
   └───┬──┘          └──────┬───┘  └───┬───┘    └───┬────┘
       │                   │            │            │
       └───────────────────┼────────────┼────────────┘
                           │
                ┌──────────┴──────────┐
                │                    │
           ┌────▼────┐          ┌────▼─────┐
           │ Redis   │          │RDS PG    │
           │ (Cache) │          │(DB)      │
           │ Cluster │          │ Primary  │
           └────┬────┘          └──┬──┬────┘
                │                  │  │
                │                  │  └──────────┐
                │                  │             │
                │             ┌────▼──┐     ┌────▼──┐
                │             │PG Read│     │PG Read│
                │             │Replica│     │Replica│
                │             └───────┘     └───────┘
                │
       ┌────────▼──────────┐
       │  SQS/RabbitMQ     │
       │  (Task Queue)     │
       └────────┬──────────┘
                │
       ┌────────▼──────────┐
       │ Lambda Workers    │
       │ (File Processing) │
       │ (Auto-scaling)    │
       └───────────────────┘
```

### Scaling Checklist

```
Database Optimization:
✅ Read replicas for query load
✅ Connection pooling (PgBouncer)
✅ Partitioning on file_audit_log (by date)
✅ Query optimization + EXPLAIN ANALYZE
✅ Vacuum/analyze regularly

Redis Caching:
✅ Redis cluster (3 masters for HA)
✅ Key TTL strategy (5-30 min)
✅ Cache invalidation on writes
✅ Monitor hit rate (target: >80%)

API Scalability:
✅ Horizontal scaling (multiple FastAPI instances)
✅ Connection pooling to DB
✅ Async operations (don't block on I/O)
✅ Rate limiting (per user, per IP)
✅ Request timeout (30s for downloads, 60s for uploads)

Queue Processing:
✅ Auto-scaling workers (AWS Lambda or ECS)
✅ Dead Letter Queue for failed tasks
✅ Monitoring: queue depth, processing time
✅ Backoff strategy for retries

S3 Optimization:
✅ CloudFront CDN for frequently accessed files
✅ S3 Transfer Acceleration for uploads
✅ Lifecycle policies (archive old files)
✅ Server-side encryption
✅ Versioning + MFA Delete

Monitoring & Observability:
✅ Datadog/ELK for logs
✅ Prometheus for metrics
✅ CloudWatch for AWS services
✅ Alerts for: high latency, error rates, queue depth
```

---

## 🔒 PART 6: SECURITY CONSIDERATIONS

### Authentication & Authorization

```python
# JWT-based authentication
@app.post("/auth/login")
async def login(email: str, password: str):
    user = await authenticate_user(email, password)
    
    access_token = create_jwt_token(
        user_id=user.id,
        exp=timedelta(hours=1)
    )
    refresh_token = create_jwt_token(
        user_id=user.id,
        exp=timedelta(days=7),
        token_type="refresh"
    )
    
    # Store refresh token in Redis
    await redis.setex(
        f"refresh:{refresh_token}",
        7 * 24 * 3600,
        user.id
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

# Permission checking middleware
async def verify_file_access(file_id: str, user_id: str):
    """
    Check permission with hierarchy:
    1. User explicit permission (user_file_mapping)
    2. Group permission (group_file_mapping + group_user_mapping)
    """
    perm = await cache_manager.get_file_permissions(file_id, user_id)
    return perm is not None and perm > 0
```

### File Security

```
✅ Virus scanning (ClamAV on upload)
✅ File type validation (whitelist MIME types)
✅ S3 encryption at rest (AES-256)
✅ HTTPS/TLS in transit
✅ Signed URLs (time-limited, revokable)
✅ Audit logging (who accessed what, when)
✅ Rate limiting (prevent abuse)
✅ CORS configuration (restrict to frontend domain)
```

---

## 📊 PART 7: MONITORING & OBSERVABILITY

### Key Metrics to Track

```
Upload Metrics:
- Upload success rate (%)
- Average upload latency (ms)
- Max file size uploaded
- Queue depth (SQS)
- Worker processing time

Download Metrics:
- Download success rate (%)
- Average download latency (ms)
- Bandwidth utilization (GB/s)
- Concurrent downloads

Database Metrics:
- Query latency p50/p95/p99
- Connection pool utilization
- Slow queries (>1s)
- Replication lag (read replicas)

Cache Metrics:
- Hit rate (%) - target >80%
- Eviction rate
- Memory usage
- TTL expirations

Error Tracking:
- Error rate (%) - target <0.1%
- Error types (timeout, permission denied, etc.)
- Stack traces (Sentry)
- User impact (affected users count)
```

### Recommended Tools

```
Logging:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- CloudWatch (AWS native)
- Structured logging (JSON format)

Metrics:
- Prometheus (open-source)
- Datadog (commercial, more features)
- CloudWatch Metrics

Tracing:
- Jaeger (distributed tracing)
- AWS X-Ray (AWS native)

Alerting:
- PagerDuty (on-call management)
- Slack notifications (for critical alerts)
- Email alerts (for warnings)
```

---

## 🎯 PART 8: RECOMMENDATIONS BY PRIORITY

### Immediate (Week 1)

1. **Add file_master table** (you're missing this)
   - Stores: file_id, name, size, s3_path, uploaded_by, created_at
   - Critical for file list operations

2. **Implement Redis caching**
   - Cache: file permissions, group info, user sessions
   - Hit rate target: >80%

3. **Add audit logging**
   - Track: who uploaded, downloaded, shared files
   - Use file_audit_log table

4. **Implement proper error handling**
   - Try-catch on all DB operations
   - DLQ for failed queue tasks
   - User notifications on failure

### Short-term (Weeks 2-4)

5. **Pre-signed URLs for large file uploads**
   - Reduces backend load
   - Faster uploads for >500MB files
   - Client uploads directly to S3

6. **Queue-based async processing**
   - AWS SQS or RabbitMQ
   - Lambda or dedicated workers
   - Auto-scaling based on queue depth

7. **Implement download streaming**
   - Support HTTP Range requests
   - Efficient memory usage
   - Resume capability

8. **Add storage quotas**
   - Per-user limits
   - Per-group limits
   - Quota enforcement on upload

### Medium-term (Months 2-3)

9. **Set up monitoring & alerts**
   - Datadog/ELK for logs
   - Prometheus for metrics
   - PagerDuty for on-call

10. **CDN integration (CloudFront)**
    - Cache frequently accessed files
    - Reduce S3 bandwidth costs
    - Improve download speeds

11. **Database read replicas**
    - Separate read traffic from writes
    - Reduce query latency
    - Improve availability

12. **Rate limiting & DDoS protection**
    - AWS WAF for API protection
    - Token bucket algorithm for rate limiting

### Long-term (Months 4+)

13. **Multi-region deployment**
    - Replicate to multiple AWS regions
    - Route traffic based on latency
    - Disaster recovery

14. **Advanced features**
    - File versioning (keep history)
    - File deduplication (save storage)
    - Full-text search
    - Activity feed/notifications

---

## 🔄 PART 9: FAILURE SCENARIOS & HANDLING

### Scenario: S3 Upload Succeeds, DB Fails

```
Timeline:
1. 10:00:00 - File uploaded to S3 ✓
2. 10:00:02 - DB insert fails (connection timeout) ✗
3. File exists in S3 but no record in DB
4. User doesn't know status
5. File takes up S3 storage but isn't accessible

Solution:
- Use file_upload_tracker with status field
- Retry DB operation with exponential backoff (3 attempts)
- If still fails, create ticket for manual recovery
- Background cleanup job finds orphaned S3 files
- User is notified of partial failure + next steps
- Option to retry upload
```

### Scenario: User Loses Network During Upload

```
Without Range Requests:
- Upload restarts from 0 byte
- User wastes bandwidth
- Frustrating experience

With Range Requests + Multipart Upload:
- Resume from byte where connection broke
- Only missing bytes are re-uploaded
- Much better UX for large files
```

### Scenario: User Removed from Group

```
When user is removed from group_user_mapping:
- Their group-based file access should revoke
- But if they have user_file_mapping (individual share), keep it
- Clear distinction in permission logic

Implementation:
1. Delete group_user_mapping record
2. Keep user_file_mapping entries (they still have individual access)
3. Cache invalidation for: user_files:{user_id}
4. User can still access individually shared files
```

---

## 📝 PART 10: ADDITIONAL CONSIDERATIONS

### File Versioning (Optional but Recommended)

```sql
CREATE TABLE file_version (
  version_id UUID PRIMARY KEY,
  file_id UUID FK,
  version_number INT,
  s3_path VARCHAR,
  file_size BIGINT,
  uploaded_by UUID FK,
  created_at TIMESTAMP,
  is_current BOOLEAN DEFAULT true,
  UNIQUE(file_id, version_number)
)
```

### Deduplication (For Cost Savings)

```
Store file hash (SHA256) in file_master
Before uploading, check if hash exists
If exists, link to existing S3 object instead of uploading again
Saves storage but need copy-on-write for modifications
```

### Full-Text Search (Future Feature)

```
Use Elasticsearch for file search
Index: file_name, description, content (for documents)
Search across files user has access to
Requires indexing pipeline from S3/database
```

---

## ✅ FINAL CHECKLIST

**Before Going to Production**:

- [ ] Unit tests (>80% coverage)
- [ ] Integration tests (API, DB, S3)
- [ ] Load testing (100K users, 1M files)
- [ ] Security audit (OWASP top 10)
- [ ] Disaster recovery plan (backup/restore)
- [ ] Monitoring setup (dashboards, alerts)
- [ ] Documentation (API, architecture, runbooks)
- [ ] Change management process
- [ ] Incident response process
- [ ] SLA definition (99.9% uptime)

---

## 🎓 WHAT YOU DID WELL

1. ✅ **Understood async patterns** - Correctly identified queue-based processing for scalability
2. ✅ **Normalized schema** - Avoided JSON columns, proper entity separation
3. ✅ **Permission hierarchy** - Correctly implemented user override > group permission
4. ✅ **Session management** - Redis for scale, identity tools for enterprise
5. ✅ **Size-based strategies** - Different approaches for small vs large files
6. ✅ **Error handling mindset** - Considered failures and notifications

---

## 🚀 WHAT YOU NEED TO IMPROVE

1. ⚠️ **File metadata table** - You never defined file_master schema
2. ⚠️ **Download design** - Didn't think through streaming, range requests
3. ⚠️ **Caching strategy** - Didn't detail what/how to cache
4. ⚠️ **Failure scenarios** - Missed edge cases (S3 success, DB fail)
5. ⚠️ **Monitoring** - No discussion of metrics, alerts, observability
6. ⚠️ **Atomicity** - Transaction handling not clear
7. ⚠️ **Pre-signed URLs** - Didn't consider direct S3 uploads
8. ⚠️ **Audit logging** - No activity tracking table

---

## 🎯 FOR YOUR NEXT INTERVIEW

**When they ask about file sharing systems, remember to cover**:

1. **Data Model** - Draw normalized schema (user, group, file, mappings)
2. **Upload Flow** - Sync for small, async + queue for large
3. **Download Flow** - Streaming, range requests, caching
4. **API Design** - RESTful endpoints, pagination, error handling
5. **Caching** - Redis strategy, TTL, invalidation
6. **Scalability** - Horizontal scaling, read replicas, CDN
7. **Security** - JWT auth, permission checking, audit logs
8. **Monitoring** - Metrics, alerts, dashboards
9. **Failure Handling** - Orphaned files, retries, DLQ
10. **Trade-offs** - Why each decision, pros/cons

**Practice questions to ask yourself**:
- "How would this handle 10M users?"
- "What happens if S3 goes down?"
- "How do you prevent one user from overloading the system?"
- "What's the biggest bottleneck in this design?"
- "How would you migrate data if you change storage provider?"

---

