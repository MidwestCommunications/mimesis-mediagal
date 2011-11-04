### New Model: easy_thumbnails.Source
CREATE TABLE "easy_thumbnails_source" (
    "id" serial NOT NULL PRIMARY KEY,
    "storage_hash" varchar(40) NOT NULL,
    "name" varchar(255) NOT NULL,
    "modified" timestamp with time zone NOT NULL,
    UNIQUE ("storage_hash", "name")
)
;
### New Model: easy_thumbnails.Thumbnail
CREATE TABLE "easy_thumbnails_thumbnail" (
    "id" serial NOT NULL PRIMARY KEY,
    "storage_hash" varchar(40) NOT NULL,
    "name" varchar(255) NOT NULL,
    "modified" timestamp with time zone NOT NULL,
    "source_id" integer NOT NULL REFERENCES "easy_thumbnails_source" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("storage_hash", "name")
)
;
CREATE INDEX "easy_thumbnails_source_storage_hash" ON "easy_thumbnails_source" ("storage_hash");
CREATE INDEX "easy_thumbnails_source_storage_hash_like" ON "easy_thumbnails_source" ("storage_hash" varchar_pattern_ops);
CREATE INDEX "easy_thumbnails_source_name" ON "easy_thumbnails_source" ("name");
CREATE INDEX "easy_thumbnails_source_name_like" ON "easy_thumbnails_source" ("name" varchar_pattern_ops);
CREATE INDEX "easy_thumbnails_thumbnail_storage_hash" ON "easy_thumbnails_thumbnail" ("storage_hash");
CREATE INDEX "easy_thumbnails_thumbnail_storage_hash_like" ON "easy_thumbnails_thumbnail" ("storage_hash" varchar_pattern_ops);
CREATE INDEX "easy_thumbnails_thumbnail_name" ON "easy_thumbnails_thumbnail" ("name");
CREATE INDEX "easy_thumbnails_thumbnail_name_like" ON "easy_thumbnails_thumbnail" ("name" varchar_pattern_ops);
CREATE INDEX "easy_thumbnails_thumbnail_source_id" ON "easy_thumbnails_thumbnail" ("source_id");
