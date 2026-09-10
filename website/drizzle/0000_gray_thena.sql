CREATE TABLE `news_daily_packs` (
	`pack_date` text PRIMARY KEY NOT NULL,
	`run_id` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `news_editions` (
	`edition_date` text PRIMARY KEY NOT NULL,
	`draft_json` text NOT NULL,
	`revision` integer NOT NULL,
	`approved_revision` integer,
	`approved_by` text,
	`approved_at` text,
	`published_json` text,
	`published_revision` integer,
	`published_at` text
);
--> statement-breakpoint
CREATE TABLE `news_ingest_generations` (
	`generation` integer PRIMARY KEY NOT NULL,
	`run_id` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `news_identities` (
	`alias` text PRIMARY KEY NOT NULL,
	`item_id` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `news_identities_item` ON `news_identities` (`item_id`);--> statement-breakpoint
CREATE TABLE `news_observations` (
	`item_id` text NOT NULL,
	`source_id` text NOT NULL,
	`source_guid` text NOT NULL,
	`source_url` text NOT NULL,
	PRIMARY KEY(`item_id`, `source_id`, `source_guid`)
);
--> statement-breakpoint
CREATE TABLE `news_pack_items` (
	`pack_date` text NOT NULL,
	`item_id` text NOT NULL,
	`version_id` text NOT NULL,
	PRIMARY KEY(`pack_date`, `item_id`)
);
--> statement-breakpoint
CREATE TABLE `news_collection_runs` (
	`run_id` text PRIMARY KEY NOT NULL,
	`pack_date` text NOT NULL,
	`started_at` text NOT NULL,
	`status` text NOT NULL,
	`transport_hash` text NOT NULL,
	`payload` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `news_source_state` (
	`source_id` text PRIMARY KEY NOT NULL,
	`last_success` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `news_versions` (
	`version_id` text PRIMARY KEY NOT NULL,
	`item_id` text NOT NULL,
	`content_hash` text NOT NULL,
	`payload` text NOT NULL,
	`collected_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `news_versions_collected` ON `news_versions` (`collected_at`);--> statement-breakpoint
CREATE INDEX `news_versions_item` ON `news_versions` (`item_id`);