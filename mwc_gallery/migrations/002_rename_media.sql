### New Model: gallery.GalleryMedia
CREATE TABLE "gallery_gallerymedia" (
    "id" serial NOT NULL PRIMARY KEY,
    "gallery_id" integer NOT NULL REFERENCES "gallery_gallery" ("id") DEFERRABLE INITIALLY DEFERRED,
    "media_id" integer NOT NULL REFERENCES "mimesis_mediaupload" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE INDEX "gallery_gallerymedia_gallery_id" ON "gallery_gallerymedia" ("gallery_id");
CREATE INDEX "gallery_gallerymedia_media_id" ON "gallery_gallerymedia" ("media_id");
