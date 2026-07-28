-- D-008-approved G4-03 long analytical schema for SQLite.
-- This file creates empty tables only; it does not promote or load data.

PRAGMA foreign_keys = ON;

CREATE TABLE dataset_releases (
    source_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    publisher TEXT NOT NULL,
    title TEXT NOT NULL,
    publication_date TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    source_url TEXT NOT NULL,
    licence TEXT NOT NULL,
    release_status TEXT NOT NULL CHECK (
        release_status IN (
            'registered',
            'accepted_for_schema_design',
            'approved_processed',
            'retired'
        )
    ),
    CHECK (length(trim(source_id)) > 0),
    CHECK (length(trim(dataset_id)) > 0),
    CHECK (length(trim(dataset_version)) > 0),
    CHECK (period_start <= period_end),
    PRIMARY KEY (source_id, dataset_id, dataset_version)
) STRICT;

CREATE TABLE indicators (
    indicator_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    definition TEXT NOT NULL,
    preferred_unit TEXT NOT NULL CHECK (
        preferred_unit IN ('proportion', 'count', 'rate', 'index', 'currency')
    ),
    CHECK (length(trim(indicator_id)) > 0),
    CHECK (length(trim(label)) > 0),
    CHECK (length(trim(definition)) > 0),
    UNIQUE (indicator_id, preferred_unit)
) STRICT;

CREATE TABLE denominators (
    denominator_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    definition TEXT NOT NULL,
    CHECK (length(trim(denominator_id)) > 0),
    CHECK (length(trim(label)) > 0),
    CHECK (length(trim(definition)) > 0)
) STRICT;

CREATE TABLE pipeline_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    code_path TEXT NOT NULL,
    code_sha256 TEXT NOT NULL CHECK (length(code_sha256) = 64),
    metadata_path TEXT NOT NULL,
    output_path TEXT NOT NULL,
    output_sha256 TEXT NOT NULL CHECK (length(output_sha256) = 64),
    validation_result TEXT NOT NULL CHECK (
        validation_result IN ('passed', 'failed')
    ),
    approval_status TEXT NOT NULL CHECK (
        approval_status IN (
            'unreviewed_interim',
            'accepted_for_schema_design',
            'approved_processed',
            'approved_for_analysis',
            'approved_for_publication'
        )
    ),
    CHECK (started_at <= completed_at)
) STRICT;

CREATE TABLE observations (
    observation_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    source_table_id TEXT NOT NULL,
    source_question_id TEXT NOT NULL,
    indicator_id TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    population_label TEXT NOT NULL,
    denominator_id TEXT NOT NULL,
    unit TEXT NOT NULL CHECK (
        unit IN ('proportion', 'count', 'rate', 'index', 'currency')
    ),
    dimension_type TEXT NOT NULL,
    dimension_value TEXT NOT NULL,
    source_dimension_label TEXT NOT NULL,
    scope_role TEXT NOT NULL CHECK (
        scope_role IN (
            'primary',
            'reference_benchmark',
            'reconciliation_comparator',
            'context'
        )
    ),
    estimate REAL,
    lower_limit REAL,
    upper_limit REAL,
    confidence_level REAL,
    sample_base INTEGER,
    source_status TEXT NOT NULL CHECK (
        source_status IN (
            'observed',
            'suppressed_c',
            'not_asked_z',
            'missing',
            'unknown'
        )
    ),
    run_id TEXT NOT NULL,
    approval_status TEXT NOT NULL CHECK (
        approval_status IN (
            'unreviewed_interim',
            'accepted_for_schema_design',
            'approved_processed',
            'approved_for_analysis',
            'approved_for_publication'
        )
    ),
    notes TEXT NOT NULL DEFAULT '',
    CHECK (length(trim(observation_id)) > 0),
    CHECK (length(trim(source_table_id)) > 0),
    CHECK (length(trim(source_question_id)) > 0),
    CHECK (length(trim(population_label)) > 0),
    CHECK (length(trim(dimension_type)) > 0),
    CHECK (length(trim(dimension_value)) > 0),
    CHECK (length(trim(source_dimension_label)) > 0),
    CHECK (period_start <= period_end),
    CHECK (sample_base IS NULL OR sample_base > 0),
    CHECK (
        source_status = 'observed'
        OR (
            estimate IS NULL
            AND lower_limit IS NULL
            AND upper_limit IS NULL
            AND confidence_level IS NULL
        )
    ),
    CHECK (source_status <> 'observed' OR estimate IS NOT NULL),
    CHECK (
        unit <> 'proportion'
        OR estimate IS NULL
        OR estimate BETWEEN 0.0 AND 1.0
    ),
    CHECK (
        unit <> 'proportion'
        OR lower_limit IS NULL
        OR lower_limit BETWEEN 0.0 AND 1.0
    ),
    CHECK (
        unit <> 'proportion'
        OR upper_limit IS NULL
        OR upper_limit BETWEEN 0.0 AND 1.0
    ),
    CHECK (
        (
            lower_limit IS NULL
            AND upper_limit IS NULL
            AND confidence_level IS NULL
        )
        OR (
            lower_limit IS NOT NULL
            AND upper_limit IS NOT NULL
            AND confidence_level IS NOT NULL
            AND confidence_level > 0.0
            AND confidence_level <= 1.0
            AND estimate IS NOT NULL
            AND lower_limit <= estimate
            AND estimate <= upper_limit
        )
    ),
    FOREIGN KEY (source_id, dataset_id, dataset_version)
        REFERENCES dataset_releases (source_id, dataset_id, dataset_version),
    FOREIGN KEY (indicator_id, unit)
        REFERENCES indicators (indicator_id, preferred_unit),
    FOREIGN KEY (denominator_id) REFERENCES denominators (denominator_id),
    FOREIGN KEY (run_id) REFERENCES pipeline_runs (run_id),
    UNIQUE (
        source_id,
        dataset_id,
        dataset_version,
        source_table_id,
        source_question_id,
        indicator_id,
        period_start,
        period_end,
        denominator_id,
        dimension_type,
        dimension_value
    )
) STRICT;

CREATE INDEX observations_lookup_idx ON observations (
    indicator_id,
    period_end,
    dimension_type,
    dimension_value,
    approval_status
);
