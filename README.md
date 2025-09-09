# E-ink Display Server Project

## Overview


This project implements a Django-based server to manage and serve content to Raspberry Pi Zero 2 W devices equipped with e-ink displays. The system supports content updates, device authentication, and remote control via button presses.


## Architecture


The project follows a client-server architecture:


*   **Server**: A Django application with a REST API built using Django REST Framework (DRF). It manages display states, pre-rendered images, job scheduling, and device authentication. (This repository)
*   **Client**: Raspberry Pi Zero 2 W devices with e-ink displays that poll the server for updates and send button press events. (Link to this repo will follow)


## Key Components


1.  **Networking & Discovery**
    *   UDP broadcast for device discovery: Devices send `EINK_DISCOVER` requests, and the server responds with a bootstrap URL.
    *   (Optional) mDNS/zeroconf for discovery.

2.  **Authentication & Security**
    *   DRF TokenAuthentication for device authentication.
    *   Each device has a unique `User` and `Token`.
    *   Bootstrap endpoint to provision new devices.
    *   HTTPS for all communication.


3.  **API Endpoints**
    *   `GET /api/display/state`: Returns the current display state (mode, version, image URL, refresh intervals). Supports `If-None-Match` for efficient updates.
    *   `GET /api/display/image?version=...`: Streams the image file. Supports conditional GET with `ETag`.
    *   `POST /api/display/button`: Handles button press events and sets temporary overrides.

4.  **Rendering & Files**
    *   Images are pre-rendered and served via `FileResponse`.
    *   Atomic writes to ensure image consistency.

5.  **Scheduling & Daemon**
    *   A single Django management command runs three async tasks:
        *   UDP discovery server.
        *   Stats collector (using `psutil`).
        *   Job scheduler/executor (using `croniter`).
    *   Time utilities for accurate scheduling (using `timezone.now()` and `timezone.localtime()`).
    *   Database hygiene (closing old connections and offloading ORM operations).

6.  **Jobs System**
    *   `Job` model to persist job definitions.
    *   `Execution` model to track job execution status.
    *   Cron-based job scheduling.
    *   Single-runner policy to prevent concurrent job executions.
    *   Logging to the database, associated with job executions.

7.  **Photos / Variant Selection**
    *   Weighted random selection of image variants using PostgreSQL's with a scoring algorithm.

8.  **IDs & Bootstrap Payload**
    *   Human-readable display IDs.
    *   Bootstrap response includes the display ID, token, and current mode.

# Testing

```
python manage.py job "classify" --params-json "{\"max_num_to_classify\":1}"
python manage.py job "generate_variants" --params-json "{\"max_amount\":1}"
```

