var MEDIAMAN = {

addAutoTag: function (sourceField, tagField) {
    var src = document.id(sourceField),
        dest = document.id(tagField);
    src.addEvent('change', function () {
        var tagRequest = new Request({
                url: '/mediaman/filter_tags/',
                method: 'get',
                data: {'s': src.get('value')}
            });
        tagRequest.addEvent('success', function (verifiedTags) {
            dest.set('value', verifiedTags);
        });
        tagRequest.send();
    });
},

MediaSelector: new Class({
    initialize: function (container, form, options) {
        var attachedFieldValue,
            options = options || {};
        this.container = document.id(container);
        this.form = document.id(form);
        this.model = options.model;
        this.tagField = document.id(options.tagField);
        this.attachedIdsField = this.form.getElement('input#id_mimesis_attached_media');
        attachedFieldValue = this.attachedIdsField.get('value');
        this.attachedIds = (attachedFieldValue && attachedFieldValue.split(',')) || [];
        this.addFormSubmitEvent();
        this.loadSelector(attachedFieldValue);
    },
    addFormSubmitEvent: function () {
        this.form.addEvent('submit', function () {
            var checkedItems = this.container.getElements('input[name="primary_media"]').filter(function (listItem) {
                    return listItem.get('checked');
                }),
                primaryId;
            if (checkedItems.length) {
                primaryId = checkedItems.shift().get('value');
                this.attachedIds.erase(primaryId).unshift(primaryId);
            }
            this.attachedIdsField.set('value', this.attachedIds.join());
            return true;
        }.bind(this));
    },
    loadSelector: function (attachedValue) {
        var selectorRequest = new Request.HTML({
                url: '/mediaman/mediaselector/',
                method: 'get',
                update: this.container,
                data: {
                    model: this.model,
                    media: attachedValue,
                    searchtags: this.tagField && this.tagField.get('value')
                }
            });
        selectorRequest.addEvent('complete', this.loadedSelector.bind(this));
        selectorRequest.send();
    },
    loadedSelector: function () {
        this.selectContainer = this.container.getElement('div.selectcontainer');
        
        // request to submit a query and populate the list from the response
        this.searchRequest = new Request.HTML({
            url: '/mediaman/mediaselector/search/',
            method: 'get',
            update: this.selectContainer.getElement('ul.medialist')
        });
        this.searchForm = this.selectContainer.getElement('form');
        // prevent the form from being submitted normally (i.e. by enter key press)
        this.searchForm.addEvent('submit', function () {
            this.doSearch();
            // don't do a normal submission
            return false;
        }.bind(this));
        // any of the following events should submit a search query
        this.searchForm.addEvent('reset', function () {
            this.searchForm.getElement('input.search').set('value', '');
            this.doSearch();
            // don't reset the whole form
            return false;
        }.bind(this));
        this.searchForm.getElements('input[type="radio"]').addEvent('click', this.doSearch.bind(this));
        
        this.selectContainer.getElement('ul.medialist').addEvent('click', this.clickedMedia.bind(this));
        // store the content for the search tab
        this.selectContents = {search: this.selectContainer.getChildren()};
        
        this.previewContainer = this.container.getElement('div.previewcontainer');
        this.previewLoadingContents = this.previewContainer.getChildren();
        this.attachedList = this.container.getElement('div.attachedcontainer').getElement('ul.medialist');
        if (this.attachedList.getElement('li')) {
            this.attachedList.getParent().setStyle('display', 'block');
            this.attachedList.getElements('li').each(this.setupAttachedItem.bind(this));
            this.attachedList.getElement('input[name="primary_media"]').set('checked', true);
        }
        this.currentTab = 'search';
        this.container.getElement('ul.tabs').addEvent('click', this.clickedTab.bind(this));
    },
    clickedTab: function (e) {
        var target = document.id(e.target),
            uploadRequest;
        if (target.get('tag') === 'label') {
            target = target.getParent();
        }
        if (target.get('tag') !== 'li') {
            return;
        }
        if (target.hasClass('current') || this.loading) {
            return;
        }
        this.selectContainer.getElement('ul.medialist').getChildren('li.selected').removeClass('selected');
        this.previewContainer.setStyle('display', 'none');
        target.getParent().getElement('li.current').removeClass('current');
        target.addClass('current');
        // switch the currentTab name
        this.currentTab = this.currentTab === 'search' ? 'upload' : 'search';
        if (this.currentTab === 'upload') {
            if (!this.selectContents.upload) {
                // upload tab was clicked, but form has not been loaded
                // so load it
                this.selectContainer.empty();
                this.loading = true;
                uploadRequest = new Request.HTML({
                    url: '/mediaman/mediaselector/upload/',
                    method: 'get',
                    update: this.selectContainer
                });
                uploadRequest.addEvent('complete', this.loadedUploadForm.bind(this));
                uploadRequest.send();
                return;
            }
        }
        // put the content for the tab in DOM
        this.selectContainer.empty().adopt(this.selectContents[this.currentTab]);
    },
    loadedUploadForm: function () {
        var form = this.selectContainer.getElement('form'),
            uploadForm = form.getElement('div.inputgroup.upload'),
            embedForm = form.getElement('div.inputgroup.embed'),
            fileInput = form.getElement('input[type="file"]'),
            embedInput = form.getElement('input[type="text"]'),
            embedButton = form.getElement('input[type="button"]'),
            count = 0,
            frameId,
            mediaList = this.selectContainer.getElement('ul.medialist');
        // make sure the frame ID is not being used
        do {
            count += 1;
            frameId = 'mediaselector_upload_frame_' + count.toString();
        } while (document.id(frameId));
        // make an iFrame to be the target of upload form submissions
        this.uploadFrame = new IFrame({
            id: frameId,
            name: frameId,
            styles: {display: 'none'},
            events: {
                load: function () {
                    var frameElement = this.uploadFrame.contentWindow.document.body.firstChild;
                    if (frameElement) {
                        // the iFrame loaded content
                        while (!frameElement.tagName) {
                            frameElement = frameElement.nextSibling;
                        }
                        if (mediaList.getElement('li').hasClass('empty')) {
                            mediaList.empty();
                        }
                        if (document.importNode) {
                            mediaList.grab(document.importNode(frameElement, true), 'top');
                        } else {
                            mediaList.grab(frameElement.cloneNode(true), 'top');
                        }
                    }
                    fileInput.blur();
                    fileInput.set('value', '');
                    embedInput.set('value', '');
                }.bind(this)
            }
        });
        this.uploadFrame.inject(document.body);
        form.set('target', frameId);
        this.loading = false;
        // upload the file when selected
        fileInput.addEvent('change', function () {
            form.submit();
        });
        embedButton.addEvent('click', function () {
            form.submit();
        });
        
        //
        this.selectContainer.getElements('input[name="mediaman-upload-type"]').addEvent('click', function () {
            if (form.getElement('input[value="upload"]').get('checked')) {
                embedForm.setStyle('display', 'none');
                uploadForm.setStyle('display', 'block');
                return;
            }
            uploadForm.setStyle('display', 'none');
            embedForm.setStyle('display', 'block');
        });
        // add events to filter the list
        this.selectContainer.getElements('input[name="mediaman-upload-status"]').addEvent('click', function () {
            if (form.getElement('input[value="unattached"]').get('checked')) {
                // if "Unattached" is checked, hide all attached media
                mediaList.getElements('.attached').setStyle('display', 'none');
                return;
            }
            mediaList.getElements('.attached').setStyle('display', 'list-item');
        });
        // fire click event to hide already attached media
        form.getElement('input[value="unattached"]').fireEvent('click');
        this.selectContainer.getElement('ul.medialist').addEvent('click', this.clickedMedia.bind(this));
        // store the content for the upload tab
        this.selectContents.upload = this.selectContainer.getChildren();
    },
    doSearch: function () {
        // submit a search query based on the form currently
        this.searchRequest.send(this.searchForm.toQueryString());
    },
    clickedMedia: function (e) {
        var target = document.id(e.target),
            mediaId,
            editRequest,
            previewRequest;
        // list items only have direct descendents,
        // so we only have to check the parent
        if (target.get('tag') !== 'li') {
            target = target.getParent();
        }
        if (target.get('tag') !== 'li') {
            return;
        }
        if (target.hasClass('empty')) {
            return;
        }
        target.getParent().getChildren('li.selected').removeClass('selected');
        target.addClass('selected');
        mediaId = target.getElement('span.itemid').get('text');
        // if not attached, we can still edit metadata
        if (!target.hasClass('attached')) {
            this.showPreview(mediaId, true);
            return;
        }
        this.showPreview(mediaId);
    },
    showPreview: function (mediaId, edit) {
        this.previewContainer.empty().adopt(this.previewLoadingContents);
        // show the container
        this.previewContainer.setStyle('display', 'block');
        // preview/edit
        if (edit) {
            editFormRequest = new Request.HTML({
                url: '/mediaman/mediaselector/edit/' + mediaId + '/',
                method: 'get',
                update: this.previewContainer
            });
            editFormRequest.addEvent('complete', this.loadedEditForm.bind(this));
            editFormRequest.send();
            return;
        }
        // preview only, no editing
        previewRequest = new Request.HTML({
            url: '/mediaman/mediaselector/preview/' + mediaId + '/',
            method: 'get',
            update: this.previewContainer
        });
        previewRequest.addEvent('success', function () {
            this.previewContainer.getElement('input').addEvent('click', function () {
                var selectedItem;
                this.previewContainer.setStyle('display', 'none');
                selectedItem = this.selectContainer.getElement('ul.medialist').getElement('li.selected');
                this.addToAttached(selectedItem);
            }.bind(this));
        }.bind(this));
        previewRequest.send();
    },
    loadedEditForm: function () {
        var mediaId = this.previewContainer.getElement('span.itemid').get('text'),
            form = this.previewContainer.getElement('form');
        MEDIAMAN.addAutoTag('id_mediaman-caption', 'id_mediaman-tags');
        form.addEvent('submit', function () {
            var editRequest = new Request.HTML({
                url: '/mediaman/mediaselector/edit/' + mediaId + '/',
                method: 'post'
            });
            editRequest.addEvent('success', function (tree) {
                var item;
                if (tree.length > 1) {
                    item = tree[1];
                } else {
                    item = tree[0];
                }
                if (item.get) {if (item.get('tag') === 'li') {
                    this.previewContainer.setStyle('display', 'none');
                    this.addToAttached(item);
                    item.replaces(this.selectContainer.getElement('ul.medialist').getElement('li.selected'));
                    return;
                }}
                this.previewContainer.empty().adopt(tree);
                this.loadedEditForm();
            }.bind(this));
            editRequest.send(form.toQueryString());
            return false;
        }.bind(this));
    },
    addToAttached: function (item) {
        var mediaId = item.getElement('span.itemid').get('text'),
            itemToAttach = item.clone().removeClass('selected'),
            attachedContainer;
        this.setupAttachedItem(itemToAttach);
        if (this.attachedIds.contains(mediaId)) {
            itemToAttach.replaces(this.attachedList.getElements('span.itemid').filter(function (span) {
                return span.get('text') === mediaId;
            }).shift().getParent());
            return;
        }
        this.attachedIds.push(mediaId);
        itemToAttach.inject(this.attachedList);
        this.attachedList.getParent().setStyle('display', 'block');
    },
    setupAttachedItem: function (listItem) {
        var itemId = listItem.getElement('span.itemid').get('text');
        listItem.grab(
            new Element('div', {
                'class': 'primary-selector',
                'text': 'Primary'
            }).grab(
                new Element('input', {
                    'type': 'radio',
                    'name': 'primary_media',
                    'value': itemId
                })
            )
        );
        listItem.grab(new Element('input', {
            'type': 'button',
            'value': 'x',
            'events': {
                'click': function () {
                    this.attachedIds.erase(itemId);
                    listItem.destroy();
                    if (!this.attachedIds.length) {
                        this.attachedList.getParent().setStyle('display', 'none');
                    }
                }.bind(this)
            }
        }));
    }
})

};
