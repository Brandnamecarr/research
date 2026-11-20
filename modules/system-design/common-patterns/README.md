# System design: common patterns

> Most systems are assembled from a small set of recurring problems. Recognise the problem, and you can reach for a known solution and its known failure modes instead of designing from scratch.

Source: summarised and paraphrased from Hello Interview, [System Design in a Hurry: Common Patterns](https://www.hellointerview.com/learn/system-design/in-a-hurry/patterns). Links back to the DSA modules are added where a pattern rests on a structure covered there.

## Why patterns matter

Knowing the building blocks (databases, caches, queues, blob stores) is not enough under time pressure. The faster skill is spotting that "users bidding on the same item" is a **contention** problem, or that "upload a 2 GB video" is a **large blob** problem. Each pattern brings a default solution, a list of trade-offs, and the questions an interviewer is likely to ask.

Patterns are not exclusive. A real design usually combines three or four of them.

| # | Pattern | The problem in one line | Default starting point |
|---|---|---|---|
| 1 | Realtime updates | Clients need to hear about changes as they happen | Polling, then SSE or WebSockets |
| 2 | Long-running tasks | Work takes too long to do inside a request | Queue + worker pool, **return a job ID** |
| 3 | Contention | Many users want the same resource at once | <ul><li>Let one database handle it</li><li>Atomic: check & change in one `UPDATE ... WHERE left > 0`</li><li>Lock: safe but slow</li><li>Version check: retry if someone beat you</li><li>Ticketmaster: hold seat, then sell. "Seat hold is one conditional UPDATE with expiry. Zero rows means someone beat you."</li></ul> |
| 4 | Scaling reads | Read traffic outgrows the database | Indexes → read replicas → cache / CDN |
| 5 | Scaling writes | Write throughput outgrows one server | Sharding with a good partition key, plus batching and buffering |
| 6 | Large blobs | Big files clog the application servers | Presigned URLs straight to object storage, CDN for downloads |
| 7 | Multi-step processes | A workflow spans services and must survive failures | Workflow engine / durable execution |
| 8 | Proximity search | "Find things near me" | Geospatial index (PostGIS, Redis geo, Elasticsearch) |

---

## 1. Pushing realtime updates

**Problem.** Chat messages, notifications, live dashboards, collaborative editing. The server knows something changed and the client needs to find out without asking.

**How it works.** There are two decisions.

1. **How the client hears about it (the protocol).**
   - **Polling**: the client asks "anything new?" every few seconds. Simplest to build and operate. Wastes requests when nothing has changed and adds up to one interval of latency.
   - **Server-Sent Events (SSE)**: one long-lived HTTP response that the server keeps writing to. One-way, server to client.
   - **WebSockets**: a persistent two-way connection. Lowest latency, but load balancers, reconnects and connection state make the infrastructure harder.

2. **How the update reaches the right server (the topology).** With persistent connections, the user is attached to *one* specific server, and the event may be produced on another.
   - **Pub/Sub** (e.g. Redis Pub/Sub, Kafka): servers subscribe to topics for the users they hold. Publishers don't need to know where anyone is connected. A good fit for chat.
   - **Stateful servers with consistent hashing**: each document or room is owned by one server, so all its clients connect there and that server holds the live state. A good fit when per-session processing is heavy, as in collaborative editing.

**Default.** Start with polling. Move to SSE or WebSockets only when the latency or request volume of polling is a stated problem.

---

## 2. Managing long-running tasks

**Problem.** Video transcoding, report generation, bulk imports: anything that takes more than a few seconds. Holding an HTTP request open that long ties up servers and fails badly on timeouts.

**How it works.**

```
client ──request──> web server ──enqueue──> queue (Redis, Kafka, SQS) ──> worker pool
   <── job ID (ms) ──┘                                                       │
client ──poll / subscribe for status──────────────────────── status store <──┘
```

The web server validates the request, enqueues a job and returns a job ID immediately. Workers pull jobs and do the work. You get fast responses, web and worker tiers that scale independently, and a crashed job that can't take down the API.

**What you must handle.**
- Job status tracking, so the client can poll (or be pushed to, via pattern 1).
- Retries, which means jobs should be idempotent.
- Poison messages: a job that always fails goes to a **dead-letter queue** instead of retrying forever.

**Pitfall.** Reaching for a queue too early. If the work finishes in a second or two, doing it synchronously is simpler, gives natural back-pressure, and gives the user a clearer result.

---

## 3. Dealing with contention

**Problem.** The last concert ticket, the final seconds of an auction, two people booking the same hotel room. Concurrent writes to the same data must not produce double bookings or lost updates.

**Solutions, in the order to consider them.**

1. **Inside one database** (it was built to solve this):
   - *Pessimistic locking*: `SELECT ... FOR UPDATE` holds the row while you work. Safe, but serialises access.
   - *Optimistic concurrency control*: read a version number, write only `WHERE version = ?`, retry on conflict. Cheap when conflicts are rare.
   - *Transactions and atomic operations*: `UPDATE seats SET available = available - 1 WHERE available > 0`.
2. **Across systems**, only when the data genuinely can't live in one place:
   - Distributed locks (e.g. Redis with a TTL).
   - Two-phase commit across databases.
   - Queue-based serialisation: send all requests for a resource through one queue partition so they are processed one at a time.

**Trade-off.** Stronger consistency costs throughput, and distributed coordination costs a lot of complexity.

**Pitfall.** Splitting data across databases too early. Every guarantee the single database gave you for free (atomicity, isolation, locking) now has to be rebuilt by hand. Interviewers often probe exactly this.

---

## 4. Scaling reads

**Problem.** Reads are usually the first bottleneck. Read-to-write ratios start around 10:1 and often reach 100:1 or more. Opening a photo feed triggers hundreds of reads, while the same user might post once a day.

**Progression.** Each step is more powerful and more complex than the last:

1. **Optimise the database.** Add the right indexes (a B+ tree per index, see [Module 3](../../03-trees/README.md)). Denormalise hot paths so one read replaces a join.
2. **Read replicas.** Copy the database to more servers and spread reads across them.
3. **Caching.** An in-memory cache such as Redis in front of the database (an LRU cache, see [Module 2](../../02-linear-structures/README.md)), and a CDN in front of static and cacheable content.

**What interviewers ask about.**
- **Cache invalidation**: how stale data gets evicted or updated when the source changes.
- **Replication lag**: a user writes, then reads from a replica that hasn't caught up and doesn't see their own change. A common fix is routing a user's reads to the primary for a short time after they write.
- **Hot keys**: one celebrity post or viral item can overload a single cache node. Fixes include replicating that key or adding a small local cache on each app server.

---

## 5. Scaling writes

**Problem.** Writes can't be cached away. At high volume, a single database's disk and CPU become the hard limit.

**Strategies.**
- **Horizontal sharding**: split rows across servers by a partition key.
- **Vertical partitioning**: put different kinds of data (users, messages, analytics) in different stores.
- **Write queues**: absorb bursts and let the database drain them at a steady rate.
- **Load shedding**: under overload, drop or defer low-value writes (such as view counts) to protect important ones (such as payments).
- **Batching**: group many small writes into one to amortise per-write overhead.

**The key decision: the partition key.** It should spread load evenly *and* keep data that is queried together on the same shard.
- `user_id` for a chat app: each user's data stays together, and load spreads across many users.
- `created_date`: today's shard takes every write while the rest sit idle. This is the same "sequential keys hit one page" problem as B-tree inserts, at cluster scale.

---

## 6. Handling large blobs

**Problem.** Routing a 2 GB video through your application servers wastes their bandwidth and memory and makes them a bottleneck.

**How it works.**

```
upload:    client ──"I want to upload"──> app server ──presigned URL──> client
           client ─────────────── file ──────────────────────────────> object storage (S3)
           object storage ──"upload complete" event──> app server (update metadata)

download:  client ──> CDN (signed URL) ──cache miss──> object storage
```

The app server never touches the bytes. It hands out **presigned URLs**: short-lived URLs scoped to one object and one operation. Clients upload directly to object storage, and downloads go through a CDN with signed URLs for access control. Object stores also support resumable multipart uploads, progress tracking and global distribution.

**Challenges.**
- **Keeping metadata in sync.** The database row says "uploading" but is the file actually there? Use the storage's event notifications to mark uploads complete, rather than trusting the client to report back.
- **Failed and abandoned uploads**, which need cleanup.
- **Lifecycle**: expiring, archiving or moving old files to cheaper storage tiers.

For a step-by-step walkthrough of presigned uploads and downloads, see [long-blob-supplemental.md](../long-blob-supplemental.md).

---

## 7. Multi-step processes

**Problem.** Order fulfilment (charge card → reserve stock → ship → notify), user onboarding, payment flows. Steps span services, may take minutes or days, and any of them can fail. Partial completion must never leave the system in a broken state.

**Spectrum of solutions.**
- **Single-server orchestration**: one service calls each step in turn and tracks progress in a database. Fine for simple flows, but you write all the retry and recovery logic yourself.
- **Event sourcing / choreography**: each step emits an event that triggers the next. No central coordinator, but the overall flow is hard to see and debug.
- **Workflow engines / durable execution** (Temporal, AWS Step Functions): you write the workflow as ordinary-looking code or a state machine. The engine persists progress after every step, retries failures, resumes after crashes, and keeps a full history.

**Core idea.** Replace state scattered across services and hand-written error handling with one declarative workflow definition, and let the engine provide the reliability guarantees and the audit trail.

---

## 8. Proximity-based services

**Problem.** "Drivers near this rider", "stores that deliver to this address". You need to query by location efficiently.

**How it works.** A **geospatial index** divides the map into regions (geohashes, quadtrees, S2 cells) and indexes each entity by its region. A query only examines regions near the search point and skips the rest of the map. A geohash is a prefix code: nearby points usually share a prefix, which is the same idea as the trie in [Module 3](../../03-trees/README.md).

Off-the-shelf options:
- PostgreSQL with **PostGIS**
- **Redis** geospatial commands (`GEOADD`, `GEOSEARCH`)
- **Elasticsearch** geo queries

**Pitfalls.**
- Don't add a geo index too early. With around a thousand entities, scanning them all is cheaper. The index pays off at hundreds of thousands to millions.
- Queries are almost always local. Nobody asks for "the nearest driver on Earth", so you can often shard by city or region as well.

---

## Choosing and combining patterns

A video platform shows how the patterns stack up:

| Step | Pattern |
|---|---|
| User uploads a large video file | Large blobs (presigned upload) |
| Video is transcoded into several resolutions | Long-running tasks (queue + workers) |
| User sees "processing... 60%" | Realtime updates |
| Upload → transcode → thumbnail → publish → notify, surviving failures | Multi-step processes |
| Millions of viewers | Scaling reads (CDN) |

Guidelines:
- **Start simple.** Polling before WebSockets, one database before distributed locks, synchronous before queued, a full scan before a geo index. Add complexity only when a stated requirement forces it, and say which requirement it is.
- **Name the pattern out loud.** "This is a contention problem, so first I'll lean on the database" tells an interviewer you recognise the shape of the problem and keeps the discussion on the decisions that matter.
- **Know the failure modes.** Each pattern has two or three standard follow-up questions (cache invalidation, replication lag, hot keys, poison messages, metadata sync). Have an answer ready before you're asked.
