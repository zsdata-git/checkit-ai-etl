CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT,
    title TEXT NOT NULL,
    text TEXT,
    image_url TEXT,
    image_path TEXT,
    article_url TEXT,
    published_at TIMESTAMP,
    language TEXT,
    label INTEGER,
    original_label TEXT,
    label_status TEXT,
    modality TEXT,

    CONSTRAINT valid_label
        CHECK (label IN (0, 1) OR label IS NULL)
);