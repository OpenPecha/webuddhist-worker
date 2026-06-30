# Push Notification Format

This document describes the push notification payload sent by the WebBuddhist worker to mobile devices. Use it when implementing notification handling, deep linking, or routing in the frontend app.

## Overview

The worker sends notifications via **Firebase Cloud Messaging (FCM)** for both Android and iOS.

Each push includes:

1. A **display notification** (`title`, `body`, and optional `image`) shown in the system tray.
2. A **data payload** with routing metadata plus the resolved notification content (`title`, `body`, `image_url`).

## Push Payload

```json
{
  "notification": {
    "title": "Day 3 — Breath Awareness",
    "body": "Take 10 minutes for today's practice.",
    "image": "https://cdn.example.com/plans/cover.jpg"
  },
  "data": {
    "session_type": "PLAN",
    "source_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Day 3 — Breath Awareness",
    "body": "Take 10 minutes for today's practice.",
    "image_url": "https://cdn.example.com/plans/cover.jpg"
  }
}
```

### Display notification

| Field   | Type   | Description |
|---------|--------|-------------|
| `title` | string | Notification title shown to the user |
| `body`  | string | Notification body shown to the user |
| `image` | string | Optional image URL for rich notifications (Android and supported iOS setups). Omitted when no image is resolved. |

### Data payload

All data values are **strings** (FCM requirement).

| Field          | Type   | Description |
|----------------|--------|-------------|
| `session_type` | string | Type of routine session (see [Session types](#session-types)) |
| `source_id`    | string | UUID of the related entity (plan or series). Empty string (`""`) when there is no linked entity |
| `title`        | string | Resolved notification title (same value as the display notification) |
| `body`         | string | Resolved notification body (same value as the display notification) |
| `image_url`    | string | Presigned HTTPS URL for the notification image. Empty string (`""`) when no image is resolved |

The app can read routing fields (`session_type`, `source_id`) and content fields (`title`, `body`, `image_url`) from `message.data` in both foreground and background handlers.

## Session types

Routine notifications are sent only for **`PLAN`** and **`SERIES`** sessions.

| `session_type` | `source_id` refers to |
|----------------|------------------------|
| `PLAN`         | Plan UUID              |
| `SERIES`       | Series UUID            |

Plan reminder dispatches (enrollment API) always use `session_type: "PLAN"`.

## Default content

When no custom content is configured:

| Field   | Default value                    |
|---------|----------------------------------|
| `title` | `WebBuddhist`                    |
| `body`  | `Time for your daily practice.`  |
| `image_url` | Empty string                 |

Config keys: `NOTIFICATION_DEFAULT_TITLE`, `NOTIFICATION_DEFAULT_BODY`.

## How title, body, and image are resolved

Content is resolved by the **backend** when building routine notification targets. The worker forwards the resolved values into the FCM notification and data payload.

### Routine notifications (time-block based)

Triggered when a user's routine time block matches the current UTC minute (`routine_time_blocks.time_utc`).

| Session type | Title | Body | Image (`image_url`) |
|--------------|-------|------|---------------------|
| `PLAN`       | Day notification title from `day_notifications`, or plan title if no day copy exists | Day notification body from `day_notifications`, or default body | See [Plan image rules](#plan-image-rules) |
| `SERIES`     | Series metadata title, or default title | Default body | Series cover image (presigned), or empty string |

For `PLAN`, the backend calculates the user's current day from plan progress and loads that day's notification copy from `day_notifications` (linked to the plan item / day).

#### Plan image rules

| Condition | `image_url` |
|-----------|-------------|
| Day notification exists with `image_type = CUSTOM` | Presigned URL for `day_notifications.image_url` |
| Day notification exists with `image_type = PLAN`, or no day notification | Presigned plan cover image (`plans.image_url`) |
| No plan cover available | Empty string |

#### Series image rules

| Condition | `image_url` |
|-----------|-------------|
| Series has a cover image | Presigned series cover image (`series.image`) |
| No series cover available | Empty string |

### Plan reminders (enrollment API)

Used when the app enrolls reminders via `POST /api/v1/notifications/reminders`.

**Title/body resolution:**

1. `routine.message_template` (if set)
2. `"Time for {plan_name}"` (if `plan_name` is set)
3. `"Day {current_day_number}: time for your practice."` (if `current_day_number` is set)
4. Default title/body

**Data payload** includes `title` and `body` but not `image_url` (empty string):

```json
{
  "session_type": "PLAN",
  "source_id": "<plan_id>",
  "title": "Time for Morning Practice",
  "body": "Day 3: time for your practice.",
  "image_url": ""
}
```

## Reading the payload in the app

### Flutter (`firebase_messaging`)

```dart
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  final title = message.notification?.title ?? message.data['title'];
  final body = message.notification?.body ?? message.data['body'];
  final imageUrl = message.notification?.android?.imageUrl
      ?? message.data['image_url'];

  final sessionType = message.data['session_type'];
  final sourceId = message.data['source_id'];

  if (sourceId != null && sourceId.isNotEmpty) {
    // navigate to content for sessionType + sourceId
  }
});

FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
  final sessionType = message.data['session_type'];
  final sourceId = message.data['source_id'];
  // Handle notification tap
});
```

### Android (Firebase SDK)

```kotlin
override fun onMessageReceived(remoteMessage: RemoteMessage) {
    val title = remoteMessage.notification?.title ?: remoteMessage.data["title"]
    val body = remoteMessage.notification?.body ?: remoteMessage.data["body"]
    val imageUrl = remoteMessage.notification?.imageUrl
        ?: remoteMessage.data["image_url"]?.takeIf { it.isNotEmpty() }

    val sessionType = remoteMessage.data["session_type"]
    val sourceId = remoteMessage.data["source_id"]
}
```

### iOS (Firebase Messaging)

When the user taps a notification, read the data keys from the FCM payload:

```swift
let sessionType = userInfo["session_type"] as? String
let sourceId = userInfo["source_id"] as? String
let title = userInfo["title"] as? String
let body = userInfo["body"] as? String
let imageUrl = (userInfo["image_url"] as? String).flatMap { $0.isEmpty ? nil : $0 }
```

## Foreground vs background

| App state              | Behavior |
|------------------------|----------|
| Background or killed   | OS shows the notification using `title`, `body`, and `image` when present |
| Foreground             | App receives the message in the FCM handler; show UI manually if needed |

The `data` payload is available in both cases. Use it to route the user when they tap the notification.

## Example payloads

### Plan session (custom day notification + plan image)

```json
{
  "notification": {
    "title": "Day 3 — Breath Awareness",
    "body": "Take 10 minutes for today's practice.",
    "image": "https://cdn.example.com/plans/cover.jpg"
  },
  "data": {
    "session_type": "PLAN",
    "source_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Day 3 — Breath Awareness",
    "body": "Take 10 minutes for today's practice.",
    "image_url": "https://cdn.example.com/plans/cover.jpg"
  }
}
```

### Plan session (custom day image)

When the day notification uses `image_type = CUSTOM`, `image_url` points to the day-specific asset instead of the plan cover.

### Series session

```json
{
  "notification": {
    "title": "Morning Teachings",
    "body": "Time for your daily practice.",
    "image": "https://cdn.example.com/series/cover.jpg"
  },
  "data": {
    "session_type": "SERIES",
    "source_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "title": "Morning Teachings",
    "body": "Time for your daily practice.",
    "image_url": "https://cdn.example.com/series/cover.jpg"
  }
}
```

### Plan reminder (no image)

```json
{
  "notification": {
    "title": "Time for Morning Practice",
    "body": "Day 3: time for your practice."
  },
  "data": {
    "session_type": "PLAN",
    "source_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Time for Morning Practice",
    "body": "Day 3: time for your practice.",
    "image_url": ""
  }
}
```

## Preview API vs push payload

The backend preview endpoint (`GET /internal/routine-notification-targets`) returns additional server-side fields that are **not** sent to the device:

| Field | In preview API | In FCM push |
|-------|----------------|-------------|
| `notification.title` | Yes | Yes (`notification.title` and `data.title`) |
| `notification.body` | Yes | Yes (`notification.body` and `data.body`) |
| `notification.image_url` | Yes | Yes (`notification.image` and `data.image_url`) |
| `source_image_url` | Yes (group-level plan/series cover) | No — use `notification.image_url` per user |
| `user_id` | Yes | No |
| Deep link URL | No | No |

## Related API (enrollment only)

The worker also exposes reminder enrollment endpoints used by the app to schedule plan reminders:

| Method   | Path                                              | Purpose              |
|----------|---------------------------------------------------|----------------------|
| `POST`   | `/api/v1/notifications/reminders`                 | Enroll a reminder    |
| `PUT`    | `/api/v1/notifications/reminders/{user_id}/{plan_id}` | Update a reminder |
| `DELETE` | `/api/v1/notifications/reminders/{user_id}/{plan_id}` | Cancel a reminder |

Routine notifications are driven by routines and time blocks in the shared database (`routines`, `routine_time_blocks`, `push_device_tokens`), not by these enrollment endpoints.

## Suggested client routing

When the user taps a notification:

1. Read `session_type` and `source_id` from `message.data`.
2. Optionally use `title`, `body`, and `image_url` from `message.data` for in-app UI.
3. If `source_id` is empty, open the app's default home or practice screen.
4. Otherwise, navigate to the screen for that session type and entity ID:

| `session_type` | Suggested route        |
|----------------|------------------------|
| `PLAN`         | Plan detail / day view |
| `SERIES`       | Series player          |
