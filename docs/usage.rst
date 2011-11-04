=====
Usage
=====

The gallery app consists of 3 components:
	
	* Models
	* Views
	* Template tags

Models
======

The models should be usable without any work on your part.  A ``Gallery`` can consist of any mimesis ``MediaUpload`` model, which in turn can be any type of uploaded file.

Views
=====

Template Tags
=============

The gallery app provides a ``render_media`` template tag that allows you to include a media object within a subtemplate corresponding to its media type.  You can customize these templates by altering the following template files:

	* templates/gallery/_base_display.html - The base template that all subtemplates should extend
	* templates/gallery/_(typename)_display.html - Template matching your media type.  For exmaple, "_image_display.html" would be used for images, "_video_display.html" for videos.
