CREATE TABLE `news_research_jobs` (
	`job_id` text PRIMARY KEY NOT NULL,
	`item_id` text NOT NULL,
	`version_id` text NOT NULL,
	`run_id` text NOT NULL,
	`decision_revision` integer NOT NULL,
	`attempt` integer NOT NULL,
	`status` text NOT NULL,
	`lease` text NOT NULL,
	`started_at` text NOT NULL,
	`finished_at` text,
	`model` text NOT NULL,
	`result_json` text,
	`error` text
);
--> statement-breakpoint
CREATE UNIQUE INDEX `news_research_version_attempt` ON `news_research_jobs` (`version_id`,`attempt`);--> statement-breakpoint
CREATE INDEX `news_research_started` ON `news_research_jobs` (`started_at`);--> statement-breakpoint
CREATE TABLE `news_research_runner` (
	`id` integer PRIMARY KEY NOT NULL,
	`status` text NOT NULL,
	`checked_at` text NOT NULL,
	`model` text NOT NULL
);
