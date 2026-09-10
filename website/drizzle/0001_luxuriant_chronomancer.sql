CREATE TABLE `news_review_decisions` (
	`item_id` text PRIMARY KEY NOT NULL,
	`version_id` text NOT NULL,
	`run_id` text NOT NULL,
	`status` text NOT NULL,
	`revision` integer NOT NULL,
	`note` text NOT NULL,
	`ranking_json` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `news_review_events` (
	`event_id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`item_id` text NOT NULL,
	`version_id` text NOT NULL,
	`run_id` text NOT NULL,
	`status` text NOT NULL,
	`revision` integer NOT NULL,
	`note` text NOT NULL,
	`ranking_json` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `news_review_event_item_revision` ON `news_review_events` (`item_id`,`revision`);--> statement-breakpoint
CREATE TABLE `news_review_sessions` (
	`session_hash` text PRIMARY KEY NOT NULL,
	`expires_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `news_review_session_expiry` ON `news_review_sessions` (`expires_at`);
--> statement-breakpoint
-- Append-only decision history is recorded atomically with each successful save.
CREATE TRIGGER news_review_decision_insert AFTER INSERT ON news_review_decisions BEGIN
  INSERT INTO news_review_events(item_id,version_id,run_id,status,revision,note,ranking_json,updated_at)
  VALUES (NEW.item_id,NEW.version_id,NEW.run_id,NEW.status,NEW.revision,NEW.note,NEW.ranking_json,NEW.updated_at);
END;
--> statement-breakpoint
CREATE TRIGGER news_review_decision_update AFTER UPDATE ON news_review_decisions BEGIN
  INSERT INTO news_review_events(item_id,version_id,run_id,status,revision,note,ranking_json,updated_at)
  VALUES (NEW.item_id,NEW.version_id,NEW.run_id,NEW.status,NEW.revision,NEW.note,NEW.ranking_json,NEW.updated_at);
END;
