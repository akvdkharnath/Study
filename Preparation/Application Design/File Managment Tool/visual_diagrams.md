# Visual System Design - Group File Sharing System

## 1. COMPLETE SYSTEM ARCHITECTURE

```
                          ┌─────────────────────────────────────┐
                          │     100K Users (Concurrent: ~5K)    │
                          └──────────────┬──────────────────────┘
                                         │
                          ┌──────────────▼──────────────┐
                          │   CloudFront CDN            │
                          │  (Caching Layer)            │
                          └──────────────┬──────────────┘
                                         │
                          ┌──────────────▼──────────────┐
                          │   AWS ALB                   │
                          │  (Load Balancer)            │
                          └──────────────┬──────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
   ┌────▼───┐    ┌───────┐    ┌──────┐  │   ┌──────────────┐    ┌───────▼──┐
   │FastAPI │    │FastAPI│    │FastAPI   │   │  Redis Cluster│    │   S3    │
   │Inst-1  │    │Inst-2 │    │Inst-N    │   │  (3 nodes)   │    │ Storage │
   └────┬───┘    └───┬───┘    └──┬───┘   │   └──────┬───────┘    └─────────┘
        │             │            │      │          │
        └─────────────┼────────────┘      │          │
                      │                   │          │
            ┌─────────▼──────────┐        │    ┌────▼──────────┐
            │   Connection Pool  │        │    │  Cache Keys:  │
            │   (PgBouncer)      │◄───────┼────│ user_files    │
            └─────────┬──────────┘        │    │ file_perms    │
                      │                   │    │ group_info    │
            ┌─────────▼──────────┐        │    │ sessions      │
            │   RDS PostgreSQL   │        │    └───────────────┘
            │   (Primary)        │        │
            └─────────┬──────────┘        │
                      │                   │
        ┌─────────────┴─────────────┐     │
        │                           │     │
   ┌────▼─────┐          ┌────────▼──┐   │
   │  Read    │          │  Read     │   │
   │ Replica1 │          │ Replica2  │   │
   └──────────┘          └───────────┘   │
                                         │
                          ┌──────────────▼──────────────┐
                          │  AWS SQS                    │
                          │  (Message Queue)           │
                          └──────────────┬──────────────┘
                                         │
        ┌────────────────────────────────┘
        │
   ┌────▼──────────────────────────┐
   │  AWS Lambda Workers            │
   │  (Auto-scaling)                │
   │  - Process uploads             │
   │  - Handle retries              │
   │  - Notify users                │
   └───────────────────────────────┘
```

---

## 2. DATABASE SCHEMA DIAGRAM

```
┌────────────────────────────────────┐
│       user_master                  │
├────────────────────────────────────┤
│ PK: user_id (UUID)                 │
│ - email (UNIQUE)                   │
│ - password_hash                    │
│ - name                             │
│ - created_at                       │
│ - is_active                        │
└────────────┬───────────────────────┘
             │ 1:M
             │
    ┌────────┴────────┬───────────────────────────────┐
    │                 │                               │
    │                 │                               │
┌───▼──────────────┐ │ ┌────────────────────┐    ┌───▼──────────────┐
│ group_user_      │ │ │ user_file_mapping  │    │ file_audit_log   │
│ mapping          │ │ ├────────────────────┤    ├──────────────────┤
├──────────────────┤ │ │ PK: id             │    │ PK: audit_id     │
│ PK: id           │ │ │ FK: file_id        │    │ FK: file_id      │
│ FK: group_id ────┼─┼─┤ FK: user_id ───────┼────│ FK: user_id      │
│ FK: user_id ─────┼─┤ │ permissions (INT)  │    │ action (ENUM)    │
│ role (ENUM)      │ │ │ shared_at          │    │ created_at       │
│ permissions (INT)│ │ │ shared_by          │    └──────────────────┘
│ created_at       │ │ └────────────────────┘
└──────────────────┘ │
                     │
            ┌────────▼────────┐
            │ group_master    │
            ├─────────────────┤
            │ PK: group_id    │
            │ name            │
            │ description     │
            │ created_by ─────┤────┐
            │ created_at      │    │ (self-join to user_id)
            │ is_active       │
            └────────┬────────┘
                     │ 1:M
                     │
        ┌────────────┘
        │
        │
┌───────▼──────────────────┐
│ group_file_mapping       │
├──────────────────────────┤
│ PK: id                   │
│ FK: group_id             │
│ FK: file_id ─────┐       │
│ permissions (INT)│       │
│ shared_at        │       │
│ shared_by        │       │
└──────────────────┘       │
                           │
                 ┌─────────▼────────────────┐
                 │ file_master              │
                 ├────────────────────────┤
                 │ PK: file_id (UUID)     │
                 │ file_name               │
                 │ file_type (ENUM)        │
                 │ file_size_bytes         │
                 │ mime_type               │
                 │ uploaded_by ────────────┤──┐ (FK to user_id)
                 │ original_group_id       │  │
                 │ s3_path (UNIQUE)        │  │
                 │ s3_etag                 │  │
                 │ version (INT)           │  │
                 │ is_deleted (BOOL)       │  │
                 │ created_at              │  │
                 │ updated_at              │  │
                 └────────────────────────┘  │
                                             │
                                      (FK reference)

┌─────────────────────────────────────┐
│ file_upload_tracker                 │
├─────────────────────────────────────┤
│ PK: upload_id (UUID)                │
│ FK: file_id (nullable until done)   │
│ FK: user_id                         │
│ status (ENUM: initiated, progress,  │
│        completed, failed)           │
│ total_size_bytes                    │
│ uploaded_bytes                      │
│ s3_multipart_upload_id              │
│ created_at                          │
│ completed_at (nullable)             │
│ error_message (nullable)            │
└─────────────────────────────────────┘

Index Strategy:
- group_user_mapping: (group_id, user_id), (user_id, group_id)
- group_file_mapping: (group_id, file_id), (file_id, group_id)
- user_file_mapping: (user_id, file_id), (file_id, user_id)
- file_audit_log: (file_id, created_at), (user_id, created_at)
- file_master: (uploaded_by, created_at), (file_type), (is_deleted)
```

---

## 3. FILE UPLOAD SEQUENCE DIAGRAM

```
Client              Backend API        S3           DB        SQS Queue      Lambda
  │                     │              │            │             │            │
  ├─ POST upload ───────>               │            │             │            │
  │  (form-data)         │              │            │             │            │
  │                      │              │            │             │            │
  │                ┌─ Validate ──────┐  │            │             │            │
  │                │ - Auth          │  │            │             │            │
  │                │ - Permissions   │  │            │             │            │
  │                │ - File type     │  │            │             │            │
  │                │ - Quota         │  │            │             │            │
  │                └─────────────────┘  │            │             │            │
  │                      │              │            │             │            │
  │              ┌──────Decision────┐    │            │             │            │
  │              │ File Size?       │    │            │             │            │
  │              └──────┬───────────┘    │            │             │            │
  │                     │                │            │             │            │
  │         ┌───────────┴──────────┐     │            │             │            │
  │         │                      │     │            │             │            │
  │      <100MB             >=100MB │     │            │             │            │
  │         │                      │     │            │             │            │
  │  [SYNC PATH]           [ASYNC PATH]  │            │             │            │
  │         │                      │     │            │             │            │
  │         │          ┌─ Generate ID ──>│            │             │            │
  │         │          │ upload_id      │             │             │            │
  │         │          │              │ CREATE      │             │            │
  │         │          │              │ file_upload_│             │            │
  │         │          │              │ tracker     │             │            │
  │         │          │              │ (status=   │             │            │
  │         │          │              │ initiated) │             │            │
  │         │          │              │<────────┐  │             │            │
  │         │          │                        │  │             │            │
  │  ┌──────▼──────┐   │  ┌─────────────────┐   │  │  ┌─ Send ─>│             │
  │  │Upload to S3 │   │  │ Immediate       │   │  │  │ Task to │             │
  │  │             │   │  │ Response: 202   │   │  │  │ Queue   │             │
  │<─┤ (PUT object)┤   │  │ (Accepted)      │   │  │  │         │             │
  │  │             │   │  │ upload_id       │   │  │  └─────────>             │
  │  └──────┬──────┘   │  └──┬──────────────┘   │  │             │             │
  │<────────┤ 200 OK   │     │                  │  │             │  Poll Queue │
  │         │          │     └─ Return 202 ────>     │             │<────┐      │
  │         │          │        (client waits)       │             │     │      │
  │         │          │                              │             │     │      │
  │  [INSERT DB]       │                              │             │  Get Task  │
  │         │          │                              │             │     │      │
  │ ┌──────▼────────┐  │                              │  ┌─────────┴────┐│      │
  │ │file_master    │  │                              │  │             ││      │
  │ │group_file_    │  │                              │  │  [Lambda    ││      │
  │ │mapping        │  │                              │  │   Execution]│      │
  │ │user_file_     │  │                              │  │             │      │
  │ │mapping        │  │                              │  │ 1. S3       │      │
  │ │               │  │                              │  │    Upload   │      │
  │ │ ✓ Completed   │  │                              │  │    (multipart
  │ └───────────────┘  │                              │  │    if >500MB)
  │                    │                              │  │             │
  │                    │                              │  │ 2. Update   │
  │                    │                              │  │    file_    │
  │                    │                              │  │    upload_  │
  │                    │                              │  │    tracker  │
  │                    │                              │  │             │
  │                    │                              │  │ 3. Insert   │
  │                    │                              │  │    mappings │
  │                    │                              │  │             │
  │                    │                              │  │ 4. Update   │
  │                    │                              │  │    quotas   │
  │                    │                              │  │             │
  │                    │ ◄────────────────────────────────────┐      │
  │                    │  (Optional webhook or SNS)           │      │
  │                    │                              │      Send    │
  │<─ Notify User: Done (email/push)───────────────────┘ Notification│
  │                    │                              │             │
```

---

## 4. FILE DOWNLOAD SEQUENCE

```
Client              Backend API        S3          Redis Cache
  │                     │              │             │
  ├─ GET /files/{id} ──>               │             │
  │  /download          │              │             │
  │                      │              │             │
  │                ┌─ Check Auth ────┐  │             │
  │                │ - Validate JWT  │  │             │
  │                └─────────────────┘  │             │
  │                      │              │             │
  │                ┌─ Check Permission ─┐│             │
  │                │ Cache Lookup       └┤─ Miss ────>│
  │                │ file_perms:        │             │
  │                │ {file_id}:{user_id}│            │
  │                └────────┬───────────┘│             │
  │                         │            │             │
  │              ┌──────────Decision──┐   │   ┌─ Hit ─┐
  │              │ Permission?       │   │   │ Return│
  │              │ 4 (read) bit set? │   │   │ perm  │
  │              └────────┬──────────┘   │   └───────┘
  │                       │               │
  │         ┌─────────────┴──────────┐   │
  │         │                        │   │
  │       YES                       NO   │
  │         │                        │   │
  │         │         ┌──────────────▼┐  │
  │         │         │ 403 Forbidden │  │
  │         │<────────┤ Access Denied │  │
  │         │         └───────────────┘  │
  │         │
  │  ┌──────▼──────────────────┐
  │  │ Get File Metadata       │
  │  │ (from cache or DB)      │
  │  │ - size                  │
  │  │ - mime_type             │
  │  │ - s3_path               │
  │  └──────┬──────────────────┘
  │         │
  │  ┌──────▼──────────────────┐
  │  │ Check HTTP Range Header │
  │  │ (for resume/seek)       │
  │  │ "Range: bytes=0-1023"   │
  │  └──────┬──────────────────┘
  │         │
  │  ┌──────▼──────────────────┐
  │  │ Stream from S3          │
  │  └──────┬──────────────────┘
  │         │
  │<────────┤ 200 OK (or 206 Partial)
  │ File    │ Content-Range: bytes 0-1023/10485760
  │ Data    │ Accept-Ranges: bytes
  │ Stream  │ Cache-Control: private, max-age=3600
  │         │
  │[Download complete]
  │
  └─ Log Access (async)──>│ UPDATE file_audit_log
                          │ (action='download')
```

---

## 5. PERMISSION CHECKING LOGIC

```
Check if User A can access File F:

  START
    │
    ├─ Query: user_file_mapping
    │  WHERE user_id='A' AND file_id='F'
    │
    │  ┌─────────────────┐
    │  │ Record Found?   │
    │  └────────┬────────┘
    │           │
    │       YES │     NO
    │           │      │
    │    Return │      │
    │    Perm   │      │
    │    (4/2/1)│      └─────────┐
    │           │                │
    │           ▼                │
    │         DONE               │
    │                            │
    │           ┌────────────────┘
    │           │
    │           ├─ Query: group_user_mapping
    │           │  WHERE user_id='A'
    │           │  → Get all group_ids
    │           │
    │           ├─ Query: group_file_mapping
    │           │  WHERE file_id='F'
    │           │  AND group_id IN (user's groups)
    │           │
    │           ┌─────────────────┐
    │           │ Records Found?  │
    │           └────────┬────────┘
    │                    │
    │                YES │  NO
    │                    │   │
    │           Return   │   │
    │           Perm     │   │
    │           (4/2/1)  │   │
    │                    │   │
    │                    ▼   ▼
    │                   DONE  DENIED (403)

Permission Bits (Octal):
- 4: Read permission
- 2: Write permission
- 1: Delete permission
- 0: No permission

Examples:
- 4 (read-only) = 0b100
- 6 (read+write) = 0b110
- 7 (all) = 0b111
- 5 (read+delete) = 0b101
```

---

## 6. ERROR HANDLING FLOW

```
Upload Fails
  │
  ├─ S3 Error
  │  └─ Retry with exponential backoff
  │     Attempt 1: wait 1s
  │     Attempt 2: wait 2s
  │     Attempt 3: wait 4s
  │     If all fail → DLQ + Alert
  │
  ├─ Database Error
  │  ├─ Orphaned file in S3
  │  ├─ Retry DB insert (max 3x)
  │  └─ If fails → Manual ticket
  │
  ├─ Permission Denied
  │  └─ Return 403 immediately
  │
  ├─ Quota Exceeded
  │  ├─ Return 400 Bad Request
  │  └─ Include available quota
  │
  └─ Network Timeout
     └─ Return 408 Request Timeout
        Client can retry

User Notification:
- Success: Email with file link
- Failure: Email with error reason
- Large file: SMS on completion
```

---

## 7. REDIS CACHE STRUCTURE

```
Cache Key Patterns:

1. User Session
   Key: session:{token}
   Value: {"user_id": "123", "email": "user@example.com"}
   TTL: 3600s (1 hour, matches JWT)
   
2. User File Access
   Key: user_files:{user_id}
   Value: ["file_id_1", "file_id_2", "file_id_3", ...]
   TTL: 300s (5 minutes)
   Invalidate: on file share, delete, permission change
   
3. File Permissions
   Key: file_perms:{file_id}:{user_id}
   Value: 4 (just the octal permission)
   TTL: 300s (5 minutes)
   Invalidate: on permission change
   
4. File Metadata
   Key: file_meta:{file_id}
   Value: {
     "file_id": "uuid",
     "file_name": "audio.mp3",
     "size": 52428800,
     "mime_type": "audio/mpeg",
     "uploaded_by": "user_123",
     "created_at": "2026-01-03T13:15:00Z"
   }
   TTL: 600s (10 minutes)
   Invalidate: on file update
   
5. Group Information
   Key: group:{group_id}
   Value: {
     "group_id": "uuid",
     "name": "Team Marketing",
     "created_by": "user_456",
     "member_count": 150
   }
   TTL: 1800s (30 minutes)
   Invalidate: on group update
   
6. Group Members
   Key: group_members:{group_id}
   Value: ["user_1", "user_2", "user_3", ...]
   TTL: 600s (10 minutes)
   Invalidate: on member add/remove

Cache Invalidation Strategy:
- Use Redis keyspace notifications
- Pub/Sub for invalidation events
- Or TTL-based (set & forget)
```

---

## 8. SCALING METRICS & THRESHOLDS

```
Auto-scaling Rules:

FastAPI Instances:
- If CPU > 70% for 2 min → Scale up
- If CPU < 30% for 5 min → Scale down
- Min: 3, Max: 20

RDS Replicas:
- If Primary read latency > 100ms → Add replica
- If Primary connections > 500 → Add replica
- Max: 3 read replicas

Lambda Workers:
- If SQS queue depth > 100 → Scale up
- If processing time > 5 min → Alert
- Concurrent: up to 1000

Redis:
- If memory usage > 80% → Add node
- If hit rate < 70% → Review TTL
- 3-node cluster for HA

S3:
- Automatic (AWS manages)
- Monitor: request rate, bandwidth
- Setup lifecycle policies

Monitoring Thresholds:

Critical (Page on-call):
- Error rate > 1%
- Latency p95 > 5s
- Uptime < 99.8%
- Queue stuck > 10 min

Warning (Email alert):
- Error rate > 0.5%
- Latency p95 > 2s
- Cache hit rate < 70%
- Disk space < 20% free

Info (Dashboard):
- Error rate > 0.1%
- Latency p95 > 1s
- Any anomaly
```

---

