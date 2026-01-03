# Quick Reference: Design Decisions Summary

## 📊 Architecture at a Glance

```
Users (100K) → ALB → FastAPI Instances → RDS PostgreSQL
                      ↓
                   Redis Cache
                      ↓
                   S3 Storage (TB)
                      ↓
                   SQS Queue → Lambda Workers
```

---

## 🗄️ Database Schema (Final)

```
Core Tables:
├── user_master (users)
├── group_master (groups)
├── group_user_mapping (group membership + perms)
├── group_file_mapping (group → file access)
├── user_file_mapping (individual file shares)
├── file_master (file metadata) ⭐ YOU MISSED THIS
├── file_audit_log (activity tracking)
└── file_upload_tracker (async upload tracking)

Key Features:
- Octal permissions (4=read, 2=write, 1=delete)
- Composite indexes on all mapping tables
- Soft delete support (for recovery)
- Audit trail for compliance
```

---

## 📤 Upload Flow (Decision Tree)

```
Upload Request
    ↓
Validate: auth, quota, file type
    ↓
Decision: File Size?
    ├─ < 100MB: SYNC (direct S3 → DB → response)
    └─ >= 100MB: ASYNC
         ├─ Generate upload_id
         ├─ Queue task (SQS)
         ├─ Return 202 (in progress)
         └─ Lambda processes
              ├─ S3 multipart if > 500MB
              ├─ Update file_master
              ├─ Create mappings
              ├─ Update quotas
              └─ Notify user

Error Handling:
- S3 fails → Retry 3x with backoff
- DB fails → Ticket for manual recovery
- Queue stuck → DLQ + alert admin
```

---

## 📥 Download Flow

```
Download Request
    ↓
Permission check (cached)
    ↓
IF Audio/Video File:
    ├─ Support HTTP Range (206 Partial)
    ├─ Enable seeking
    └─ Stream from S3 with 1-hour cache
ELSE:
    └─ Direct download

Log: (async, non-blocking)
- User ID, file ID, timestamp
- For audit/analytics
```

---

## 💾 Caching Strategy (Redis)

```
High Priority (5-10 min TTL):
- user_files:{user_id} → list of accessible files
- file_perms:{file_id}:{user_id} → permission bits
- session:{token} → user session

Medium Priority (10-30 min TTL):
- file_meta:{file_id} → file metadata
- group:{group_id} → group details
- group_members:{group_id} → members list

Cache Hit Target: > 80%
```

---

## 🚀 Scaling Strategy

```
API Layer:
- Auto-scale FastAPI instances (3-10+)
- Load balance with ALB
- Connection pooling to DB

Database Layer:
- Primary RDS (writes)
- 2 read replicas (reads)
- Connection pooling (PgBouncer)
- Partitioning on audit logs

Cache Layer:
- Redis cluster (3 nodes)
- Keyspace notifications for invalidation

Queue Layer:
- SQS (managed) or RabbitMQ
- Auto-scale Lambda/workers
- DLQ for failures

Storage Layer:
- S3 with versioning
- CloudFront CDN
- Lifecycle policies
- Encryption at rest
```

---

## ⚠️ Critical Issues You Missed

### 1. File Metadata Table (file_master)
**Problem**: No schema for storing file name, size, path
**Impact**: Can't list files by metadata
**Fix**: Add file_master with: id, name, size, s3_path, type, uploaded_by, created_at

### 2. Download/Streaming
**Problem**: Never designed GET /files/{file_id}/download
**Impact**: Can't handle large files efficiently, no resume support
**Fix**: Implement streaming with HTTP Range support for audio/video

### 3. Failure Atomicity
**Problem**: S3 upload succeeds, DB fails → orphaned file
**Impact**: Storage waste, user confusion, data inconsistency
**Fix**: Use file_upload_tracker table, implement retry logic, cleanup job

### 4. Caching Strategy
**Problem**: No Redis design
**Impact**: Database will be bottleneck at scale (100K users)
**Fix**: Cache permissions, file metadata, group info (5-30 min TTL)

### 5. Audit Logging
**Problem**: No tracking of file access/activity
**Impact**: Can't answer "who downloaded this file?"
**Fix**: Add file_audit_log table with user, action, timestamp

---

## 🎯 What Happens at Scale (100K Users, 1M Files)

| Metric | Without Optimization | With Optimization |
|--------|---------------------|-------------------|
| DB Queries/sec | 50K+ (bottleneck!) | 5K (cached) ✓ |
| Upload latency | 5-10s | 200-500ms ✓ |
| Download latency | 2-3s | 500ms (cached) ✓ |
| Memory (Redis) | N/A | 50-100GB (cluster) |
| Cost/month | $2K-3K | $5K-8K (but bearable) |

---

## 🔒 Security Checklist

```
✅ JWT-based auth (1hr expiry)
✅ Permission checking on every request
✅ Audit logging (who did what)
✅ Signed URLs for S3 (time-limited)
✅ File type validation (whitelist MIME)
✅ Rate limiting (prevent abuse)
✅ Encryption in transit (HTTPS)
✅ Encryption at rest (S3-side)
✅ CORS configuration
```

---

## 📊 Key Metrics to Monitor

```
Success Metrics:
- Upload success rate (target: >99.9%)
- Download success rate (target: >99.9%)
- P95 latency for list (target: <200ms)
- P95 latency for download (target: <1s)

Operational Metrics:
- Cache hit rate (target: >80%)
- DB query latency p95 (target: <100ms)
- Queue depth (target: <5min processing)
- Error rate (target: <0.1%)

Business Metrics:
- Active users
- Files uploaded/day
- Total storage used
- Download/upload ratio
```

---

## 🛠️ Implementation Priority

### Week 1 (MVP)
1. Add file_master table
2. Implement Redis for permissions
3. Upload flow (sync + async)
4. Basic permission checking

### Weeks 2-4
5. Download API with streaming
6. Audit logging
7. SQS queue integration
8. Error handling + DLQ

### Months 2-3
9. Monitoring (Datadog/ELK)
10. Read replicas
11. CDN integration (CloudFront)
12. Storage quotas

### Months 4+
13. Multi-region failover
14. File versioning
15. Deduplication
16. Full-text search

---

## 🎓 Interview Tips

When asked similar questions:
1. **Start with requirements clarification** (scale, traffic, features)
2. **Draw the full architecture** (don't just code, think holistically)
3. **Think about failure modes** (S3 down? DB down? network split?)
4. **Mention trade-offs** (why sync vs async? why this DB?)
5. **Add monitoring from the start** (not an afterthought)
6. **Handle edge cases** (concurrent uploads, permission changes)
7. **Show scaling path** (single server → multi-server → cluster)

---

## 📚 Additional Resources

Books:
- "Designing Data-Intensive Applications" by Kleppmann
- "System Design Interview" by Xu
- AWS Well-Architected Framework

Practice:
- LeetCode System Design
- Educative.io System Design Course
- Real system architectures (GitHub, Medium)

---

