import { index, integer, primaryKey, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

export const newsSourceState = sqliteTable("news_source_state", {
  sourceId: text("source_id").primaryKey(), lastSuccess: text("last_success").notNull(),
});
export const newsIdentities = sqliteTable("news_identities", {
  alias: text("alias").primaryKey(), itemId: text("item_id").notNull(),
}, t => [index("news_identities_item").on(t.itemId)]);
export const newsVersions = sqliteTable("news_versions", {
  versionId: text("version_id").primaryKey(), itemId: text("item_id").notNull(),
  contentHash: text("content_hash").notNull(), payload: text("payload").notNull(), collectedAt: text("collected_at").notNull(),
}, t => [index("news_versions_collected").on(t.collectedAt), index("news_versions_item").on(t.itemId)]);
export const newsObservations = sqliteTable("news_observations", {
  itemId: text("item_id").notNull(), sourceId: text("source_id").notNull(), sourceGuid: text("source_guid").notNull(), sourceUrl: text("source_url").notNull(),
}, t => [primaryKey({ columns: [t.itemId, t.sourceId, t.sourceGuid] })]);
export const newsPackItems = sqliteTable("news_pack_items", {
  packDate: text("pack_date").notNull(), itemId: text("item_id").notNull(), versionId: text("version_id").notNull(),
}, t => [primaryKey({ columns: [t.packDate, t.itemId] })]);
export const newsRuns = sqliteTable("news_collection_runs", {
  runId: text("run_id").primaryKey(), packDate: text("pack_date").notNull(), startedAt: text("started_at").notNull(),
  status: text("status").notNull(), transportHash: text("transport_hash").notNull(), payload: text("payload").notNull(),
});
export const newsDailyPacks = sqliteTable("news_daily_packs", {
  packDate: text("pack_date").primaryKey(), runId: text("run_id").notNull(),
});
export const newsGenerations = sqliteTable("news_ingest_generations", {
  generation: integer("generation").primaryKey(), runId: text("run_id").notNull(),
});
export const newsEditions = sqliteTable("news_editions", {
  editionDate: text("edition_date").primaryKey(), draftJson: text("draft_json").notNull(), revision: integer("revision").notNull(),
  approvedRevision: integer("approved_revision"), approvedBy: text("approved_by"), approvedAt: text("approved_at"),
  publishedJson: text("published_json"), publishedRevision: integer("published_revision"), publishedAt: text("published_at"),
});

export const newsReviewSessions = sqliteTable("news_review_sessions", {
  sessionHash: text("session_hash").primaryKey(), expiresAt: text("expires_at").notNull(),
}, t => [index("news_review_session_expiry").on(t.expiresAt)]);
export const newsReviewDecisions = sqliteTable("news_review_decisions", {
  itemId: text("item_id").primaryKey(), versionId: text("version_id").notNull(), runId: text("run_id").notNull(),
  status: text("status").notNull(), revision: integer("revision").notNull(), note: text("note").notNull(),
  rankingJson: text("ranking_json").notNull(), updatedAt: text("updated_at").notNull(),
});
export const newsReviewEvents = sqliteTable("news_review_events", {
  eventId: integer("event_id").primaryKey({ autoIncrement: true }), itemId: text("item_id").notNull(),
  versionId: text("version_id").notNull(), runId: text("run_id").notNull(), status: text("status").notNull(),
  revision: integer("revision").notNull(), note: text("note").notNull(), rankingJson: text("ranking_json").notNull(), updatedAt: text("updated_at").notNull(),
}, t => [index("news_review_event_item_revision").on(t.itemId, t.revision)]);

export const newsResearchJobs = sqliteTable("news_research_jobs", {
  jobId: text("job_id").primaryKey(), itemId: text("item_id").notNull(), versionId: text("version_id").notNull(),
  runId: text("run_id").notNull(), decisionRevision: integer("decision_revision").notNull(),
  attempt: integer("attempt").notNull(), status: text("status").notNull(), lease: text("lease").notNull(),
  startedAt: text("started_at").notNull(), finishedAt: text("finished_at"),
  model: text("model").notNull(), resultJson: text("result_json"), error: text("error"),
}, t => [uniqueIndex("news_research_version_attempt").on(t.versionId, t.attempt), index("news_research_started").on(t.startedAt)]);
export const newsResearchRunner = sqliteTable("news_research_runner", {
  id: integer("id").primaryKey(), status: text("status").notNull(), checkedAt: text("checked_at").notNull(), model: text("model").notNull(),
});
