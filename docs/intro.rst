========
Overview
========

This app allows for integrating a gallery into your application.  For these purposes, a gallery is a collection of user-uploaded media with a name and description.  It allows creating, editing, and deleting galleries.

Galleries are created or updating by uploading a zip archive containing the photos that should be in gallery.

============
Dependencies
============

Major libraries and apps that gallery depends on:

        * mimesis (specifically, MWC's mwc-thumbnail-property branch)
        * mimesis-mediaman
        * easy_thumbnails (which requires PIL)
        * django-endless-pagination

========
Settings
========

**PAGINATE_COUNT**: An integer setting the amount of items to be used per "page" in endless-pagination