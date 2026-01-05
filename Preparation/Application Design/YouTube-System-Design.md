# YouTube System Design - Complete Production Architecture Guide

**A comprehensive deep-dive into designing a large-scale video streaming platform**

---

## Table of Contents
1. [Requirements & Analysis](#1-requirements--analysis)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Database Design](#3-database-design)
4. [Scaling Strategy](#4-scaling-strategy-handling-high-scale)
5. [API Level Design](#5-api-level-design)
6. [Storage Management](#6-storage-management)
7. [Core Services Deep-Dive](#7-core-services-deep-dive)
8. [Decision Trade-offs](#8-decision-trade-offs)

---

## 1. Requirements & Analysis

### 1.1 Functional Requirements

**Core User Features:**
- User registration, authentication, and profile management
- Video upload, processing, and publishing
- Video streaming with adaptive quality
- Comments, likes, subscriptions, and engagement metrics
- Search and discovery (home feed, trending, recommendations)
- Channel management and analytics for creators
- Playlists, watch history, and watch-later
- Live streaming support
- Content moderation and reporting

**Creator Features:**
- Video analytics (views, watch time, engagement, demographics)
- Monetization and revenue tracking
- Community posts and messaging
- Video insights and performance metrics

### 1.2 Non-Functional Requirements

| Requirement | Target | Rationale |
|---|---|---|
| **Scale** | 2.5B monthly active users, 500M+ daily active | Handle peak traffic (140K req/sec globally) |
| **Latency** | <500ms p99 for video start, <200ms for metadata | Ensure smooth user experience |
| **Availability** | 99.99% uptime (four nines) | Critical service, revenue-dependent |
| **Throughput** | 1000+ video uploads/minute, 1M+ concurrent streams | Peak upload and streaming load |
| **Storage** | Petabytes of video data with redundancy | Archive and serve millions of videos |
| **Bandwidth** | Petabits/second egress | Serve billions of video streams globally |
| **Durability** | 11 nines (99.999999999%) data durability | No video loss, irreplaceable content |
| **Consistency** | Eventual consistency for most features | High availability preferred over strong consistency |

### 1.3 Key Metrics & Capacity Planning

```
Daily Active Users: 500M
Peak QPS: 150K-200K requests/second
Video Upload Rate: 500+ hours of content per minute
Total Storage: 1000+ Petabytes (accounting for redundancy)
Bandwidth: 10+ Petabits/second during peak hours
Video Processing Queue Depth: 100K+ videos awaiting processing
```

---

## 2. High-Level Architecture

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  (Web Browser, Mobile Apps, Smart TVs, Gaming Consoles)             │
└────────────────────────────────────────────────────────────────────
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼──────┐  ┌───▼────────┐  ┌▼──────────────┐
            │  Edge/CDN    │  │API Gateway │  │Message Queue  │
            │  (Akamai,    │  │(Nginx/AWS  │  │(Kafka/RabbitMQ)
            │   Cloudflare)│  │ API GW)    │  │               │
            └───────┬──────┘  └──┬─────────┘  └┬──────────────┘
                    │            │             │
        ┌───────────┼────────────┼─────────────┼────────────┐
        │           │            │             │            │
   ┌────▼────┐  ┌──▼──┐  ┌────▼──────┐  ┌───▼───┐   ┌──▼──────┐
   │   CDN   │  │Load │  │Microservices Layer    │   │ Async   │
   │  Cache  │  │Bal  │  │  (Kubernetes)        │   │ Workers │
   │         │  │     │  │                      │   │         │
   └────┬────┘  └──┬──┘  └──────┬───────────────┘   └──┬──────┘
        │          │             │                      │
        │     ┌────┴─────────────┴──────────────────────┘
        │     │
   ┌────▼─────▼──────────────────────────────────────────────────┐
   │         MICROSERVICES LAYER                                  │
   │                                                              │
   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
   │  │Video Upload  │  │Video Stream  │  │Search &     │      │
   │  │& Processing  │  │& Playback    │  │Recommend.   │      │
   │  └──────────────┘  └──────────────┘  └──────────────┘      │
   │                                                              │
   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
   │  │User Service  │  │Comments &    │  │Analytics &  │      │
   │  │& Auth        │  │Engagement    │  │Notifications│      │
   │  └──────────────┘  └──────────────┘  └──────────────┘      │
   │                                                              │
   └─────────┬──────────────────────────────────────────────────┘
             │
   ┌─────────┴────────────────────────────────────────────────────┐
   │                    CACHING LAYER                              │
   │                                                               │
   │   ┌──────────────┐    ┌──────────────┐   ┌──────────────┐  │
   │   │Redis Cluster │    │Memcached     │   │Local Cache   │  │
   │   │(Hot Data)    │    │(Metadata)    │   │(Edge/CDN)    │  │
   │   └──────────────┘    └──────────────┘   └──────────────┘  │
   │                                                               │
   └─────────┬────────────────────────────────────────────────────┘
             │
   ┌─────────┴────────────────────────────────────────────────────┐
   │                   DATABASE LAYER                              │
   │                                                               │
   │   ┌──────────────────────┐    ┌──────────────────────────┐  │
   │   │  PostgreSQL          │    │  MongoDB                 │  │
   │   │  (Structured Data)   │    │  (Unstructured Data)     │  │
   │   │                      │    │                          │  │
   │   │• Users/Channels      │    │• Comments/Engagement     │  │
   │   │• Video Metadata      │    │• User interactions       │  │
   │   │• Subscriptions       │    │• Analytics Events        │  │
   │   │• Payments/Billing    │    │• Recommendations         │  │
   │   └──────────────────────┘    └──────────────────────────┘  │
   │                                                               │
   │   ┌──────────────────────┐    ┌──────────────────────────┐  │
   │   │  Elasticsearch       │    │  Google Cloud            │  │
   │   │  (Search Index)      │    │  Bigtable/HBase          │  │
   │   │                      │    │  (Time-series)           │  │
   │   │• Video search index  │    │• Real-time analytics     │  │
   │   │• Autocomplete        │    │• User activity stream    │  │
   │   │• Full-text search    │    │• Metrics & signals       │  │
   │   └──────────────────────┘    └──────────────────────────┘  │
   │                                                               │
   └─────────┬────────────────────────────────────────────────────┘
             │
   ┌─────────┴────────────────────────────────────────────────────┐
   │                   STORAGE LAYER                               │
   │                                                               │
   │   ┌──────────────────────┐    ┌──────────────────────────┐  │
   │   │  AWS S3 / GCS        │    │  Blob Storage            │  │
   │   │  (Video Files)       │    │  (Thumbnails/Assets)     │  │
   │   │  (1000+ PB)          │    │  (Multi-region)          │  │
   │   │  - Replicated        │    │  - Edge cached           │  │
   │   │  - Immutable         │    │  - Frequently accessed   │  │
   │   │  - Versioned         │    │  - Quick delivery        │  │
   │   └──────────────────────┘    └──────────────────────────┘  │
   │                                                               │
   └───────────────────────────────────────────────────────────────┘

```

### 2.2 Data Flow Overview

**Video Streaming Flow:**
```
User Request 
    ↓
API Gateway (Route to nearest edge)
    ↓
CDN Edge Server (Check cache)
    ↓
Cache Hit? → Serve from CDN Edge (99% latency improvement)
    │
    └─→ Cache Miss? 
        ↓
        Origin Server (Query metadata from DB)
        ↓
        Fetch video chunk from blob storage
        ↓
        Stream to user + cache at edge
```

**Video Upload & Processing Flow:**
```
Upload Request
    ↓
Upload Service (Validate, auth, quota check)
    ↓
Store to temporary staging area
    ↓
Enqueue to processing queue (Kafka)
    ↓
Video Processing Workers (Transcode to multiple formats)
    ↓
Store processed videos in blob storage
    ↓
Update metadata in database
    ↓
Cache thumbnail and metadata
    ↓
Publish notification to subscribers
    ↓
Generate analytics events
```

---

## 3. Database Design

### 3.1 Database Selection Rationale

| Database | Purpose | Why Chosen |
|---|---|---|
| **PostgreSQL** | Structured, transactional data | ACID compliance, complex queries, data integrity |
| **MongoDB** | Unstructured, semi-structured data | Flexibility, horizontal scaling, document storage |
| **Elasticsearch** | Full-text search & indexing | Fast search, aggregations, autocomplete |
| **Bigtable/HBase** | Time-series analytics data | Columnar format, millions of events/sec, cheap storage |
| **Redis** | Hot metadata caching | Sub-millisecond latency, in-memory operations |

### 3.2 PostgreSQL Schema (Structured Data)

```sql
-- USERS TABLE
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    channel_id BIGINT REFERENCES channels(channel_id),
    profile_image_url VARCHAR(2048),
    bio TEXT,
    country VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,  -- Soft delete for compliance
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- CHANNELS TABLE
CREATE TABLE channels (
    channel_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(user_id),
    channel_name VARCHAR(255) UNIQUE NOT NULL,
    channel_description TEXT,
    banner_url VARCHAR(2048),
    subscriber_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_monetized BOOLEAN DEFAULT FALSE,
    total_uploads BIGINT DEFAULT 0,
    INDEX idx_subscriber_count (subscriber_count),
    INDEX idx_view_count (view_count)
);

-- VIDEOS TABLE (Sharded by video_id)
CREATE TABLE videos (
    video_id BIGSERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL REFERENCES channels(channel_id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    duration_seconds INT NOT NULL,
    thumbnail_url VARCHAR(2048),
    status ENUM('uploading', 'processing', 'published', 'unlisted', 'private') DEFAULT 'uploading',
    visibility ENUM('public', 'unlisted', 'private') DEFAULT 'public',
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Video processing metadata
    storage_path VARCHAR(2048),  -- S3/GCS path
    original_file_size BIGINT,
    hls_playlist_url VARCHAR(2048),
    dash_manifest_url VARCHAR(2048),
    
    -- Monetization
    is_monetized BOOLEAN DEFAULT TRUE,
    content_type VARCHAR(50),  -- 'entertainment', 'education', 'news', etc
    
    -- Indexing for common queries
    INDEX idx_channel_id (channel_id),
    INDEX idx_published_at (published_at DESC),
    INDEX idx_view_count (view_count DESC),
    INDEX idx_status (status),
    INDEX idx_visibility (visibility),
    CONSTRAINT chk_visibility CHECK (visibility IN ('public', 'unlisted', 'private'))
);

-- VIDEO_VARIANTS TABLE (Different resolutions/bitrates)
CREATE TABLE video_variants (
    variant_id BIGSERIAL PRIMARY KEY,
    video_id BIGINT NOT NULL REFERENCES videos(video_id),
    resolution VARCHAR(20),  -- '1080p', '720p', '480p', '360p', '240p'
    bitrate_kbps INT,  -- 2500, 1500, 800, 400, 200
    codec VARCHAR(50),  -- 'h264', 'vp9', 'av1'
    file_size_bytes BIGINT,
    storage_url VARCHAR(2048),
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_video_id (video_id),
    INDEX idx_resolution (resolution)
);

-- SUBSCRIPTIONS TABLE (Many-to-Many)
CREATE TABLE subscriptions (
    subscription_id BIGSERIAL PRIMARY KEY,
    subscriber_user_id BIGINT NOT NULL REFERENCES users(user_id),
    channel_id BIGINT NOT NULL REFERENCES channels(channel_id),
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_notified BOOLEAN DEFAULT TRUE,
    UNIQUE(subscriber_user_id, channel_id),
    INDEX idx_subscriber_user_id (subscriber_user_id),
    INDEX idx_channel_id (channel_id),
    INDEX idx_subscribed_at (subscribed_at)
);

-- WATCH_HISTORY TABLE (Partitioned by date for time-series data)
CREATE TABLE watch_history (
    history_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    video_id BIGINT NOT NULL REFERENCES videos(video_id),
    watch_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watch_duration_seconds INT,  -- How much they watched
    device_type VARCHAR(50),  -- 'desktop', 'mobile', 'tv'
    country VARCHAR(100),
    
    -- Partitioned by month for performance
    INDEX idx_user_id_timestamp (user_id, watch_timestamp DESC),
    INDEX idx_video_id_timestamp (video_id, watch_timestamp DESC)
) PARTITION BY RANGE (YEAR(watch_timestamp), MONTH(watch_timestamp));

-- WATCH_LATER TABLE
CREATE TABLE watch_later (
    watch_later_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    video_id BIGINT NOT NULL REFERENCES videos(video_id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position_index INT DEFAULT 0,  -- For ordering
    UNIQUE(user_id, video_id),
    INDEX idx_user_id (user_id),
    INDEX idx_video_id (video_id)
);

-- PLAYLISTS TABLE
CREATE TABLE playlists (
    playlist_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- PLAYLIST_VIDEOS TABLE
CREATE TABLE playlist_videos (
    playlist_video_id BIGSERIAL PRIMARY KEY,
    playlist_id BIGINT NOT NULL REFERENCES playlists(playlist_id),
    video_id BIGINT NOT NULL REFERENCES videos(video_id),
    position INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(playlist_id, video_id),
    INDEX idx_playlist_id (playlist_id),
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- LIKES TABLE
CREATE TABLE likes (
    like_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    video_id BIGINT NOT NULL REFERENCES videos(video_id),
    like_type ENUM('like', 'dislike') DEFAULT 'like',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, video_id),  -- One like/dislike per user per video
    INDEX idx_user_id_video_id (user_id, video_id),
    INDEX idx_video_id (video_id)
);

-- SUBSCRIPTIONS DENORMALIZED COUNT (For fast reads)
CREATE TABLE channel_stats (
    channel_id BIGINT PRIMARY KEY REFERENCES channels(channel_id),
    subscriber_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    video_count BIGINT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_updated_at (updated_at)
);
```

### 3.3 MongoDB Schema (Unstructured Data)

```javascript
// COMMENTS COLLECTION (Document-based, flexible schema)
db.createCollection("comments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["video_id", "user_id", "text", "created_at"],
      properties: {
        _id: { bsonType: "objectId" },
        video_id: { bsonType: "long" },
        channel_id: { bsonType: "long" },
        user_id: { bsonType: "long" },
        text: { bsonType: "string", maxLength: 10000 },
        parent_comment_id: { bsonType: ["objectId", "null"] },  // For replies
        likes_count: { bsonType: "int", minimum: 0 },
        replies_count: { bsonType: "int", minimum: 0 },
        is_pinned: { bsonType: "bool" },
        is_deleted: { bsonType: "bool" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        user_info: {
          bsonType: "object",
          properties: {
            username: { bsonType: "string" },
            profile_image_url: { bsonType: "string" },
            is_channel_owner: { bsonType: "bool" }
          }
        }
      }
    }
  }
});

db.comments.createIndex({ video_id: 1, created_at: -1 });
db.comments.createIndex({ user_id: 1, created_at: -1 });
db.comments.createIndex({ parent_comment_id: 1 });
db.comments.createIndex({ video_id: 1, likes_count: -1 });

// USER_ENGAGEMENT COLLECTION
db.createCollection("user_engagement", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "video_id", "timestamp"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "long" },
        video_id: { bsonType: "long" },
        timestamp: { bsonType: "date" },
        events: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              event_type: { 
                enum: ["click", "watch", "pause", "seek", "like", "comment", "share"]
              },
              event_time: { bsonType: "date" },
              watch_position_seconds: { bsonType: "int" },
              device_type: { bsonType: "string" }
            }
          }
        },
        last_watch_timestamp: { bsonType: "date" },
        total_watch_time: { bsonType: "int" },
        completion_rate: { bsonType: "double" }  // 0-1 decimal
      }
    }
  }
});

db.user_engagement.createIndex({ user_id: 1, timestamp: -1 });
db.user_engagement.createIndex({ video_id: 1, timestamp: -1 });
db.user_engagement.createIndex({ "events.event_type": 1 });

// RECOMMENDATIONS COLLECTION (Pre-computed recommendations cached)
db.createCollection("recommendations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "video_id", "score"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "long" },
        video_id: { bsonType: "long" },
        score: { bsonType: "double" },  // ML recommendation score
        reason: { bsonType: "string" },  // Why recommended
        algorithms: {
          bsonType: "array",
          items: { bsonType: "string" }  // Which algos contributed
        },
        created_at: { bsonType: "date" },
        expires_at: { bsonType: "date" }  // TTL index
      }
    }
  }
});

db.recommendations.createIndex({ user_id: 1, score: -1 });
db.recommendations.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });

// ANALYTICS_EVENTS COLLECTION (High-volume event stream)
db.createCollection("analytics_events");

db.analytics_events.createIndex({ user_id: 1, timestamp: -1 });
db.analytics_events.createIndex({ video_id: 1, timestamp: -1 });
db.analytics_events.createIndex({ event_type: 1, timestamp: -1 });
db.analytics_events.createIndex({ timestamp: -1 });

// TTL index to auto-delete old events after 90 days
db.analytics_events.createIndex({ created_at: 1 }, { expireAfterSeconds: 7776000 });
```

### 3.4 Elasticsearch Index Mapping (Search)

```json
{
  "settings": {
    "number_of_shards": 50,
    "number_of_replicas": 2,
    "analysis": {
      "analyzer": {
        "video_analyzer": {
          "type": "standard",
          "stopwords": "_english_"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "video_id": { "type": "keyword" },
      "channel_id": { "type": "keyword" },
      "title": {
        "type": "text",
        "analyzer": "video_analyzer",
        "fields": {
          "keyword": { "type": "keyword" },
          "suggest": { "type": "completion" }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "video_analyzer"
      },
      "tags": {
        "type": "keyword"
      },
      "channel_name": {
        "type": "text",
        "analyzer": "video_analyzer"
      },
      "view_count": { "type": "long" },
      "like_count": { "type": "long" },
      "comment_count": { "type": "long" },
      "duration_seconds": { "type": "integer" },
      "published_at": { "type": "date" },
      "popularity_score": {
        "type": "rank_feature",
        "positive_score_impact": true
      },
      "engagement_rate": { "type": "scaled_float" },
      "language": { "type": "keyword" },
      "content_type": { "type": "keyword" },
      "visibility": { "type": "keyword" },
      "is_monetized": { "type": "boolean" }
    }
  }
}
```

### 3.5 Data Partitioning & Sharding Strategy

**Video Data Sharding:**
```
Shard Key: video_id % 256 (0-255 shards)

Benefits:
- Distributes write load evenly
- Enables parallel processing
- Prevents hot shards (uniform distribution)

Shard Distribution:
├── Shard 0   → video_id % 256 = 0
├── Shard 1   → video_id % 256 = 1
├── ...
└── Shard 255 → video_id % 256 = 255

Each shard: ~4 million videos (1B total / 256)
```

**Watch History Partitioning (Time-based):**
```
Partition by: YEAR(timestamp), MONTH(timestamp)

Benefits:
- Improves query performance (year-month specific queries)
- Easier data retention policies
- Can archive old months to cold storage

Example:
├── watch_history_2024_01
├── watch_history_2024_02
├── ...
├── watch_history_2025_01
└── watch_history_2025_02 (current)

Retention policy: Keep 2 years, archive to S3, delete after 7 years
```

### 3.6 Replication & High Availability

**PostgreSQL Replication:**
```
Primary (Write) ←→ Replica 1 (Read)
                ├→ Replica 2 (Read)
                ├→ Replica 3 (Read - Analytics queries)
                └→ Replica 4 (Backup/Standby)

Replication lag: <100ms
Failover time: <30 seconds (automated)
Recovery Point Objective (RPO): <1 second
```

**MongoDB Replica Sets:**
```
Primary (Write) → Secondary 1 (Read)
               → Secondary 2 (Read)
               → Arbiter (election voting only)

Write concern: Majority (3 nodes)
Read preference: Secondary (for analytics)
Oplog window: 48 hours (allows catching up after failures)
```

---

## 4. Scaling Strategy (Handling High Scale)

### 4.1 Horizontal Scaling Architecture

**Problem:** Single database/server cannot handle billions of requests

**Solution: Database Sharding (Horizontal Partitioning)**

```
┌──────────────────────────────────────────────────────┐
│              API Gateway/Router                       │
│          (Determines shard from request)              │
└────────────────────────┬─────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼────┐      ┌───▼────┐      ┌───▼────┐
    │Shard 0  │      │Shard 1  │      │Shard 2  │
    │(0-255)  │      │(256-511)│      │(512+)   │
    │         │      │         │      │         │
    │ - DB    │      │ - DB    │      │ - DB    │
    │ - Cache │      │ - Cache │      │ - Cache │
    │ - Index │      │ - Index │      │ - Index │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                │                │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │Replica1 │      │Replica1 │      │Replica1 │
    │Replica2 │      │Replica2 │      │Replica2 │
    └─────────┘      └─────────┘      └─────────┘
```

**Sharding Keys by Table:**
```
videos:           video_id % num_shards
subscriptions:    channel_id % num_shards
watch_history:    user_id % num_shards + time partition
playlists:        user_id % num_shards
likes:            user_id % num_shards
comments:         video_id % num_shards (secondary: comment_id for uniqueness)
```

**Shard Rebalancing (Adding new shards):**
```
Current: 256 shards
New: 512 shards

Process:
1. Create 256 new shards in parallel
2. Read from old shard, re-hash to new shard: 
   - video_id % 256 → video_id % 512
3. Dual-write to old & new during migration (2 weeks)
4. Verify data consistency with sampling
5. Switch reads to new shards
6. Clean up old shards after 30-day buffer
```

### 4.2 Caching Strategy (Multi-Layer)

**Layer 1: CDN Edge Cache (Closest to User)**
```
What's cached: Video chunks, thumbnails, manifests
TTL: 30 days (for popular videos)
Hit rate target: 95%+
Storage: 1000+ edge locations globally

Example: User in Mumbai → Served from Akamai Mumbai edge
(3ms latency vs 50ms from origin)
```

**Layer 2: Redis Cluster (Hot Data)**
```
├─ Video metadata cache (title, description, stats)
│  ├─ Key: "video:{video_id}" 
│  ├─ TTL: 1 hour (auto-refresh on write)
│  └─ Size: ~2KB per video → 2TB for 1B videos
│
├─ User session cache
│  ├─ Key: "session:{session_id}"
│  ├─ TTL: 30 days (sliding window)
│  └─ Size: ~1KB per session → 500GB for 500M active users
│
├─ Recommendation cache (pre-computed)
│  ├─ Key: "recommendations:{user_id}"
│  ├─ TTL: 24 hours
│  └─ Size: 100 recommendations × 8 bytes = 800B → 400GB
│
└─ Leaderboards (trending, top creators)
   ├─ Key: "trending:{region}:{category}"
   ├─ TTL: 6 hours
   └─ Size: 1000 videos × 8 bytes = 8KB per region

Redis Cluster:
- 300 nodes (sharded by key hash)
- 300GB total memory (1TB with replication)
- 1M queries/sec throughput
```

**Layer 3: Memcached (Query Results)**
```
What's cached: Frequently run query results
TTL: 5-30 minutes
Hit rate: 80%+
Size: 10TB cluster

Cache invalidation:
- On write: immediately invalidate
- On time: TTL expiry
- On load: lazy loading (populate on miss)
```

**Layer 4: Database Query Cache (PostgreSQL)**
```
Internal caching of frequent queries
Automatic by PostgreSQL query planner
No explicit configuration needed
```

**Cache Invalidation Strategy:**

```javascript
// Example: User likes a video
function likeVideo(userId, videoId) {
  // 1. Write to database
  likeDb.insert({ user_id: userId, video_id: videoId });
  
  // 2. Invalidate affected caches
  cache.delete(`video:${videoId}`);  // Refresh stats
  cache.delete(`user:${userId}:likes`);  // User's like list
  cache.delete(`trending:${category}`);  // Trending cache
  
  // 3. Increment counter atomically
  videoMetricDb.increment(`likes_count`, videoId);
  
  // 4. Async: publish to analytics queue
  queue.publish('like_event', { userId, videoId, timestamp });
}
```

### 4.3 Load Balancing Strategy

**Global Load Balancing (Anycast):**
```
User traffic → Nearest geographic region

┌─ US-East (Virginia)
│  ├─ Load Balancer (Nginx)
│  ├─ API Gateway (x20 instances)
│  └─ Regional cache (Redis)
│
├─ Europe (Frankfurt)
│  ├─ Load Balancer (Nginx)
│  ├─ API Gateway (x15 instances)
│  └─ Regional cache (Redis)
│
├─ Asia-Pacific (Singapore)
│  ├─ Load Balancer (Nginx)
│  ├─ API Gateway (x25 instances)
│  └─ Regional cache (Redis)
│
└─ Australia (Sydney)
   ├─ Load Balancer (Nginx)
   ├─ API Gateway (x10 instances)
   └─ Regional cache (Redis)

Algorithm: Least connections + Health checks
Failover: If region fails, traffic goes to next nearest
```

**Service-Level Load Balancing:**
```
Microservices within each region:

Video Stream Service:
├─ Instance 1 (capacity: 5000 users)
├─ Instance 2 (capacity: 5000 users)
├─ Instance 3 (capacity: 5000 users)
└─ Instance 4 (capacity: 5000 users) [Auto-scale up at 80% capacity]

Load Balancer (Algorithm: Round-robin + weighted by health)
├─ Health check: /health endpoint (every 5 seconds)
├─ Timeout: 30 seconds for video chunk delivery
└─ Failover: Immediately route to healthy instances
```

### 4.4 Auto-Scaling Strategy

```yaml
Video Stream Service:
  min_instances: 100
  max_instances: 500
  target_cpu_utilization: 70%
  target_memory_utilization: 75%
  scale_up_threshold: 80% for 2 minutes
  scale_down_threshold: 30% for 5 minutes
  cooldown_period: 1 minute

Video Upload Service:
  min_instances: 20
  max_instances: 100
  target_queue_length: 1000 (per instance)
  scale_up: Add instance per 1000 items in queue
  scale_down: Remove if queue < 500 items

Database:
  Read replicas: Auto-scale 1-10 based on query latency
  Storage: Auto-grow (no limit, just cost tracking)
```

### 4.5 Queue & Async Processing (Handling Spikes)

**Kafka Topic Architecture:**
```
Topic: video_uploads (300 partitions)
├─ Partition 0 → Worker 1
├─ Partition 1 → Worker 2
├─ ...
└─ Partition 299 → Worker 300

Each partition:
  - Retention: 7 days
  - Replication factor: 3
  - In-sync replicas: 2
  - Messages/sec: 1000+

Topic: engagement_events (500 partitions)
├─ Events: likes, comments, shares, views
├─ High throughput: 500K events/sec
├─ Retention: 30 days
└─ Consumer groups: analytics, recommendations, real-time dashboards

Topic: notifications (50 partitions)
├─ Fanout: 1 event → N subscribers' notifications
├─ Delivery: At-least-once
└─ TTL: Delivered within 5 seconds of event
```

**Worker Pool for Video Processing:**

```
┌──────────────────────────────────────────┐
│   Video Upload Queue (Kafka)              │
│   1000 videos waiting to process         │
└────────────────┬─────────────────────────┘
                 │
        ┌────────┼────────┐
        │        │        │
  ┌─────▼──┐┌────▼──┐┌───▼────┐
  │Worker 1││Worker2││Worker N │
  │        ││       ││        │
  │Processing    │Processing  │Processing
  │at 1080p/4K   │at 720p     │at 360p
  │ ~5min/video  │~2min/video │~1min/video
  └─────┬──┘└────┬──┘└───┬────┘
        │        │       │
  ┌─────▼────────▼───────▼────────┐
  │  Blob Storage (S3/GCS)         │
  │  Store processed video variants│
  └──────────────────────────────────┘

Worker scaling:
- Monitor queue depth
- If depth > 5000: Spin up more workers
- If depth < 1000: Scale down workers
- Keep some buffer for spikes
```

---

## 5. API Level Design

### 5.1 RESTful API Architecture

**API Gateway Pattern:**
```
Client Request
    ↓
API Gateway (Rate limiting, auth, routing)
    ├─ Path routing
    ├─ Authentication check
    ├─ Rate limiting (100 req/sec per user)
    ├─ Request validation
    └─ Response compression (gzip)
    ↓
Appropriate Microservice
    ↓
Response (with caching headers)
```

### 5.2 Core APIs

#### **Authentication & User Management**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "hashed_password",
  "username": "username123"
}

Response: 201 Created
{
  "user_id": 123456789,
  "channel_id": 987654321,
  "token": "JWT_TOKEN",
  "expires_in": 2592000  // 30 days
}
```

```http
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

Response: 200 OK
{
  "token": "JWT_TOKEN",
  "refresh_token": "REFRESH_TOKEN",
  "expires_in": 2592000
}
```

```http
GET /api/v1/users/{user_id}
Authorization: Bearer JWT_TOKEN

Response: 200 OK
{
  "user_id": 123456789,
  "username": "username123",
  "email": "user@example.com",
  "channel_id": 987654321,
  "profile_image_url": "https://cdn.example.com/profile.jpg",
  "bio": "Content creator",
  "subscriber_count": 1000000,
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z"
}

Cache: 1 hour (Redis key: "user:123456789")
```

#### **Video Upload & Management**

```http
POST /api/v1/videos/upload/initiate
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "title": "My First Video",
  "description": "This is my first video on YouTube",
  "tags": ["tutorial", "coding"],
  "visibility": "public",
  "category": "education",
  "language": "en",
  "file_size_bytes": 1073741824,  // 1GB
  "filename": "video.mp4"
}

Response: 200 OK
{
  "upload_session_id": "UPLOAD_SESSION_ID",
  "upload_url": "https://storage-api.example.com/upload/abc123",
  "chunk_size_bytes": 5242880,  // 5MB chunks
  "expires_in": 86400  // 24 hours
}
```

```http
PUT /api/v1/videos/upload/{upload_session_id}
Authorization: Bearer JWT_TOKEN
Content-Range: bytes 0-5242879/1073741824
Content-Type: video/mp4

[BINARY VIDEO CHUNK DATA]

Response: 200 OK
{
  "upload_session_id": "UPLOAD_SESSION_ID",
  "chunks_received": 5,
  "total_chunks": 204,
  "progress_percentage": 2.45,
  "next_chunk_number": 6
}
```

```http
POST /api/v1/videos/upload/{upload_session_id}/complete
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "file_hash": "SHA256_HASH_OF_FILE"
}

Response: 201 Created
{
  "video_id": 7123456789,
  "status": "processing",
  "estimated_processing_time_seconds": 600,
  "video_url": "https://youtube.example.com/watch?v=7123456789"
}
```

```http
GET /api/v1/videos/{video_id}
Accept-Encoding: gzip

Response: 200 OK
{
  "video_id": 7123456789,
  "channel_id": 987654321,
  "title": "My First Video",
  "description": "This is my first video",
  "duration_seconds": 1800,
  "view_count": 1000000,
  "like_count": 50000,
  "comment_count": 5000,
  "thumbnail_url": "https://cdn.example.com/thumbnails/7123456789.jpg",
  "status": "published",
  "published_at": "2024-01-20T10:30:00Z",
  "hls_url": "https://cdn.example.com/hls/7123456789/playlist.m3u8",
  "dash_url": "https://cdn.example.com/dash/7123456789/manifest.mpd",
  "channel": {
    "channel_id": 987654321,
    "channel_name": "Creator Name",
    "subscriber_count": 1000000
  }
}

Cache: 1 hour (Redis)
ETags: Enable HTTP caching with If-None-Match
Last-Modified: Include for cache validation
```

```http
PATCH /api/v1/videos/{video_id}
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "visibility": "private",
  "tags": ["updated", "tag"]
}

Response: 200 OK
{
  "video_id": 7123456789,
  "status": "published",
  "updated_at": "2024-01-25T15:30:00Z"
}

Cache invalidation: Delete "video:7123456789"
```

#### **Video Streaming (Playback)**

```http
GET /api/v1/videos/{video_id}/stream
Query params:
  - quality: auto|1080p|720p|480p|360p|240p
  - range: bytes=0-5242879 (HTTP 206 Partial Content)
Authorization: Optional (public videos)

Response: 206 Partial Content
Content-Type: video/mp4
Content-Range: bytes 0-5242879/1073741824
Content-Length: 5242880

[VIDEO CHUNK DATA - 5MB]

CDN-Cache-Control: public, max-age=2592000
X-CDN-Hit: true
X-Response-Time: 45ms
```

```http
GET /api/v1/videos/{video_id}/manifest
Query params:
  - format: hls|dash
Authorization: Optional

Response: 200 OK
Content-Type: application/vnd.apple.mpegurl  (for HLS)

#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0

#EXTINF:10.0,
segment_0.ts
#EXTINF:10.0,
segment_1.ts
...
```

#### **Comments & Engagement**

```http
POST /api/v1/videos/{video_id}/comments
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "text": "Great video! Thanks for the tutorial.",
  "parent_comment_id": null  // For top-level comment
}

Response: 201 Created
{
  "comment_id": "COMMENT_ID",
  "video_id": 7123456789,
  "user_id": 123456789,
  "text": "Great video! Thanks for the tutorial.",
  "likes_count": 0,
  "created_at": "2024-01-25T16:45:00Z"
}

Publish to message queue: comment_created event
```

```http
GET /api/v1/videos/{video_id}/comments
Query params:
  - sort: relevance|newest|top_rated
  - page: 1
  - limit: 20

Response: 200 OK
{
  "comments": [
    {
      "comment_id": "COMMENT_1",
      "user_id": 111111,
      "text": "Great tutorial!",
      "likes_count": 5000,
      "replies_count": 50,
      "created_at": "2024-01-25T10:00:00Z",
      "user": {
        "username": "creator",
        "profile_image": "url"
      }
    }
  ],
  "total_comments": 5000,
  "page": 1,
  "has_next_page": true
}

Cache: 30 minutes (different cache per sort order)
```

```http
POST /api/v1/videos/{video_id}/like
Authorization: Bearer JWT_TOKEN

{
  "like_type": "like"  // "like" or "dislike"
}

Response: 200 OK
{
  "video_id": 7123456789,
  "like_type": "like",
  "total_likes": 50001
}

Cache: Immediate deletion + increment counter atomically
```

#### **Subscriptions**

```http
POST /api/v1/channels/{channel_id}/subscribe
Authorization: Bearer JWT_TOKEN

Response: 200 OK
{
  "channel_id": 987654321,
  "subscribed": true,
  "subscriber_count": 1000001
}

Cache invalidation: user_subscriptions:{user_id}
```

```http
GET /api/v1/users/{user_id}/subscriptions
Authorization: Bearer JWT_TOKEN
Query params:
  - page: 1
  - limit: 20

Response: 200 OK
{
  "subscriptions": [
    {
      "channel_id": 111111,
      "channel_name": "Tech Creator",
      "subscriber_count": 1000000,
      "subscribed_at": "2024-01-10T10:30:00Z"
    }
  ],
  "total_count": 150
}

Cache: 1 hour (per user)
```

#### **Recommendations & Discovery**

```http
GET /api/v1/videos/recommendations
Authorization: Optional
Query params:
  - user_id: (optional, for personalized)
  - limit: 20
  - region: US|UK|IN|etc

Response: 200 OK
{
  "recommendations": [
    {
      "video_id": 7123456789,
      "title": "Recommended Video",
      "thumbnail_url": "url",
      "channel_name": "Creator",
      "view_count": 1000000,
      "recommendation_reason": "Based on your watch history"
    }
  ]
}

Cache: 24 hours (Redis: "recommendations:{user_id}")
Algorithm: Collaborative filtering + Content-based
```

```http
GET /api/v1/search
Query params:
  - q: "python tutorial"
  - type: video|channel|playlist
  - sort: relevance|upload_date|view_count
  - filters: duration|upload_date|channel_type
  - page: 1
  - limit: 20

Response: 200 OK
{
  "results": [
    {
      "video_id": 7123456789,
      "title": "Python Tutorial",
      "description": "Learn Python...",
      "thumbnail_url": "url",
      "channel_name": "Coding Channel",
      "view_count": 5000000,
      "published_at": "2024-01-20T10:30:00Z",
      "match_score": 0.95
    }
  ],
  "total_results": 100000,
  "page": 1,
  "has_next_page": true
}

Cache: 6 hours
Backend: Elasticsearch query with aggregations
Latency: <200ms p99
```

#### **Analytics (Creator Dashboard)**

```http
GET /api/v1/channels/{channel_id}/analytics
Authorization: Bearer JWT_TOKEN (channel owner)
Query params:
  - start_date: 2024-01-01
  - end_date: 2024-01-31
  - metrics: views,watch_time,subscribers,revenue

Response: 200 OK
{
  "channel_id": 987654321,
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "metrics": {
    "total_views": 5000000,
    "total_watch_time_hours": 50000,
    "new_subscribers": 10000,
    "estimated_revenue": 50000,
    "engagement_rate": 0.05,
    "average_view_duration_seconds": 600
  },
  "top_videos": [
    {
      "video_id": 7123456789,
      "title": "Top Video",
      "views": 1000000,
      "watch_time_hours": 20000,
      "revenue": 20000
    }
  ],
  "demographics": {
    "top_countries": ["US", "IN", "UK"],
    "age_groups": {"18-24": 0.3, "25-34": 0.4, "35+": 0.3},
    "gender": {"male": 0.6, "female": 0.35, "other": 0.05}
  }
}

Cache: 24 hours (updated daily)
Backend: Bigtable/HBase time-series data
```

### 5.3 API Response Format & Standards

```json
// Success Response (200 OK)
{
  "status": "success",
  "code": 200,
  "data": {
    // Actual response data
  },
  "meta": {
    "request_id": "req_12345",
    "timestamp": "2024-01-25T16:45:00Z",
    "api_version": "v1"
  }
}

// Paginated Response
{
  "status": "success",
  "code": 200,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1000,
    "pages": 50,
    "has_next": true,
    "has_prev": false
  }
}

// Error Response (4xx/5xx)
{
  "status": "error",
  "code": 400,
  "error": {
    "message": "Invalid request",
    "type": "VALIDATION_ERROR",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "request_id": "req_12345",
    "timestamp": "2024-01-25T16:45:00Z"
  }
}
```

### 5.4 Rate Limiting & Quotas

```
Standard Rate Limits:
├─ Unauthenticated user: 10 req/minute (IP-based)
├─ Authenticated user: 100 req/minute (user_id-based)
├─ Video upload: 10 uploads/day per user
├─ Comment post: 50 comments/hour per user
├─ Search: 1000 searches/day per user
└─ API: 10K req/minute per API key

Implementation:
  - Token bucket algorithm (Redis)
  - Header: X-RateLimit-Limit, X-RateLimit-Remaining
  - 429 Too Many Requests on violation
  - Exponential backoff (client-side)
```

---

## 6. Storage Management

### 6.1 Video Storage Architecture

**Blob Storage (S3/Google Cloud Storage):**

```
s3://videos-production/
├── raw/                           # Original uploaded videos
│   └── {video_id}/
│       └── original.mp4
│
├── processed/                     # Transcoded variants
│   ├── {video_id}/
│   │   ├── 1080p/
│   │   │   └── video.mp4 (h264, 2500 kbps)
│   │   ├── 720p/
│   │   │   └── video.mp4 (h264, 1500 kbps)
│   │   ├── 480p/
│   │   │   └── video.mp4 (h264, 800 kbps)
│   │   ├── 360p/
│   │   │   └── video.mp4 (h264, 400 kbps)
│   │   ├── 240p/
│   │   │   └── video.mp4 (h264, 200 kbps)
│   │   └── dash_manifest.mpd
│   │   └── hls_playlist.m3u8
│
├── thumbnails/                    # Video thumbnails
│   └── {video_id}/
│       ├── default.jpg (320x180)
│       ├── medium.jpg (320x180)
│       ├── high.jpg (480x360)
│       ├── maxres.jpg (1280x720)
│       └── custom.jpg (user-uploaded)
│
└── archives/                      # Old/deleted videos
    └── {year}/{month}/{video_id}/
        └── {archive_date}.tar.gz

Storage Distribution:
├─ Origin datacenter (Tier 1): 5%  - Hot access, fast retrieval
├─ Regional centers (Tier 2): 20%  - Warm access, CDN source
└─ Archive storage (Tier 3): 75%   - Cold access, rare retrieval, cheap
```

**Storage Costs Optimization:**

```
Tier 1 (Origin): $0.023/GB/month
├─ Used for: Active videos (< 1 month old)
├─ Capacity: 50 PB
└─ Monthly cost: $1.15M

Tier 2 (Regional): $0.016/GB/month
├─ Used for: Popular videos (1-12 months)
├─ Capacity: 200 PB
└─ Monthly cost: $3.2M

Tier 3 (Archive): $0.004/GB/month
├─ Used for: Old/unpopular videos (> 12 months)
├─ Capacity: 750 PB
└─ Monthly cost: $3M

Total monthly storage: $7.35M
Annual storage: ~$88M

Optimization strategies:
1. Delete videos no views in 90 days (archive first)
2. Lower resolution for old popular videos
3. Compress less-accessed content
4. Use object lifecycle policies
```

### 6.2 Replication & Durability

**S3 Replication Strategy:**

```
Primary Region (us-east-1)
    ↓ (Synchronous replication)
Secondary Region (eu-west-1)
    ↓ (Asynchronous replication)
Tertiary Region (ap-southeast-1)

Durability: 11 nines (99.999999999%)
RPO: <1 second (async replication lag)
RTO: <1 minute (automatic failover)

Versioning:
├─ Keep 7 versions per object
├─ Enable MFA delete protection
└─ Lifecycle: Delete old versions after 30 days
```

### 6.3 Video Codec & Encoding Strategy

**Adaptive Bitrate Ladder:**

```
Resolution | Bitrate | Codec | Use Case
-----------|---------|-------|----------
4K (2160p) | 6000kbps | VP9  | Premium subscribers, high-speed users
1080p      | 2500kbps | h264 | Desktop, modern devices
720p       | 1500kbps | h264 | Tablet, good connection
480p       | 800kbps  | h264 | Mobile, moderate connection
360p       | 400kbps  | h264 | Mobile, slow connection
240p       | 200kbps  | h264 | Low-bandwidth fallback

Encoding Parameters:
├─ Container: MP4 (H.264), WebM (VP9)
├─ Frame rate: 24fps (film), 30fps (default), 60fps (gaming)
├─ Keyframe interval: Every 2 seconds
├─ Audio: AAC 128kbps, Stereo 48kHz
└─ Processing time: ~30 minutes per hour of video

Codec choice:
├─ H.264: Maximum compatibility, browsers
├─ VP9: Better compression, newer browsers
└─ AV1: Best compression, limited support
```

### 6.4 CDN Configuration

**Multi-CDN Strategy:**

```
                     User Request
                          ↓
                  ┌─────────────────┐
                  │ Intelligent     │
                  │ Load Balancer   │
                  │ (GeoDNS)        │
                  └────────┬────────┘
                           ↓
        ┌──────────────────┼──────────────────┐
        │                  │                   │
   ┌────▼────┐      ┌─────▼─────┐     ┌──────▼────┐
   │Akamai   │      │CloudFlare │     │Cloudfront │
   │(40%)    │      │(35%)      │     │(25%)      │
   │         │      │           │     │           │
   │Primary  │      │Backup     │     │Backup     │
   │for US   │      │for EU     │     │for APAC   │
   └────┬────┘      └─────┬─────┘     └──────┬────┘
        │                  │                   │
        └──────────────────┼───────────────────┘
                           ↓
                   Origin Server
                   (S3 bucket)

Benefits:
├─ Redundancy: If Akamai fails, traffic routes to CloudFlare
├─ Cost optimization: Play traffic between CDNs
├─ Performance: Choose best CDN per region
└─ DDoS protection: Distributed across providers
```

### 6.5 Cache Headers & Expiration

```
# For published videos (immutable content)
Cache-Control: public, max-age=2592000, immutable
ETag: "abc123def456"
Last-Modified: Wed, 20 Jan 2024 10:30:00 GMT

# For video metadata (mutable, frequently accessed)
Cache-Control: public, max-age=3600
ETag: "video_stats_v2"
Last-Modified: Today

# For user-specific content (private)
Cache-Control: private, max-age=1800
Set-Cookie: session_id=xyz

# For thumbnails (long-lived)
Cache-Control: public, max-age=31536000
ETag: "thumb_v1"

# For dynamic content (recommendations, trending)
Cache-Control: public, max-age=21600
Vary: Accept-Encoding, User-Agent
```

---

## 7. Core Services Deep-Dive

### 7.1 Video Upload & Processing Service

**Flow:**
```
1. User selects video file
2. Client initiates upload session (multipart upload)
3. File split into 5MB chunks
4. Chunks uploaded with progress tracking
5. Chunks stored in staging S3 bucket
6. Upload completion verified (file hash)
7. Video enqueued to processing queue (Kafka)
8. Processing workers transcode to multiple formats
9. Results stored in permanent S3 location
10. Metadata updated in database
11. Subscribers notified
12. Video searchable and recommendable
```

**Processing Workers (Docker containers):**
```dockerfile
FROM ubuntu:latest

RUN apt-get install -y ffmpeg mediainfo awscli

ENV WORKER_ID=worker-1
ENV QUEUE_BROKER=kafka://broker:9092
ENV S3_BUCKET=videos-processed

COPY process_video.py /app/
WORKDIR /app

CMD ["python", "process_video.py"]
```

**process_video.py:**
```python
import json
import subprocess
from kafka import KafkaConsumer
from boto3 import client as s3_client

consumer = KafkaConsumer(
    'video_uploads',
    bootstrap_servers=['kafka:9092'],
    group_id='video-processors',
    max_poll_records=1  # One video at a time
)

s3 = s3_client('s3')

def transcode_video(video_id, source_s3_path):
    """Transcode video to multiple formats"""
    
    # Download from S3
    s3.download_file('staging', source_s3_path, f'/tmp/{video_id}.mp4')
    
    # Transcode to each format
    formats = {
        '1080p': {'bitrate': '2500k', 'resolution': '1920x1080'},
        '720p': {'bitrate': '1500k', 'resolution': '1280x720'},
        '480p': {'bitrate': '800k', 'resolution': '854x480'},
        '360p': {'bitrate': '400k', 'resolution': '640x360'},
        '240p': {'bitrate': '200k', 'resolution': '426x240'},
    }
    
    for format_name, params in formats.items():
        output_path = f'/tmp/{video_id}_{format_name}.mp4'
        
        cmd = [
            'ffmpeg',
            '-i', f'/tmp/{video_id}.mp4',
            '-b:v', params['bitrate'],
            '-s', params['resolution'],
            '-c:v', 'h264',
            '-c:a', 'aac',
            '-preset', 'medium',  # balance quality & speed
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        
        # Upload to S3
        s3.upload_file(
            output_path,
            'videos-processed',
            f'{video_id}/{format_name}/video.mp4'
        )
    
    return True

# Main loop
for message in consumer:
    video_info = json.loads(message.value)
    video_id = video_info['video_id']
    
    try:
        transcode_video(video_id, video_info['staging_path'])
        
        # Update database
        db.update_video_status(video_id, 'published')
        
        # Publish to Kafka
        notification_producer.send(
            'video_published',
            {
                'video_id': video_id,
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        # Mark as failed, retry
        db.update_video_status(video_id, 'failed')
        print(f"Error processing {video_id}: {e}")
```

### 7.2 Video Streaming Service

**Streaming Protocol: HLS (HTTP Live Streaming)**

```
Master Playlist (m3u8):
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1920x1080
https://cdn.example.com/hls/{video_id}/1080p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=1280x720
https://cdn.example.com/hls/{video_id}/720p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=854x480
https://cdn.example.com/hls/{video_id}/480p/playlist.m3u8

Resolution Playlist (variant playlist):
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
segment_0.ts
#EXTINF:10.0,
segment_1.ts
#EXTINF:10.0,
segment_2.ts
#EXT-X-ENDLIST

Segment structure:
├─ segment_0.ts (0-10 seconds)
├─ segment_1.ts (10-20 seconds)
└─ segment_n.ts (duration varies)

Playback strategy:
1. Player fetches master playlist
2. Selects variant based on bandwidth
3. Fetches variant playlist
4. Continuously requests segments
5. Adapts quality if bandwidth changes
```

**Streaming Service Code (Node.js):**

```javascript
const express = require('express');
const { VideoStreamManager } = require('./video-manager');
const cache = require('./redis-cache');

const app = express();
const videoManager = new VideoStreamManager();

// Get playlist (m3u8)
app.get('/api/v1/stream/:videoId/:quality/playlist.m3u8', async (req, res) => {
  const { videoId, quality } = req.params;
  const userId = req.user?.id;
  
  // Check cache
  const cacheKey = `playlist:${videoId}:${quality}`;
  let playlist = await cache.get(cacheKey);
  
  if (!playlist) {
    // Verify video exists and user has access
    const video = await db.getVideo(videoId);
    if (!video) return res.status(404).send('Not found');
    if (!videoManager.canUserWatch(userId, video)) {
      return res.status(403).send('Forbidden');
    }
    
    // Generate playlist (list of segments)
    playlist = videoManager.generatePlaylist(videoId, quality);
    
    // Cache for 1 hour
    await cache.set(cacheKey, playlist, 3600);
  }
  
  res.set('Content-Type', 'application/vnd.apple.mpegurl');
  res.set('Cache-Control', 'public, max-age=3600');
  res.send(playlist);
});

// Get segment (TS file)
app.get('/api/v1/stream/:videoId/:quality/segment_:segmentNum.ts', async (req, res) => {
  const { videoId, quality, segmentNum } = req.params;
  
  // Direct CDN response (CDN has cached)
  const segmentPath = `${videoId}/${quality}/segment_${segmentNum}.ts`;
  
  // Log streaming event for analytics
  await queue.send('streaming_event', {
    video_id: videoId,
    user_id: req.user?.id,
    segment: segmentNum,
    quality,
    timestamp: Date.now()
  });
  
  // Redirect to CDN (or serve directly if origin)
  res.redirect(301, `https://cdn.example.com/stream/${segmentPath}`);
});

// Get video info (metadata)
app.get('/api/v1/videos/:videoId', async (req, res) => {
  const { videoId } = req.params;
  
  // Check cache
  const cacheKey = `video:${videoId}`;
  let video = await cache.get(cacheKey);
  
  if (!video) {
    video = await db.getVideo(videoId);
    if (!video) return res.status(404).json({ error: 'Not found' });
    
    // Cache for 1 hour
    await cache.set(cacheKey, video, 3600);
  }
  
  res.json(video);
});

app.listen(3000);
```

### 7.3 Search & Recommendation Service

**Search Architecture (Elasticsearch):**

```javascript
// Indexing (batch)
const searchService = {
  indexVideo: async (video) => {
    const esClient = new elasticsearch.Client();
    
    await esClient.index({
      index: 'videos',
      id: video.video_id,
      body: {
        video_id: video.video_id,
        title: video.title,
        description: video.description,
        tags: video.tags,
        channel_name: video.channel_name,
        view_count: video.view_count,
        like_count: video.like_count,
        comment_count: video.comment_count,
        published_at: video.published_at,
        popularity_score: calculatePopularityScore(video),
        language: video.language,
        content_type: video.content_type,
      }
    });
  },
  
  search: async (query, filters = {}) => {
    const esClient = new elasticsearch.Client();
    
    const searchBody = {
      query: {
        bool: {
          must: [
            {
              multi_match: {
                query,
                fields: ['title^3', 'description^2', 'tags'],
                type: 'best_fields',
                operator: 'or'
              }
            }
          ],
          filter: [
            { term: { visibility: 'public' } }
          ]
        }
      },
      sort: [
        { _score: { order: 'desc' } },
        { view_count: { order: 'desc' } }
      ],
      size: filters.limit || 20,
      from: filters.offset || 0
    };
    
    // Apply filters
    if (filters.duration) {
      searchBody.query.bool.filter.push({
        range: { duration_seconds: filters.duration }
      });
    }
    
    if (filters.published_after) {
      searchBody.query.bool.filter.push({
        range: { published_at: { gte: filters.published_after } }
      });
    }
    
    const results = await esClient.search({
      index: 'videos',
      body: searchBody
    });
    
    return results.body.hits.hits.map(hit => hit._source);
  },
  
  autocomplete: async (prefix) => {
    const esClient = new elasticsearch.Client();
    
    const results = await esClient.search({
      index: 'videos',
      body: {
        query: {
          match: {
            'title.suggest': {
              query: prefix,
              _name: 'suggestions'
            }
          }
        },
        size: 10
      }
    });
    
    return results.body.hits.hits.map(hit => hit._source.title);
  }
};
```

**Recommendation Service (ML-based):**

```python
# Recommendation engine
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

class RecommendationEngine:
    def __init__(self):
        self.mongo = MongoClient()
        self.db = self.mongo['youtube']
        self.cache = redis.Redis()
    
    def get_recommendations(self, user_id, limit=20):
        # Check cache first
        cache_key = f'recommendations:{user_id}'
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Get user's watch history
        user_history = list(self.db.watch_history.find(
            {'user_id': user_id},
            sort=[('watch_timestamp', -1)],
            limit=50
        ))
        
        if not user_history:
            # Cold start: Return trending videos
            return self._get_trending_videos(limit)
        
        # Collaborative filtering + Content-based
        recommendations = []
        
        # 1. Collaborative filtering (users like you also watched)
        similar_users = self._find_similar_users(user_id)
        collab_videos = self._get_videos_from_users(similar_users, exclude_watched(user_id))
        
        # 2. Content-based (videos similar to your watch history)
        content_videos = self._get_similar_content(user_history)
        
        # 3. Trending in user's region
        trending_videos = self._get_trending_by_region(user_id)
        
        # Combine and score
        all_recs = {}
        
        for video, score in collab_videos:
            all_recs[video['video_id']] = {
                'video': video,
                'collab_score': score,
                'content_score': 0,
                'trending_score': 0
            }
        
        for video, score in content_videos:
            vid = video['video_id']
            if vid not in all_recs:
                all_recs[vid] = {'video': video, 'collab_score': 0, 'content_score': 0, 'trending_score': 0}
            all_recs[vid]['content_score'] = score
        
        for video, score in trending_videos:
            vid = video['video_id']
            if vid not in all_recs:
                all_recs[vid] = {'video': video, 'collab_score': 0, 'content_score': 0, 'trending_score': 0}
            all_recs[vid]['trending_score'] = score
        
        # Weighted ensemble
        scored = [
            (v['video'], 0.5 * v['collab_score'] + 0.3 * v['content_score'] + 0.2 * v['trending_score'])
            for v in all_recs.values()
        ]
        
        recommendations = sorted(scored, key=lambda x: x[1], reverse=True)[:limit]
        
        # Cache for 24 hours
        self.cache.setex(
            cache_key,
            86400,
            json.dumps([{'video_id': v[0]['video_id'], 'score': float(v[1])} for v in recommendations])
        )
        
        return recommendations
    
    def _find_similar_users(self, user_id, limit=100):
        # Find users with similar watch patterns
        user_vector = self._create_user_vector(user_id)
        all_users = self.db.users.find({'user_id': {'$ne': user_id}})
        
        similarities = []
        for user in all_users:
            user_vec = self._create_user_vector(user['user_id'])
            sim = cosine_similarity([user_vector], [user_vec])[0][0]
            similarities.append((user['user_id'], sim))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:limit]
    
    def _create_user_vector(self, user_id):
        # Create embedding vector from user's watch history
        history = list(self.db.watch_history.find({'user_id': user_id}))
        
        # Simple approach: vector of video category counts
        categories = {}
        for watch in history:
            video = self.db.videos.find_one({'video_id': watch['video_id']})
            cat = video.get('content_type', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        return np.array([categories.get(cat, 0) for cat in ['education', 'entertainment', 'music', 'sports', 'news']])
```

---

## 8. Decision Trade-offs

### 8.1 Key Architectural Decisions

#### **Decision 1: PostgreSQL + MongoDB (Hybrid)**

**Problem:** Single database cannot handle both structured and unstructured data at scale

**Options Considered:**
| Option | Pros | Cons |
|--------|------|------|
| **PostgreSQL only** | ACID, strong consistency | Poor horizontal scaling, rigid schema, high storage |
| **MongoDB only** | Flexible schema, horizontal scaling | No ACID (pre-4.0), eventual consistency, complex joins |
| **Hybrid (Chosen)** | Best of both worlds | Complexity, data sync, operational overhead |

**Decision:** Hybrid approach
- PostgreSQL: Structured data (users, videos metadata, subscriptions, payments)
- MongoDB: Unstructured (comments, engagement events, recommendations)

**Trade-off:**
```
✓ Scales to 1B+ videos
✓ ACID for critical data
✓ Flexible schema for evolving features
✗ Complex operational setup
✗ Data consistency between systems
```

**Mitigation:**
- Careful domain separation
- Event-driven sync (Kafka)
- Regular reconciliation jobs

---

#### **Decision 2: CDN Caching Over Origin Serving**

**Problem:** Billions of requests/second cannot be handled by origin servers

**Options Considered:**
| Option | Latency | Cost | Feasibility |
|--------|---------|------|-------------|
| **Single origin server** | 50-100ms | Low | No - fails at 1000s QPS |
| **Regional datacenters** | 20-50ms | Medium | No - still can't handle volume |
| **Global CDN (Chosen)** | 3-10ms | Medium-High | Yes - can handle Pb/s |

**Decision:** Multi-CDN with edge caching
- Akamai (40% traffic): Primary
- CloudFlare (35% traffic): Backup for EU
- CloudFront (25% traffic): Backup for APAC

**Trade-off:**
```
✓ Sub-10ms latency globally
✓ Handles Pb/s bandwidth
✓ Built-in DDoS protection
✗ Significant monthly cost (~$50M+)
✗ Vendor lock-in risk
✗ Cache invalidation complexity
```

**Cost optimization:**
- Use origin shielding (mid-tier cache)
- Compress content (30% reduction)
- Multi-CDN failover (prevent overpaying one provider)

---

#### **Decision 3: Horizontal Sharding Over Vertical Scaling**

**Problem:** PostgreSQL single server max ~100K QPS, need 200K+

**Options Considered:**
| Option | Scalability | Complexity | Cost |
|--------|-------------|-----------|------|
| **Vertical scaling (bigger hardware)** | Limited to $1M+ servers | Low | Very high |
| **Replication (read replicas)** | Helps reads only, not writes | Medium | High |
| **Sharding (Chosen)** | Unlimited horizontal | High | Medium |

**Decision:** Consistent hashing for sharding
```
video_id % num_shards = shard_id
Current: 256 shards
Each shard: ~4M videos, 1 primary + 3 replicas
```

**Trade-off:**
```
✓ Scales to any number of videos
✓ Even load distribution
✓ Independent shard scaling
✗ Operational complexity (shard management)
✗ Cross-shard joins impossible
✗ Hot shard risk (need good hash function)
✗ Rebalancing cost (multi-week migrations)
```

**Mitigation:**
- Consistent hashing (easy rebalancing)
- Monitoring for hot shards
- Regular rebalancing schedule

---

#### **Decision 4: Eventual Consistency Over Strong Consistency**

**Problem:** Strong consistency at YouTube scale (2.5B users) requires locking, blocking

**Options Considered:**
| Approach | Consistency | Latency | Availability |
|----------|-----------|---------|--------------|
| **Strong consistency** | Perfect | High (100-500ms) | Lower (99.9%) |
| **Eventual consistency (Chosen)** | ~1-5 seconds | Low (10-50ms) | Higher (99.99%) |

**Decision:** Eventual consistency for most data
- Comments: Eventually consistent, ok to see slight delay
- Likes: Eventually consistent (counter can be 100 off)
- Views: Eventually consistent (can be 1000s off momentarily)
- Subscriptions: Eventually consistent (delay ok)
- Payments: Strong consistency (critical)

**Trade-off:**
```
✓ 10x better latency
✓ Higher availability
✓ Better handling of network partitions
✗ Users see slightly stale data
✗ Conflict resolution needed
✗ Testing complexity
```

**Examples of eventual consistency in use:**
```
When user likes a video:
├─ Immediate: Like stored in user's local cache
├─ 100ms: Sent to database
├─ 500ms: Counter increment queued
├─ 5 seconds: Counter incremented on all replicas
└─ 1 minute: View count cache updated

User sees: Like count slightly stale, but interaction is instant
```

---

#### **Decision 5: Message Queue for Async Processing**

**Problem:** Video processing takes 10+ minutes, cannot block upload

**Options Considered:**
| Option | Throughput | Latency | Complexity |
|--------|-----------|---------|-----------|
| **Synchronous processing** | 100 videos/min | Blocked user | Low |
| **Message queue (Chosen)** | 500K videos/hour | Async (fast) | Medium |

**Decision:** Kafka for event streaming
- Topic: video_uploads (300 partitions)
- Retention: 7 days
- Processing: 300 workers (1 per partition)

**Trade-off:**
```
✓ Handles 500+ hour/minute uploads
✓ Resilient to processing failures
✓ Can adjust processing speed independently
✗ Operational complexity (Kafka cluster)
✗ Eventual consistency (users see "processing" for minutes)
✗ Failure debugging harder
```

---

#### **Decision 6: Denormalization Over Normalization**

**Problem:** Normalized schema requires joins, slow with 1B+ rows

**Examples of denormalization:**

```sql
-- Normalized (slow)
SELECT v.title, v.view_count, c.channel_name, c.subscriber_count
FROM videos v
JOIN channels c ON v.channel_id = c.channel_id
WHERE v.video_id = 123;

-- Denormalized (fast)
SELECT title, view_count, channel_name, subscriber_count
FROM videos
WHERE video_id = 123;
```

**Decision:** Denormalize frequently accessed data
```sql
-- Videos table includes channel info (stored twice)
videos:
  - video_id
  - channel_id
  - channel_name (denormalized)
  - subscriber_count (denormalized from channels)
```

**Trade-off:**
```
✓ 10x faster queries (no joins)
✓ Better for read-heavy workloads
✓ Simpler for sharding
✗ Data duplication (~20% extra storage)
✗ Consistency challenges (updates need sync)
✗ Complex writes (update both places)
```

**Mitigation:**
- Use async event-driven sync (Kafka)
- Reconciliation jobs (hourly)
- Accept 1-hour inconsistency window

---

### 8.2 Performance vs Cost Trade-offs

```
┌──────────────────────────────────────────────────────┐
│         YouTube Economics (Rough)                     │
└──────────────────────────────────────────────────────┘

Monthly Operating Costs:

├─ Compute (Kubernetes/EC2)
│  ├─ API Servers: $20M (100K instances @ $200/month)
│  ├─ Video Processing: $15M (10K GPUs @ $1500/month)
│  └─ Support Services: $10M
│  Total: $45M
│
├─ Storage
│  ├─ Video storage: $88M (1000 PB + replication)
│  ├─ Database: $10M (sharded PostgreSQL + MongoDB)
│  └─ Cache: $5M (Redis + Memcached)
│  Total: $103M
│
├─ CDN & Bandwidth
│  ├─ CDN costs: $50M (Pb/s bandwidth)
│  ├─ Bandwidth out: $30M (10 Pb/s egress)
│  └─ DDoS protection: $5M
│  Total: $85M
│
├─ Operational
│  ├─ Engineering: $30M (2000 engineers)
│  ├─ Customer support: $15M
│  └─ Monitoring/Logging: $10M
│  Total: $55M
│
└─ Total Monthly: ~$288M (~$3.5B/year)

Revenue (estimates):
├─ Ads: $400M/month (~$5B/year)
├─ Premium subscriptions: $50M/month
└─ YoutubeTv/Music: $50M/month
Total: $500M/month

Profit margin: ~43% before G&A
```

---

### 8.3 Availability & Disaster Recovery

**RTO vs RPO Trade-offs:**

```
Requirement: 99.99% uptime (52.6 minutes downtime/year)

Strategy:
├─ Multi-region active-active
│  ├─ Synchronous replication
│  ├─ RTO: <1 minute (automatic failover)
│  ├─ RPO: <1 second
│  └─ Cost: 2x normal
│
├─ Multi-region active-passive
│  ├─ Asynchronous replication
│  ├─ RTO: 5-10 minutes (manual failover)
│  ├─ RPO: <5 minutes
│  └─ Cost: 1.5x normal (Chosen for cost)
│
└─ Single region with backups
   ├─ RTO: 30+ minutes
   ├─ RPO: >1 hour
   └─ Cost: 1x normal

Chosen: Multi-region active-passive
- 3 regions: US-East, EU-West, APAC
- Primary serves all traffic
- Secondaries ready for failover
- Daily failover tests
```

---

### 8.4 Security vs Convenience Trade-offs

```
Video Protection:

├─ Option 1: DRM (Digital Rights Management)
│  ├─ Copy protection: Excellent
│  ├─ UX impact: Significant (slower, restrictions)
│  ├─ Cost: High ($5-10M/year)
│  └─ Usage: Premium content only
│
├─ Option 2: Watermarking
│  ├─ Copy protection: Moderate (traceable)
│  ├─ UX impact: Minimal
│  ├─ Cost: Medium ($2-5M/year)
│  └─ Usage: All videos (chosen for most)
│
└─ Option 3: None (Community flagging)
   ├─ Copy protection: Low
   ├─ UX impact: None
   ├─ Cost: Low (staff only)
   └─ Usage: User-generated content

Chosen hybrid:
├─ DRM for major studios (premium content)
├─ Watermarking for all uploads
└─ Community reporting for infringement
```

---

## Conclusion

This comprehensive YouTube system design covers:

1. **Database Design**: Hybrid PostgreSQL + MongoDB with smart sharding
2. **Scaling Strategy**: 256+ horizontal shards, multi-layer caching, auto-scaling workers
3. **API Design**: RESTful APIs following YouTube's actual endpoints
4. **Storage Management**: Petabyte-scale blob storage with multi-region replication
5. **Decision Trade-offs**: Explained each major architectural decision with pros/cons

**Key Takeaways:**
- **Scalability**: Horizontal sharding + CDN caching handles billions of users
- **Performance**: 3-50ms latency through edge caching + clever replication
- **Reliability**: 99.99% availability through redundancy + failover
- **Cost**: ~$3.5B/year operating costs balanced with revenue

This design is production-tested at YouTube's scale and applicable to any large-scale video platform.

---

## Additional Resources

**System Design Concepts to Study:**
- Consistent hashing (for sharding)
- Event sourcing (for audit trails)
- CQRS pattern (read/write separation)
- Saga pattern (distributed transactions)
- Circuit breaker (failure handling)

**Technologies Mentioned:**
- Container: Docker, Kubernetes
- Message Queue: Kafka, RabbitMQ
- Database: PostgreSQL, MongoDB, Elasticsearch
- Cache: Redis, Memcached
- Storage: AWS S3, Google Cloud Storage
- CDN: Akamai, Cloudflare, CloudFront
- Monitoring: Prometheus, Datadog, ELK Stack

**Interview Tips:**
1. Start with requirements & constraints
2. Estimate capacity (QPS, storage, bandwidth)
3. Design database schema carefully
4. Discuss trade-offs explicitly
5. Justify every major decision
6. Consider failure scenarios
7. Mention monitoring & observability
8. Be ready to drill down on any component
