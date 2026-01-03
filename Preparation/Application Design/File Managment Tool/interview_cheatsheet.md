# Interview Cheat Sheet: Large File Upload/Download System Design
## Quick Reference for Technical Interviews

**Author**: Senior Backend Engineer  
**Date**: January 3, 2026  
**Status**: Interview-Ready

---

## ⏱️ 45-Minute Interview Structure

```
0-2 min  → Greetings, problem clarification
2-7 min  → Ask clarifying questions (CRITICAL!)
7-15 min → Propose architecture + decision trees
15-25 min → Deep dive into chosen strategy (code skeleton)
25-35 min → Handle failures + edge cases
35-40 min → Discuss scalability + costs
40-45 min → Answer follow-up questions
```

---

## 🎯 Clarifying Questions (ALWAYS Ask First!)

When asked: **"Design a file upload/download system"**

Say this:
```
"Great! Before I design, let me clarify the requirements:

SCOPE:
1. What's the file size range?
   - Small (1-100MB)?
   - Large (100MB-5GB)?
   - Massive (>5GB)?
   
2. How many concurrent users?
   - Hundreds? Thousands? Millions?
   
3. Network reliability?
   - Datacenter? Mobile? Global?

CONSTRAINTS:
4. Storage: Where? (AWS S3? Local?)
5. Budget: Cost matters?
6. Compliance: Any regulations?

FEATURES:
7. Resume/resume on fail?
8. Progress tracking?
9. Speed critical?
10. Security: Audit logs?
11. Delete/revoke mid-transfer?
12. Parallel downloads?

Given I've got ~45 minutes, I'll assume:
- Files: 100MB-5GB
- Users: 100K concurrent
- Network: Mixed (some mobile)
- Use: S3, cost-aware
- Features: Resume + audit logs

Sound good?"
```

This shows you're thinking about tradeoffs, not just coding.

---

## 📊 The 5-Tier Answer (Interview Gold)

### Tier 1: Decision Tree (2 minutes)

```
"Here's how I'd choose a strategy:

┌─ If file < 100MB
│  └─ Single-request: simple, backend streams to S3
│
├─ If file 100MB-1GB, network GOOD
│  └─ Multipart (S3 native): backend orchestrates
│
├─ If file 100MB-1GB, network BAD
│  └─ Pre-signed multipart: client→S3 direct, resume
│
├─ If file 1GB-5GB
│  └─ Pre-signed multipart + resume logic
│
└─ If file > 5GB
   └─ Pre-signed multipart + bandwidth throttling
```

### Tier 2: Core Concept (3 minutes)

**For your assumed scenario** (100MB-5GB, 100K users):

```
"I'd use: S3 Multipart Upload with Pre-signed URLs

Why:
1. Avoids backend bottleneck (data doesn't flow through backend)
2. Supports resume (each part independently)
3. Cost-effective (no backend bandwidth)
4. Scales to millions of uploads

Flow:
1. Client → Backend: "Start upload"
2. Backend → Client: 
   - Auth + permission check
   - Return pre-signed URLs (one per part)
3. Client → S3: Upload parts directly (parallel!)
4. Client → Backend: "Done uploading"
5. Backend:
   - Verify on S3
   - Create DB record
   - Return file ID"
```

### Tier 3: Code Skeleton (5 minutes)

**Backend (Python FastAPI)**:

```python
@app.post("/api/uploads/initiate")
async def initiate(payload, user = Depends(get_user)):
    # 1. Validate: auth, quota, permissions
    validate_user(user)
    validate_quota(user, payload['file_size'])
    
    # 2. Initiate S3 multipart
    upload = s3.create_multipart_upload(
        Bucket='bucket',
        Key=f"files/{uuid4()}/{payload['name']}"
    )
    
    # 3. Generate pre-signed URLs for each part
    urls = []
    for part_num in range(1, num_parts + 1):
        url = s3.generate_presigned_url(
            'upload_part',
            Params={
                'Bucket': 'bucket',
                'Key': key,
                'UploadId': upload['UploadId'],
                'PartNumber': part_num
            },
            ExpiresIn=3600
        )
        urls.append({'part': part_num, 'url': url})
    
    # 4. Store in Redis (temporary)
    redis.hset(f"upload:{upload['UploadId']}", 
               mapping=upload_meta)
    
    return {"upload_id": upload['UploadId'], "urls": urls}

@app.post("/api/uploads/{upload_id}/complete")
async def complete(upload_id, payload):
    # 1. Get metadata from Redis
    meta = redis.hgetall(f"upload:{upload_id}")
    
    # 2. Complete multipart on S3
    s3.complete_multipart_upload(
        Bucket='bucket',
        Key=meta['key'],
        UploadId=upload_id,
        MultipartUpload={'Parts': payload['parts']}
    )
    
    # 3. Create DB record
    db.add(FileMaster(...))
    db.commit()
    
    # 4. Cleanup
    redis.delete(f"upload:{upload_id}")
    
    return {"file_id": file_id}
```

**Client (JavaScript)**:

```javascript
async function upload(file, groupId) {
  // 1. Initiate
  const init = await fetch('/api/uploads/initiate', {
    method: 'POST',
    body: JSON.stringify({
      name: file.name,
      size: file.size,
      group_id: groupId
    })
  }).then(r => r.json());
  
  // 2. Upload parts (parallel!)
  const parts = [];
  for (let part of init.urls) {
    const chunk = file.slice(
      part.part * CHUNK_SIZE,
      (part.part + 1) * CHUNK_SIZE
    );
    
    // Retry logic
    let retries = 0;
    while (retries < 3) {
      try {
        const resp = await fetch(part.url, {
          method: 'PUT',
          body: chunk
        });
        parts.push({
          PartNumber: part.part,
          ETag: resp.headers.get('etag')
        });
        break;
      } catch {
        retries++;
        await sleep(Math.pow(2, retries) * 1000);
      }
    }
  }
  
  // 3. Complete
  const result = await fetch(
    `/api/uploads/${init.upload_id}/complete`,
    {
      method: 'POST',
      body: JSON.stringify({ parts })
    }
  ).then(r => r.json());
  
  return result;
}
```

### Tier 4: Failure Handling (3 minutes)

```
Interviewer: "What if the network fails at part 5/10?"

You: "Great question! Here's the flow:

1. Client uploads parts 1-4 successfully
2. Network drops at part 5
3. User closes browser / reconnects

ON RESUME:
1. Client: "Which parts do you have?"
2. Backend/S3: "I have parts 1-4"
3. Client: "Upload parts 5-10" (retry from part 5!)
4. S3 multipart: Already has 1-4 cached
5. Final complete: Assembles all

Why this works:
- S3 multipart keeps uploaded parts for 7 days
- Each part is independent
- No re-upload of successful parts

Code:
if (lastPartUploaded < totalParts) {
  startFrom = lastPartUploaded + 1;
  // Upload remaining parts
}
```

### Tier 5: Scalability (2 minutes)

```
Interviewer: "How does this scale to 1M concurrent uploads?"

You: "Perfectly! Here's why:

LOAD DISTRIBUTION:
- Backend: Only handles metadata + signing
  - Typical request: 100ms (instant)
  - Backend can handle 10,000 concurrent /initiate calls
  
- S3: Handles all the data
  - Designed for millions of requests/sec
  - Auto-scales

- Client: Uploads to S3 directly
  - No backend bottleneck
  - Each upload independent

COST AT SCALE:
- S3 multipart API: $0.005 per 10,000 requests
- 1M files = 100 requests each = 100M requests
- Cost: $500 (acceptable!)
- Backend bandwidth: $0 (client→S3 direct!)

COMPARISON:
- If backend proxied: 100TB bandwidth = $900k!
- Our way: ~$500 (client→S3 direct)
```

---

## 🔴 Common Mistakes (Don't Make These!)

```
❌ Mistake 1: Proxying file data through backend at scale
   ✅ Solution: Use pre-signed URLs

❌ Mistake 2: No resume capability for large files
   ✅ Solution: Use multipart (each part retriable)

❌ Mistake 3: Storing files on instance disk
   ✅ Solution: Always use S3 (survives instance failure)

❌ Mistake 4: No audit logs
   ✅ Solution: Log every upload/download with user + timestamp

❌ Mistake 5: Orphaned files in S3
   ✅ Solution: Cleanup job + retention policy

❌ Mistake 6: No quota enforcement
   ✅ Solution: Check before generating pre-signed URL

❌ Mistake 7: Pre-signed URLs never expire
   ✅ Solution: 15-60 min expiry, user-scoped

❌ Mistake 8: No virus scanning
   ✅ Solution: Lambda function on S3 put event

❌ Mistake 9: Retry without backoff
   ✅ Solution: Exponential backoff (1s, 2s, 4s)

❌ Mistake 10: No monitoring of upload success rate
   ✅ Solution: CloudWatch metrics, alerts at >1% error
```

---

## 📈 Follow-Up Questions (Be Ready!)

**Q: "How do you handle very large files (>5GB)?"**

```
A: "Same architecture, but add:

1. Resumable checksums
   - Client: Calculate MD5 of each part
   - Backend: Verify on S3
   - If mismatch: Re-upload part
   
2. Progress persistence
   - Redis: {upload_id: {part_5: done, part_6: pending}}
   - Client polls: "Show me what's done"
   
3. Bandwidth throttling (optional)
   - Limit upload speed per user
   - Prevent abuse

4. Split into smaller chunks
   - Instead of 5MB: use 1MB
   - More parts = more granular retry"
```

**Q: "What about downloads?"**

```
A: "Much simpler! Use signed S3 URLs:

1. User: GET /download/file_id
2. Backend:
   - Check permission
   - Generate signed URL (1 hour expiry)
   - Return URL
3. User: Download directly from S3 (CloudFront edge)

Why:
- Zero backend load
- Fast (CloudFront cache)
- Cheap (no bandwidth through backend)

For resume:
- Browser supports HTTP Range natively
- S3 returns 206 Partial Content
- Browser resumes automatically"
```

**Q: "How do you prevent abuse (DDoS, quota)"**

```
A: "Multiple layers:

1. BEFORE generating pre-signed URL
   - Check user quota
   - Check rate limit
   - Check file type (whitelist)
   
2. S3 bucket policy
   - Restrict IP range
   - Restrict key prefix
   - Restrict principals
   
3. Pre-signed URL constraints
   - Time limit (1 hour)
   - IP restriction (optional)
   - Content-length limit
   
4. Monitoring
   - Alert if user uploads >1GB/day
   - Alert if error rate >1%
   - Block on suspicious patterns"
```

**Q: "What if backend goes down during upload?"**

```
A: "No problem! Here's why:

1. Backend down BEFORE signing: User retries, times out ✓
2. Backend down DURING signing: User already has URLs ✓
3. Backend down AFTER signing: User completes S3 upload ✓

RECOVERY:
- S3 has the data (complete multipart already done)
- User notifies backend via retry: "Complete my upload"
- Backend verifies on S3, creates DB record

The data is never lost because:
- Client already uploaded to S3 (not backend)
- S3 is durable (99.999999999% durability)
- Backend is just orchestration"
```

---

## 🎓 Perfect Opening (First 2 minutes)

```
"Thanks for this question. File upload is a classic system design problem 
because it touches multiple layers:

1. CLIENT: How to efficiently send data
2. NETWORK: How to handle failures
3. BACKEND: How to orchestrate without bottleneck
4. STORAGE: How to store durably and cost-effectively

My approach:
- Ask a few clarifying questions
- Propose a tiered strategy
- Show the code for the recommended approach
- Deep dive into failure scenarios
- Discuss scalability

Let me start with questions..."
```

---

## 🎯 Decision Matrix (Cheat Sheet)

**Print this on index card for interview:**

```
FILE SIZE     | STRATEGY           | WHY
--            | --                 | --
<50MB         | Single request     | Simple, fast enough
50-100MB      | Multipart proxy    | Control, reliability
100MB-1GB     | Presigned MP       | Speed, scalability
1GB-5GB       | Presigned MP+res   | Resume, large files
>5GB          | Direct stream      | Must bypass backend

NETWORK       | ADD               | WHY
--            | --                | --
Good (DC)     | Nothing extra     | Simple works
Poor (mobile) | Resume logic      | Handle drops
Very bad      | Checksum verify   | Data integrity

SCALE         | CHANGE            | WHY
--            | --                | --
<1K users     | Simple/streaming  | Overhead not worth it
1K-100K       | Multipart proxy   | Good balance
>100K         | Presigned URLs    | Must bypass backend
```

---

## 💬 Practice Answer (3 minutes)

**Scenario**: "Design file upload for Dropbox"

```
"Great! Let me break this down:

REQUIREMENTS (assuming):
- Files: 1 byte to 50GB
- Users: Millions globally
- Network: Mixed (WiFi, mobile, office)
- Features: Resume, progress, audit

MY STRATEGY - Tiered approach:

1. SMALL FILES (<100MB)
   - Single PUT to S3 with pre-signed URL
   - Fast, simple, cost-effective

2. MEDIUM FILES (100MB-1GB)
   - Multipart with pre-signed URLs per part
   - Client uploads parts in parallel
   - Each part independently retriable

3. LARGE FILES (>1GB)
   - Same as medium, but:
   - Add checksum verification
   - Add progress persistence (Redis)
   - Add bandwidth throttling

WHY PRE-SIGNED:
- Backend never touches file data
- No bandwidth cost through backend
- Scales to millions of concurrent uploads
- Simple architecture

HOW IT WORKS:
1. User clicks 'upload'
2. Client → Backend: 'Start upload' (auth, quota check)
3. Backend → Client: Pre-signed URLs for each part
4. Client → S3: Upload parts (parallel, with retry)
5. Client → Backend: 'Done' (verify and finalize)

FAILURE HANDLING:
- Part fails? Retry with backoff
- Network drops? Resume from part N
- Backend crash? Data already on S3

SCALING:
- At 1M concurrent: Backend 3 instances (light)
- S3 scales auto, CloudFront caches downloads
- Cost: ~$500/month S3 API, $0 backend bandwidth

MONITORING:
- Success rate >99%
- Error rate <0.1%
- Latency p95 <5s (from your perspective)

Does this match your thinking?"
```

---

## ⚡ Emergency Fallback (If stuck)

```
Interviewer asks something you don't know...

YOU SAY:
"That's a great point. In production, here's what I'd do:

1. Research: Check AWS docs / SO
2. Prototype: Write spike code
3. Benchmark: Test with realistic data
4. Monitor: See what breaks in practice
5. Iterate: Fix based on real metrics

For now, my assumption is: [your best guess]

But I'd definitely validate that with the team."

This shows: Intellectual honesty, good engineering practice.
```

---

## ✅ Interview Checklist

Before the interview, review:

- [ ] Can explain decision tree without notes
- [ ] Can sketch 5-tier answer in 15 minutes
- [ ] Understand pre-signed URLs (concept + code)
- [ ] Understand S3 multipart API
- [ ] Know 3 failure scenarios + solutions
- [ ] Can calculate cost at scale
- [ ] Understand HTTP Range requests
- [ ] Know the tradeoff: simplicity vs scalability

---

## 🎓 Key Concepts (Memorize These)

1. **Pre-signed URL**: Time-limited, scoped permission to S3 object
2. **Multipart Upload**: S3 API to upload large files in parts (auto-assemble)
3. **HTTP Range**: Request specific byte range (enable resume)
4. **Exponential Backoff**: 1s, 2s, 4s, 8s retry delays
5. **Chunking**: Split file into smaller pieces client-side
6. **Streaming**: Read file in chunks, don't load fully in memory
7. **Audit Log**: Record every upload/download for compliance
8. **Quota**: Limit per-user/per-group storage

---

## 📞 Final Tips

```
DO:
✅ Ask clarifying questions FIRST
✅ Propose multiple approaches
✅ Choose based on constraints
✅ Explain tradeoffs
✅ Write clean code (even if pseudo)
✅ Handle failures
✅ Discuss monitoring
✅ Show production mindset

DON'T:
❌ Jump to code immediately
❌ Assume requirements
❌ Overcomplicate
❌ Ignore edge cases
❌ Forget about costs
❌ Ignore scalability
❌ Make up technical details

TONE:
- Confident but not arrogant
- Think out loud (let them see your process)
- Ask for feedback
- Show you care about tradeoffs
```

---

**Good luck! 🚀**

Remember: Interviewers want to see how you THINK, not just what you know.

