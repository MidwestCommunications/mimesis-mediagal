ALTER TABLE "gallery_gallery" ADD COLUMN "sites" integer REFERENCES "django_site" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "gallery_gallery" ADD COLUMN "cover_id" integer REFERENCES "mimesis_mediaupload" ("id") DEFERRABLE INITIALLY DEFERRED;
