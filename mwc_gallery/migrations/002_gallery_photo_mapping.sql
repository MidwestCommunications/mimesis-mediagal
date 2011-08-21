### New Model: gallery.GalleryPhotos
CREATE TABLE "gallery_galleryphotos" (
    "id" serial NOT NULL PRIMARY KEY,
    "gallery_id" integer NOT NULL REFERENCES "gallery_gallery" ("id") DEFERRABLE INITIALLY DEFERRED,
    "photo_id" integer NOT NULL REFERENCES "mimesis_mediaupload" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE INDEX "gallery_galleryphotos_gallery_id" ON "gallery_galleryphotos" ("gallery_id");
CREATE INDEX "gallery_galleryphotos_photo_id" ON "gallery_galleryphotos" ("photo_id");
