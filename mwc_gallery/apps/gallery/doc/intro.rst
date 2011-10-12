========
Overview
========

This app allows for integrating a gallery into your application.  For these purposes, a gallery is a collection of user-uploaded media with a name and description.  It allows creating, editing, and deleting galleries.

Galleries can be created using 2 methods: a standard HTML form, or a Flash-based uploader.

============
Dependencies
============

Major libraries and apps that gallery depends on:

        * mimesis (specifically, MWC's mwc-thumbnail-property branch)
        * mimesis-mediaman
        * django-uploadify
          
----------------------------
Special Note on Flash Uploads
----------------------------

Currently, django-uploadify does **not** ship with the uploadify static files.  These are installed at the project level right now.
