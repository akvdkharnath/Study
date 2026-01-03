# Redis Architecture - Complete Visual Guide

This document covers Redis internal architecture, replication, sharding, and production setups with detailed diagrams.

---

## Table of Contents
1. [Redis Internal Queue (Event Loop)](#1-redis-internal-queue-event-loop)
2. [Replication (Master-Replica)](#2-replication-master-replica)
3. [Sharding (Redis Cluster)](#3-sharding-redis-cluster)
4. [Replication + Sharding (Production Setup)](#4-replication--sharding-production-setup)

---

## 1. Redis Internal Queue (Event Loop)

Redis uses an **event-driven architecture** with an internal queue to handle concurrent requests from multiple clients.

### How Redis Handles Multiple Clients

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REDIS EVENT LOOP ARCHITECTURE                        │
│                                                                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│   │Client 1 │  │Client 2 │  │Client 3 │  │Client 4 │  │Client N │     │
│   │(Auth    │  │(Orders  │  │(Payment │  │(Catalog │  │ (...)   │     │
│   │Service) │  │Service) │  │Service) │  │Service) │  │         │     │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘     │
│        │            │            │            │            │           │
│        │   GET      │   SET      │   HGET     │   INCR     │           │
│        │            │            │            │            │           │
│        └────────────┴─────┬──────┴────────────┴────────────┘           │
│                           │                                             │
│                           ▼                                             │
│              ┌────────────────────────────┐                            │
│              │      NETWORK I/O LAYER     │                            │
│              │   (Receives all requests)  │                            │
│              └─────────────┬──────────────┘                            │
│                            │                                            │
│                            ▼                                            │
│              ┌────────────────────────────┐                            │
│              │     INTERNAL QUEUE         │                            │
│              │                            │                            │
│              │  ┌────┬────┬────┬────┐    │                            │
│              │  │CMD1│CMD2│CMD3│CMD4│... │  ← Commands queued         │
│              │  └────┴────┴────┴────┘    │                            │
│              └─────────────┬──────────────┘                            │
│                            │                                            │
│                            ▼                                            │
│              ┌────────────────────────────┐                            │
│              │    SINGLE MAIN THREAD      │                            │
│              │                            │                            │
│              │  Processes ONE command     │                            │
│              │  at a time (sequential)    │                            │
│              │                            │                            │
│              │  Time per command: ~1μs    │                            │
│              └────────────────────────────┘                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Command Processing Timeline

```
Timeline (in microseconds):
═══════════════════════════════════════════════════════════════════════════

Time 0μs:    Multiple clients send commands (arrive at Redis)
             ┌─────────────────────────────────────────────────────────┐
             │ Queue: [GET user:1] [SET cart:2] [HGET prod:3] [INCR x] │
             └─────────────────────────────────────────────────────────┘

Time 1μs:    Process GET user:1     → Response to Client 1 ✓
Time 2μs:    Process SET cart:2     → Response to Client 2 ✓
Time 3μs:    Process HGET prod:3    → Response to Client 3 ✓
Time 4μs:    Process INCR x         → Response to Client 4 ✓

═══════════════════════════════════════════════════════════════════════════
Total: 4 microseconds for ALL 4 requests = 0.004 milliseconds
       Users perceive this as "instant" ⚡
═══════════════════════════════════════════════════════════════════════════
```

### Redis Threading Model (Complete Picture)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      REDIS THREADING MODEL                              │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    MAIN THREAD (Single)                           │ │
│  │                                                                   │ │
│  │    • Receives commands from queue                                │ │
│  │    • Executes GET, SET, HSET, LPUSH, etc.                       │ │
│  │    • All data operations happen HERE                            │ │
│  │    • No locks needed = FAST!                                    │ │
│  │                                                                   │ │
│  │    Throughput: 100,000 - 300,000+ ops/second                    │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                               │                                         │
│                               │ Delegates background work              │
│                               ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                  BACKGROUND THREADS (Multiple)                    │ │
│  │                                                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │ │
│  │  │ bio_lazy_free   │  │ bio_aof_fsync   │  │ bio_close_file  │  │ │
│  │  │                 │  │                 │  │                 │  │ │
│  │  │ UNLINK memory   │  │ AOF persistence │  │ File operations │  │ │
│  │  │ cleanup         │  │ disk sync       │  │                 │  │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Since Redis 6.0:                                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    I/O THREADS (Configurable)                     │ │
│  │                                                                   │ │
│  │    • Network read/write operations                               │ │
│  │    • Parsing client requests                                     │ │
│  │    • Sending responses                                           │ │
│  │    • Does NOT execute commands (main thread still does that)     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

KEY INSIGHT:
═══════════════════════════════════════════════════════════════════════════
"Single-threaded" means DATA OPERATIONS run on ONE thread.
Background tasks (memory cleanup, disk I/O) use SEPARATE threads.
This gives Redis both SIMPLICITY (no locks) and PERFORMANCE (async I/O).
═══════════════════════════════════════════════════════════════════════════
```

### Why Single Thread Works

```
Latency Breakdown for Typical Request:
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│   Client → Network → Redis → Network → Client                         │
│                                                                        │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │  Network round trip:        0.5 - 2.0 ms                     │    │
│   │  Redis command execution:   0.001 ms   ◀── Only 0.1% of time!│    │
│   │  Network response:          0.5 - 2.0 ms                     │    │
│   └──────────────────────────────────────────────────────────────┘    │
│                                                                        │
│   BOTTLENECK IS NETWORK, NOT REDIS!                                   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Replication (Master-Replica)

Replication provides **High Availability** and **Read Scaling**.

### Basic Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      REDIS REPLICATION SETUP                            │
│                                                                         │
│                       ┌─────────────────────┐                          │
│                       │       MASTER        │                          │
│                       │     (Primary)       │                          │
│                       │                     │                          │
│                       │   ✅ READ allowed   │                          │
│                       │   ✅ WRITE allowed  │                          │
│                       │                     │                          │
│                       │   All data here     │                          │
│                       └──────────┬──────────┘                          │
│                                  │                                      │
│                    ┌─────────────┼─────────────┐                       │
│                    │             │             │                        │
│                    │  Async      │  Async      │  Async                │
│                    │  Replication│  Replication│  Replication          │
│                    ▼             ▼             ▼                        │
│           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│           │   REPLICA 1  │ │   REPLICA 2  │ │   REPLICA 3  │           │
│           │   (Slave)    │ │   (Slave)    │ │   (Slave)    │           │
│           │              │ │              │ │              │           │
│           │ ✅ READ      │ │ ✅ READ      │ │ ✅ READ      │           │
│           │ ❌ WRITE     │ │ ❌ WRITE     │ │ ❌ WRITE     │           │
│           │              │ │              │ │              │           │
│           │ Copy of data │ │ Copy of data │ │ Copy of data │           │
│           └──────────────┘ └──────────────┘ └──────────────┘           │
│                                                                         │
│   Total: 1 Master + 3 Replicas = 4 copies of same data                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Write Operation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WRITE OPERATION IN REPLICATION                       │
│                                                                         │
│   Step 1: Client sends WRITE command                                   │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│       ┌──────────────┐                                                 │
│       │  App Server  │                                                 │
│       │              │                                                 │
│       │  SET user:1  │                                                 │
│       │  "John"      │                                                 │
│       └──────┬───────┘                                                 │
│              │                                                          │
│              │  WRITE always goes to MASTER                            │
│              ▼                                                          │
│       ┌─────────────────────────────────┐                              │
│       │           MASTER                │                              │
│       │                                 │                              │
│       │  1. Receive SET user:1 "John"  │                              │
│       │  2. Execute command            │                              │
│       │  3. Store in memory            │                              │
│       │  4. Return OK to client        │ ──────► OK (immediate)       │
│       │  5. Queue for replication      │                              │
│       │                                 │                              │
│       └──────────────┬──────────────────┘                              │
│                      │                                                  │
│   ═══════════════════════════════════════════════════════════════════  │
│   Step 2: Async Replication (happens in background)                    │
│   ═══════════════════════════════════════════════════════════════════  │
│                      │                                                  │
│                      │  Replication Stream:                            │
│                      │  ┌─────────────────────────────┐                │
│                      │  │ SET user:1 "John"           │                │
│                      │  └─────────────────────────────┘                │
│                      │                                                  │
│         ┌────────────┼────────────┐                                    │
│         │            │            │                                     │
│         ▼            ▼            ▼                                     │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐                              │
│    │REPLICA 1│  │REPLICA 2│  │REPLICA 3│                              │
│    │         │  │         │  │         │                              │
│    │ Apply   │  │ Apply   │  │ Apply   │                              │
│    │ SET cmd │  │ SET cmd │  │ SET cmd │                              │
│    │         │  │         │  │         │                              │
│    └─────────┘  └─────────┘  └─────────┘                              │
│                                                                         │
│   Note: Client gets response BEFORE replication completes              │
│         (Async = eventual consistency)                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Read Operation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    READ OPERATION IN REPLICATION                        │
│                                                                         │
│   Multiple App Servers making READ requests:                           │
│                                                                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│   │ App 1   │  │ App 2   │  │ App 3   │  │ App 4   │                  │
│   │         │  │         │  │         │  │         │                  │
│   │GET user │  │GET user │  │GET user │  │GET user │                  │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                  │
│        │            │            │            │                         │
│        │            │            │            │                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   Load Balancer distributes READs across all nodes:                    │
│   ═══════════════════════════════════════════════════════════════════  │
│        │            │            │            │                         │
│        ▼            ▼            ▼            ▼                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│   │ MASTER  │  │REPLICA 1│  │REPLICA 2│  │REPLICA 3│                  │
│   │         │  │         │  │         │  │         │                  │
│   │ "John"  │  │ "John"  │  │ "John"  │  │ "John"  │                  │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘                  │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   RESULT: 4x READ throughput! 🚀                                       │
│                                                                         │
│   • 1 Master = 100K reads/sec                                          │
│   • 1 Master + 3 Replicas = 400K reads/sec                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Failover Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FAILOVER IN REPLICATION                              │
│                                                                         │
│   BEFORE: Master is healthy                                            │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│              ┌─────────────┐                                           │
│              │   MASTER    │ ◀── All writes here                       │
│              │  (healthy)  │                                           │
│              └──────┬──────┘                                           │
│                     │                                                   │
│         ┌───────────┼───────────┐                                      │
│         ▼           ▼           ▼                                       │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐                                │
│    │REPLICA 1│ │REPLICA 2│ │REPLICA 3│                                │
│    └─────────┘ └─────────┘ └─────────┘                                │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   DISASTER: Master goes down!                                          │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│              ┌─────────────┐                                           │
│              │   MASTER    │                                           │
│              │     💀      │ ◀── CRASHED!                              │
│              │   (down)    │                                           │
│              └─────────────┘                                           │
│                                                                         │
│         ┌─────────┐ ┌─────────┐ ┌─────────┐                           │
│         │REPLICA 1│ │REPLICA 2│ │REPLICA 3│                           │
│         │         │ │         │ │         │                           │
│         │ "I have │ │ "I have │ │ "I have │                           │
│         │  data!" │ │  data!" │ │  data!" │                           │
│         └─────────┘ └─────────┘ └─────────┘                           │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   AFTER: Replica promoted to Master (Manual or via Sentinel)          │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│              ┌─────────────┐                                           │
│              │   REPLICA 1 │                                           │
│              │     NOW     │ ◀── PROMOTED TO MASTER!                   │
│              │   MASTER    │                                           │
│              └──────┬──────┘                                           │
│                     │                                                   │
│              ┌──────┴──────┐                                           │
│              ▼             ▼                                            │
│         ┌─────────┐  ┌─────────┐                                      │
│         │REPLICA 2│  │REPLICA 3│                                      │
│         │   now   │  │   now   │                                      │
│         │follows  │  │follows  │                                      │
│         │new master│ │new master│                                     │
│         └─────────┘  └─────────┘                                      │
│                                                                         │
│   SERVICE RESTORED! ✅                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Sharding (Redis Cluster)

Sharding provides **Write Scaling** and **Horizontal Data Distribution**.

### Basic Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      REDIS CLUSTER (SHARDING)                           │
│                                                                         │
│   Data is distributed across shards using 16,384 HASH SLOTS            │
│                                                                         │
│   ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐   │
│   │      SHARD 1      │ │      SHARD 2      │ │      SHARD 3      │   │
│   │     (Master)      │ │     (Master)      │ │     (Master)      │   │
│   │                   │ │                   │ │                   │   │
│   │  Slots: 0 - 5460  │ │ Slots: 5461-10922 │ │ Slots: 10923-16383│   │
│   │                   │ │                   │ │                   │   │
│   │  ~33% of keys     │ │  ~33% of keys     │ │  ~33% of keys     │   │
│   │                   │ │                   │ │                   │   │
│   │  ✅ READ/WRITE    │ │  ✅ READ/WRITE    │ │  ✅ READ/WRITE    │   │
│   │  (for its keys)   │ │  (for its keys)   │  (for its keys)   │   │
│   │                   │ │                   │ │                   │   │
│   │  Memory: 32GB     │ │  Memory: 32GB     │ │  Memory: 32GB     │   │
│   └───────────────────┘ └───────────────────┘ └───────────────────┘   │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   BENEFITS:                                                            │
│   • Total Memory: 32GB × 3 = 96GB (linear scaling!)                   │
│   • Write Throughput: 100K × 3 = 300K ops/sec                         │
│   • Each shard is independent                                          │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key → Slot → Shard Mapping

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HOW KEYS ARE DISTRIBUTED                             │
│                                                                         │
│   Step 1: Calculate hash slot for key                                  │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│       SLOT = CRC16(key) mod 16384                                      │
│                                                                         │
│       Examples:                                                         │
│       ┌──────────────────┬─────────────────┬────────────────┐          │
│       │       Key        │  CRC16 mod 16384│     Slot       │          │
│       ├──────────────────┼─────────────────┼────────────────┤          │
│       │  "user:100"      │      2345       │     2345       │          │
│       │  "user:200"      │      7890       │     7890       │          │
│       │  "order:500"     │     12456       │    12456       │          │
│       │  "cart:789"      │      4521       │     4521       │          │
│       │  "session:abc"   │     15000       │    15000       │          │
│       └──────────────────┴─────────────────┴────────────────┘          │
│                                                                         │
│   Step 2: Find shard that owns the slot                                │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│       ┌──────────────────────────────────────────────────────────┐     │
│       │                    SLOT RANGES                           │     │
│       │                                                          │     │
│       │   0 ─────── 5460 ─────── 10922 ─────── 16383            │     │
│       │   │         │            │              │                │     │
│       │   │ SHARD 1 │  SHARD 2   │   SHARD 3    │                │     │
│       │   │         │            │              │                │     │
│       └──────────────────────────────────────────────────────────┘     │
│                                                                         │
│       Mapping result:                                                   │
│       ┌──────────────────┬────────────┬─────────────────┐              │
│       │       Key        │    Slot    │     Shard       │              │
│       ├──────────────────┼────────────┼─────────────────┤              │
│       │  "user:100"      │    2345    │    SHARD 1      │              │
│       │  "user:200"      │    7890    │    SHARD 2      │              │
│       │  "order:500"     │   12456    │    SHARD 3      │              │
│       │  "cart:789"      │    4521    │    SHARD 1      │              │
│       │  "session:abc"   │   15000    │    SHARD 3      │              │
│       └──────────────────┴────────────┴─────────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Write Operation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WRITE OPERATION IN CLUSTER                           │
│                                                                         │
│   Client wants to: SET user:200 "John"                                 │
│                                                                         │
│   ┌──────────────┐                                                     │
│   │  App Server  │                                                     │
│   │              │                                                     │
│   │ SET user:200 │                                                     │
│   │   "John"     │                                                     │
│   └──────┬───────┘                                                     │
│          │                                                              │
│          │  Step 1: Calculate slot                                     │
│          │  SLOT = CRC16("user:200") mod 16384 = 7890                  │
│          │                                                              │
│          │  Step 2: Slot 7890 is in range 5461-10922                   │
│          │  → Route to SHARD 2                                         │
│          │                                                              │
│          │                              ┌────────────────┐             │
│          │                              │                │             │
│          └──────────────────────────────┤    SHARD 2     │             │
│                                         │                │             │
│   ┌──────────┐        ┌──────────┐     │   ✅ Execute   │             │
│   │ SHARD 1  │        │ SHARD 3  │     │   SET user:200 │             │
│   │          │        │          │     │   "John"       │             │
│   │  (not    │        │  (not    │     │                │             │
│   │  involved)│       │  involved)│    │   Return: OK   │             │
│   │          │        │          │     │                │             │
│   └──────────┘        └──────────┘     └───────┬────────┘             │
│                                                 │                       │
│                                                 │  Response             │
│                                                 ▼                       │
│                                          ┌──────────────┐              │
│                                          │  App Server  │              │
│                                          │     OK ✓     │              │
│                                          └──────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Read Operation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    READ OPERATION IN CLUSTER                            │
│                                                                         │
│   Multiple READ requests for different keys:                           │
│                                                                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│   │   App 1     │  │   App 2     │  │   App 3     │                   │
│   │             │  │             │  │             │                   │
│   │GET user:100 │  │GET user:200 │  │GET order:500│                   │
│   │ (slot 2345) │  │ (slot 7890) │  │(slot 12456) │                   │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                   │
│          │                │                │                           │
│          │                │                │                           │
│   ═══════════════════════════════════════════════════════════════════  │
│   Each request routed to correct shard based on slot:                  │
│   ═══════════════════════════════════════════════════════════════════  │
│          │                │                │                           │
│          ▼                ▼                ▼                           │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│   │   SHARD 1    │ │   SHARD 2    │ │   SHARD 3    │                  │
│   │              │ │              │ │              │                  │
│   │ Slots 0-5460 │ │Slots 5461-   │ │Slots 10923-  │                  │
│   │              │ │      10922   │ │      16383   │                  │
│   │              │ │              │ │              │                  │
│   │ GET user:100 │ │ GET user:200 │ │GET order:500 │                  │
│   │    ✅        │ │    ✅        │ │    ✅        │                  │
│   │              │ │              │ │              │                  │
│   └──────────────┘ └──────────────┘ └──────────────┘                  │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   All 3 shards work IN PARALLEL = 3x throughput!                       │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### MOVED Redirection (Wrong Shard)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MOVED REDIRECTION                                    │
│                                                                         │
│   Scenario: Client doesn't know cluster topology yet                   │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   ┌──────────────┐                                                     │
│   │  App Server  │                                                     │
│   │              │                                                     │
│   │ GET user:200 │  (Client connects to random node)                   │
│   └──────┬───────┘                                                     │
│          │                                                              │
│          │  Connects to Shard 1 (wrong shard!)                         │
│          ▼                                                              │
│   ┌──────────────┐                                                     │
│   │   SHARD 1    │                                                     │
│   │              │                                                     │
│   │ "I don't own │                                                     │
│   │  slot 7890!" │                                                     │
│   │              │                                                     │
│   │ MOVED 7890   │ ◀── Tells client where to go                       │
│   │ 192.168.1.2  │                                                     │
│   │ :6379        │                                                     │
│   └──────────────┘                                                     │
│          │                                                              │
│          │  Client redirected                                          │
│          ▼                                                              │
│   ┌──────────────┐                                                     │
│   │   SHARD 2    │                                                     │
│   │ 192.168.1.2  │                                                     │
│   │              │                                                     │
│   │ "Yes, I own  │                                                     │
│   │  slot 7890!" │                                                     │
│   │              │                                                     │
│   │ → "John"     │ ◀── Returns actual data                            │
│   └──────────────┘                                                     │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   Smart clients CACHE this mapping to avoid future redirects           │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Replication + Sharding (Production Setup)

This is the **recommended production setup** combining both strategies.

### Complete Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│           REDIS CLUSTER WITH REPLICATION (PRODUCTION SETUP)             │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                         SHARD 1                                  │  │
│   │                    (Slots 0 - 5460)                             │  │
│   │                                                                  │  │
│   │        ┌─────────────────────┐                                  │  │
│   │        │       MASTER        │ ◀── WRITES go here               │  │
│   │        │     192.168.1.1     │                                  │  │
│   │        │                     │                                  │  │
│   │        └──────────┬──────────┘                                  │  │
│   │                   │ replication                                 │  │
│   │                   ▼                                              │  │
│   │        ┌─────────────────────┐                                  │  │
│   │        │       REPLICA       │ ◀── READS can go here            │  │
│   │        │     192.168.1.4     │     (load balance)               │  │
│   │        │    (auto failover)  │                                  │  │
│   │        └─────────────────────┘                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                         SHARD 2                                  │  │
│   │                   (Slots 5461 - 10922)                          │  │
│   │                                                                  │  │
│   │        ┌─────────────────────┐                                  │  │
│   │        │       MASTER        │ ◀── WRITES go here               │  │
│   │        │     192.168.1.2     │                                  │  │
│   │        │                     │                                  │  │
│   │        └──────────┬──────────┘                                  │  │
│   │                   │ replication                                 │  │
│   │                   ▼                                              │  │
│   │        ┌─────────────────────┐                                  │  │
│   │        │       REPLICA       │ ◀── READS can go here            │  │
│   │        │     192.168.1.5     │                                  │  │
│   │        │    (auto failover)  │                                  │  │
│   │        └─────────────────────┘                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                         SHARD 3                                  │  │
│   │                  (Slots 10923 - 16383)                          │  │
│   │                                                                  │  │
│   │        ┌─────────────────────┐                                  │  │
│   │        │       MASTER        │ ◀── WRITES go here               │  │
│   │        │     192.168.1.3     │                                  │  │
│   │        │                     │                                  │  │
│   │        └──────────┬──────────┘                                  │  │
│   │                   │ replication                                 │  │
│   │                   ▼                                              │  │
│   │        ┌─────────────────────┐                                  │  │
│   │        │       REPLICA       │ ◀── READS can go here            │  │
│   │        │     192.168.1.6     │                                  │  │
│   │        │    (auto failover)  │                                  │  │
│   │        └─────────────────────┘                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   TOTAL: 6 Redis nodes (3 Masters + 3 Replicas)                        │
│                                                                         │
│   BENEFITS:                                                            │
│   ✅ Write Scaling: 3 masters = 3x write throughput                   │
│   ✅ Read Scaling: 6 nodes = 6x read throughput                       │
│   ✅ High Availability: Auto failover if master dies                  │
│   ✅ Data Capacity: 3 shards = 3x storage                             │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Complete Write Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│             WRITE FLOW IN CLUSTER + REPLICATION                         │
│                                                                         │
│   Client: SET order:500 "Pizza"                                        │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   ┌──────────────────┐                                                 │
│   │    App Server    │                                                 │
│   │                  │                                                 │
│   │ SET order:500    │                                                 │
│   │    "Pizza"       │                                                 │
│   └────────┬─────────┘                                                 │
│            │                                                            │
│            │  Step 1: Calculate slot                                   │
│            │  SLOT = CRC16("order:500") mod 16384 = 12456              │
│            │  Slot 12456 → SHARD 3                                     │
│            │                                                            │
│            │  Step 2: Route to SHARD 3 MASTER (not replica!)           │
│            │                                                            │
│            └──────────────────────────────────────────┐                │
│                                                       │                 │
│   ┌─────────────────┐  ┌─────────────────┐           │                 │
│   │     SHARD 1     │  │     SHARD 2     │           │                 │
│   │                 │  │                 │           │                 │
│   │ Master  Replica │  │ Master  Replica │           │                 │
│   │   │       │     │  │   │       │     │           │                 │
│   │   └───────┘     │  │   └───────┘     │           ▼                 │
│   │    (idle)       │  │    (idle)       │  ┌─────────────────┐        │
│   └─────────────────┘  └─────────────────┘  │     SHARD 3     │        │
│                                              │                 │        │
│                                              │ ┌─────────────┐ │        │
│                                              │ │   MASTER    │◀┘ WRITE │
│                                              │ │             │         │
│                                              │ │ 1. Execute  │         │
│                                              │ │ 2. Return OK│──► App  │
│                                              │ │ 3. Replicate│         │
│                                              │ └──────┬──────┘         │
│                                              │        │                │
│                                              │        │ async          │
│                                              │        ▼                │
│                                              │ ┌─────────────┐         │
│                                              │ │   REPLICA   │         │
│                                              │ │             │         │
│                                              │ │ Apply SET   │         │
│                                              │ └─────────────┘         │
│                                              │                 │        │
│                                              └─────────────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Complete Read Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│              READ FLOW IN CLUSTER + REPLICATION                         │
│                                                                         │
│   Multiple clients reading different keys:                             │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐                     │
│   │  Client 1 │    │  Client 2 │    │  Client 3 │                     │
│   │           │    │           │    │           │                     │
│   │GET user:1 │    │GET user:2 │    │GET order:5│                     │
│   │(slot 1234)│    │(slot 7890)│    │(slot 12456│                     │
│   └─────┬─────┘    └─────┬─────┘    └─────┬─────┘                     │
│         │                │                │                            │
│         │                │                │                            │
│   ═══════════════════════════════════════════════════════════════════  │
│   With read_from_replicas=True, reads are load balanced:              │
│   ═══════════════════════════════════════════════════════════════════  │
│         │                │                │                            │
│         ▼                ▼                ▼                            │
│   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐               │
│   │    SHARD 1    │ │    SHARD 2    │ │    SHARD 3    │               │
│   │               │ │               │ │               │               │
│   │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │               │
│   │ │  MASTER   │ │ │ │  MASTER   │ │ │ │  MASTER   │ │               │
│   │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │               │
│   │       │       │ │       │       │ │       │       │               │
│   │ ┌─────┴─────┐ │ │ ┌─────┴─────┐ │ │ ┌─────┴─────┐ │               │
│   │ │  REPLICA  │◀┤ │ │  REPLICA  │◀┤ │ │  REPLICA  │◀┤               │
│   │ │   READ ✓  │ │ │ │   READ ✓  │ │ │ │   READ ✓  │ │               │
│   │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │               │
│   └───────────────┘ └───────────────┘ └───────────────┘               │
│                                                                         │
│   RESULT:                                                              │
│   • Reads distributed across ALL 6 nodes                               │
│   • Masters handle writes + some reads                                 │
│   • Replicas handle reads + provide failover                          │
│   • Maximum throughput achieved! 🚀                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Automatic Failover

```
┌─────────────────────────────────────────────────────────────────────────┐
│              AUTOMATIC FAILOVER IN CLUSTER                              │
│                                                                         │
│   BEFORE: All nodes healthy                                            │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   SHARD 1              SHARD 2              SHARD 3                    │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐                │
│   │  MASTER  │        │  MASTER  │        │  MASTER  │                │
│   │    ✓     │        │    ✓     │        │    ✓     │                │
│   └────┬─────┘        └────┬─────┘        └────┬─────┘                │
│        │                   │                   │                       │
│   ┌────┴─────┐        ┌────┴─────┐        ┌────┴─────┐                │
│   │ REPLICA  │        │ REPLICA  │        │ REPLICA  │                │
│   │    ✓     │        │    ✓     │        │    ✓     │                │
│   └──────────┘        └──────────┘        └──────────┘                │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   DISASTER: Shard 2 Master crashes!                                    │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   SHARD 1              SHARD 2              SHARD 3                    │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐                │
│   │  MASTER  │        │  MASTER  │        │  MASTER  │                │
│   │    ✓     │        │    💀    │        │    ✓     │                │
│   └────┬─────┘        └────┬─────┘        └────┬─────┘                │
│        │                   │                   │                       │
│   ┌────┴─────┐        ┌────┴─────┐        ┌────┴─────┐                │
│   │ REPLICA  │        │ REPLICA  │        │ REPLICA  │                │
│   │    ✓     │        │  "I'm    │        │    ✓     │                │
│   └──────────┘        │  alive!" │        └──────────┘                │
│                       └──────────┘                                     │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│   AUTOMATIC RECOVERY (within seconds):                                 │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   SHARD 1              SHARD 2              SHARD 3                    │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐                │
│   │  MASTER  │        │   NEW    │        │  MASTER  │                │
│   │    ✓     │        │  MASTER  │        │    ✓     │                │
│   └────┬─────┘        │ (was     │        └────┬─────┘                │
│        │              │ replica) │             │                       │
│   ┌────┴─────┐        │    ✓     │        ┌────┴─────┐                │
│   │ REPLICA  │        └──────────┘        │ REPLICA  │                │
│   │    ✓     │                            │    ✓     │                │
│   └──────────┘        Old master can      └──────────┘                │
│                       rejoin as replica                                │
│                       when it comes back                               │
│                                                                         │
│   SERVICE CONTINUES WITHOUT INTERRUPTION! ✅                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference Summary

| Setup | Write Scaling | Read Scaling | High Availability | Use Case |
|-------|---------------|--------------|-------------------|----------|
| **Single Redis** | ❌ 1x | ❌ 1x | ❌ None | Development |
| **Replication** | ❌ 1x | ✅ Nx | ✅ Manual failover | Read-heavy apps |
| **Sharding** | ✅ Nx | ⚠️ Nx | ❌ No redundancy | Write-heavy apps |
| **Sharding + Replication** | ✅ Nx | ✅ 2Nx | ✅ Auto failover | **Production** |

---

## Python Client Example

```python
from redis.cluster import RedisCluster

# Connect to cluster (auto-discovers all nodes)
rc = RedisCluster(
    host="192.168.1.1",
    port=6379,
    read_from_replicas=True  # Enable read scaling
)

# Client automatically routes to correct shard
rc.set("user:123", "John")      # → Routes to correct master
rc.get("user:123")              # → Can read from master or replica
rc.set("order:456", "Pizza")    # → Routes to different shard

# All routing is handled automatically!
```

---

*Document created for interview preparation and system design understanding.*

