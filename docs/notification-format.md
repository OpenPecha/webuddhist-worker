# Push Notification Format

This document describes the push notification payload sent by the WebBuddhist worker to mobile devices. Use it when implementing notification handling, deep linking, or routing in the frontend app.

## Overview

The worker sends notifications via **Firebase Cloud Messaging (FCM)** for both Android and iOS.

Each push includes:

1. A **display notification** (`title` + `body`) shown in the system tray.
2. A **data payload** with routine session metadata the app can use for navigation.

## Push Payload

```json
{
  "notification": {
    "title": "Day 1",
    "body": "Begin practice."
  },
  "data": {
    "session_type": "PLAN",
    "source_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Display notification

| Field   | Type   | Description                          |
|---------|--------|--------------------------------------|
| `title` | string | Notification title shown to the user |
| `body`  | string | Notification body shown to the user  |

### Data payload

All data values are **strings** (FCM requirement).

| Field          | Type   | Description |
|----------------|--------|-------------|
| `session_type` | string | Type of routine session (see [Session types](#session-types)) |
| `source_id`    | string | UUID of the related entity (plan, series, collection, etc.). Empty string (`""`) when there is no linked entity |

## Session types

| `session_type`           | `source_id` refers to      |
|--------------------------|----------------------------|
| `PLAN`                   | Plan UUID                  |
| `SERIES`                 | Series UUID                |
| `RECITATION`             | Recitation UUID (if set)   |
| `RECITATION_COLLECTION`  | Recitation collection UUID |
| `ACCUMULATION`           | Accumulation UUID (if set) |
| `TIMER`                  | Empty string               |

## Default content

When no custom content is configured:

| Field   | Default value                    |
|---------|----------------------------------|
| `title` | `WebBuddhist`                    |
| `body`  | `Time for your daily practice.`  |

## How title and body are resolved

### Routine notifications (time-block based)

Triggered when a user's routine time block matches the current local time.

| Session type              | Title                         | Body                          |
|---------------------------|-------------------------------|-------------------------------|
| `PLAN`                    | Day notification title from DB | Day notification body from DB |
| `SERIES`                  | Series metadata title         | Default body                  |
| `RECITATION_COLLECTION`   | Collection name               | Default body                  |
| `RECITATION`              | Default title                 | Default body                  |
| `ACCUMULATION`            | Default title                 | Default body                  |
| `TIMER`                   | Default title                 | Default body                  |

For `PLAN`, the worker calculates the user's current day from plan progress and loads that day's notification copy from the database.

### Plan reminders (enrollment API)

Used when the app enrolls reminders via `POST /api/v1/notifications/reminders`.

Body resolution priority:

1. `routine.message_template` (if set)
2. `"Time for {plan_name}"` (if `plan_name` is set)
3. `"Day {current_day_number}: time for your practice."` (if `current_day_number` is set)
4. Default body

Data payload for plan reminders:

```json
{
  "session_type": "PLAN",
  "source_id": "<plan_id>"
}
```

## Reading the payload in the app

### Flutter (`firebase_messaging`)

```dart
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  final title = message.notification?.title;
  final body = message.notification?.body;

  final sessionType = message.data['session_type'];
  final sourceId = message.data['source_id'];

  // Parse sourceId as UUID when non-empty
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
    val title = remoteMessage.notification?.title
    val body = remoteMessage.notification?.body

    val sessionType = remoteMessage.data["session_type"]
    val sourceId = remoteMessage.data["source_id"]
}
```

### iOS (Firebase Messaging)

When the user taps a notification, read the data keys from the FCM payload:

```swift
let sessionType = userInfo["session_type"] as? String
let sourceId = userInfo["source_id"] as? String
```

## Foreground vs background

| App state              | Behavior |
|------------------------|----------|
| Background or killed   | OS shows the notification using `title` and `body` |
| Foreground             | App receives the message in the FCM handler; show UI manually if needed |

The `data` payload is available in both cases. Use it to route the user when they tap the notification.

## Example payloads

### Plan session

```json
{
  "notification": {
    "title": "Day 3 — Breath Awareness",
    "body": "Take 10 minutes for today's practice."
  },
  "data": {
    "session_type": "PLAN",
    "source_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Series session

```json
{
  "notification": {
    "title": "Morning Teachings",
    "body": "Time for your daily practice."
  },
  "data": {
    "session_type": "SERIES",
    "source_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
  }
}
```

### Timer session (no linked entity)

```json
{
  "notification": {
    "title": "WebBuddhist",
    "body": "Time for your daily practice."
  },
  "data": {
    "session_type": "TIMER",
    "source_id": ""
  }
}
```

### Accumulation session

```json
{
  "notification": {
    "title": "WebBuddhist",
    "body": "Time for your daily practice."
  },
  "data": {
    "session_type": "ACCUMULATION",
    "source_id": "c3d4e5f6-a7b8-9012-cdef-123456789012"
  }
}
```

## What is not included in the push

These fields exist server-side but are **not** sent to the device:

- `custom_image_url`
- `source_image_url`
- `user_id`
- Deep link URL

Images and rich notification content are not part of the current push payload.

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
2. If `source_id` is empty, open the app's default home or practice screen.
3. Otherwise, navigate to the screen for that session type and entity ID:

| `session_type`          | Suggested route        |
|-------------------------|------------------------|
| `PLAN`                  | Plan detail / day view |
| `SERIES`                | Series player          |
| `RECITATION`            | Recitation view        |
| `RECITATION_COLLECTION` | Collection view        |
| `ACCUMULATION`          | Accumulation view      |
| `TIMER`                 | Timer screen           |
