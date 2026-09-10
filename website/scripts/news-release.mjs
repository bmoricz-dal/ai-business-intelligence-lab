export function requireNewsDatabaseId(value) {
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value ?? '') || value === '00000000-0000-4000-8000-000000000000') {
    throw new Error('Set DAL_NEWS_DATABASE_ID to the verified production DAL News database before releasing. The local placeholder must never be deployed.');
  }
  return value;
}

export function validateNewsSecrets(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('News secrets file must be a JSON object.');
  if (Object.keys(value).some(key => !['NEWS_INGEST_TOKEN', 'NEWS_EDITOR_TOKEN', 'NEWS_REVIEW_TOKEN'].includes(key))) throw new Error('News secrets file contains an unknown credential.');
  const { NEWS_INGEST_TOKEN, NEWS_EDITOR_TOKEN } = value;
  if (typeof NEWS_INGEST_TOKEN !== 'string' || NEWS_INGEST_TOKEN.length < 32 || typeof NEWS_EDITOR_TOKEN !== 'string' || NEWS_EDITOR_TOKEN.length < 32 || NEWS_INGEST_TOKEN === NEWS_EDITOR_TOKEN) {
    throw new Error('Use separate random ingestion and editorial secrets of at least 32 characters.');
  }
  if (value.NEWS_REVIEW_TOKEN !== undefined && (typeof value.NEWS_REVIEW_TOKEN !== 'string' || value.NEWS_REVIEW_TOKEN.length < 32 || [NEWS_INGEST_TOKEN, NEWS_EDITOR_TOKEN].includes(value.NEWS_REVIEW_TOKEN))) {
    throw new Error('Use a separate random review secret of at least 32 characters.');
  }
}
