# Large blobs: how presigned URLs work

Supplement to [Common patterns, section 6: Handling large blobs](common-patterns/README.md#6-handling-large-blobs).

## The idea

The application server and the object store (for example S3) share a secret key. The server uses that key to **sign** a URL. The signature says: *this one object, this one operation, until this time.* The client presents the URL to the object store, which checks the signature and lets the request through only if it is valid.

The result is that the application server decides who may upload or download, but the file's bytes never pass through it.

## What a presigned URL looks like

```
https://bucket.s3.amazonaws.com/videos/abc.mp4
  ?X-Amz-Expires=900          ← valid for 15 minutes
  &X-Amz-Signature=9f3e...    ← proof the server approved this request
```

The signature covers the bucket, the object key, the HTTP method and the expiry time. If the client changes any of them, such as a different filename or a later expiry, the signature no longer matches and the store rejects the request. The client can use the URL but cannot change what it allows.

## Upload flow

```
client ──"I want to upload"──> app server ──(check auth, create DB row)
client <──── presigned PUT URL ───┘
client ──────────── file bytes ──────────────> object storage
object storage ──"upload complete" event──> app server ──(mark row done)
```

1. The client tells the app server it wants to upload a file.
2. The server checks the user is allowed to. It creates a metadata row in the database with `status = uploading`.
3. The server signs a PUT URL and returns it to the client.
4. The client uploads the file directly to the object store using that URL.
5. The object store emits an event when the upload completes. The server receives it and sets `status = done`.

Generating the URL with boto3:

```python
url = s3.generate_presigned_url(
    "put_object",
    Params={"Bucket": "videos", "Key": "abc.mp4"},
    ExpiresIn=900,  # seconds
)
```

### Multipart uploads for big files

For large files, use a multipart upload. The file is split into chunks, and each chunk gets its own presigned URL. If a chunk fails, only that chunk is resent, so uploads can be resumed after a dropped connection instead of starting over. Chunks can also upload in parallel, and the client can show progress as each one finishes.

## Download flow

```
client ──"I want video abc"──> app server ──(check auth)
client <──── signed GET URL (CDN) ─┘
client ──> CDN ──cache hit──> bytes
            └──cache miss──> object storage ──> CDN keeps a copy ──> bytes
```

1. The client asks the app server for a file.
2. The server checks the user is allowed to see it.
3. The server signs a short-lived GET URL that points at the CDN.
4. The client fetches the file from the CDN. If the CDN has a cached copy it serves it from a nearby edge location. If not, it fetches the file from object storage, caches it, and serves it.

## Why this works well

- **App servers stay small and fast.** They handle small JSON requests, not multi-gigabyte streams.
- **Object stores and CDNs are built for this.** They scale bandwidth and storage without any work from you.
- **Leaks are contained.** A URL expires in minutes and grants access to one object for one operation.

## Things to watch out for

- **Trust the storage event, not the client.** A client can crash mid-upload or claim it finished when it didn't. Mark an upload complete only when the object store confirms it.
- **Clean up abandoned uploads.** Uploads that start and never finish leave `uploading` rows in the database and orphaned chunks in storage. Run a periodic cleanup, and use the store's lifecycle rules to abort incomplete multipart uploads.
- **Keep expiry short.** Long-lived URLs behave like public links if they are shared or leaked.
