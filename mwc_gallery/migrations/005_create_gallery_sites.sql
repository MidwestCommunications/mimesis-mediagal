### New Model: gallery.GallerySites
CREATE TABLE "gallery_gallerysites" (
    "id" serial NOT NULL PRIMARY KEY,
    "gallery_id" integer NOT NULL REFERENCES "gallery_gallery" ("id") DEFERRABLE INITIALLY DEFERRED,
    "site_id" integer NOT NULL REFERENCES "django_site" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE INDEX "gallery_gallerysites_gallery_id" ON "gallery_gallerysites" ("gallery_id");
CREATE INDEX "gallery_gallerysites_site_id" ON "gallery_gallerysites" ("site_id");
