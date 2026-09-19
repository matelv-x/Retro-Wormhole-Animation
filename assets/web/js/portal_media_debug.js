(function ($) {
  'use strict';

  const API_ROOT = 'stargate';
  let library = null;
  let mode = 'wormhole';

  function label() {
    return mode === 'blackhole' ? 'Black Hole' : 'Wormhole';
  }

  function current() {
    return library && library[mode] ? library[mode] : {selected: mode + '.gif', files: [], scales: {}};
  }

  function showMessage(message, title) {
    $('<div></div>').text(message).dialog({modal: true, title: title || 'Portal Media'});
  }

  function request(path, payload) {
    return $.ajax({
      url: API_ROOT + path,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(payload || {})
    });
  }

  function applyResponse(data) {
    if (data && data.wormhole && data.blackhole) library = data;
  }

  function selectedScale() {
    const item = current();
    return parseInt(item.scales[item.selected] || 100, 10);
  }

  function refreshButtons() {
    $('.portal-media-choice').each(function () {
      const active = $(this).data('filename') === current().selected;
      $(this).css(active
        ? {'background-color': '#2980b9', color: '#fff', 'border-color': '#78dcff'}
        : {'background-color': '', color: '', 'border-color': 'transparent'});
    });
    const scale = selectedScale();
    $('#portalMediaScale').val(scale);
    $('#portalMediaScaleValue').text(scale + '%');
  }

  function selectFile(filename) {
    request('/update/portal_media', {
      media_type: mode,
      filename: filename,
      scale: parseInt(current().scales[filename] || 100, 10)
    }).done(function (data) {
      if (!data || data.success === false) {
        showMessage((data && data.message) || 'Unable to select the media file.');
        return;
      }
      applyResponse(data);
      render();
    }).fail(function () { showMessage('Unable to select the media file.'); });
  }

  function deleteFile(filename) {
    if (filename === mode + '.gif') {
      showMessage('The original ' + filename + ' is protected and cannot be deleted.');
      return;
    }
    $('<div></div>').text('Delete ' + filename + '?').dialog({
      modal: true,
      title: 'Delete ' + label() + ' media',
      buttons: {
        Delete: function () {
          const dialog = $(this);
          request('/update/delete_portal_media_asset', {media_type: mode, filename: filename})
            .done(function (data) {
              if (!data || data.success === false) {
                showMessage((data && data.message) || 'Unable to delete the media file.');
                return;
              }
              applyResponse(data);
              render();
              dialog.dialog('close');
            }).fail(function () { showMessage('Unable to delete the media file.'); });
        },
        Cancel: function () { $(this).dialog('close'); }
      }
    });
  }

  function render() {
    if (!library) return;
    const item = current();
    const choices = $('#portalMediaChoices').empty();
    item.files.forEach(function (filename) {
      const button = $('<button type="button" class="btn-secondary portal-media-choice"></button>')
        .data('filename', filename)
        .css({width: '160px', padding: '10px', border: '3px solid transparent', 'border-radius': '6px'});
      let preview;
      if (/\.(?:mp4|webm)$/i.test(filename)) {
        preview = $('<video autoplay muted loop playsinline preload="metadata"></video>')
          .attr({'src': 'retro/images/' + encodeURIComponent(filename), 'aria-label': filename + ' preview'});
      } else {
        preview = $('<img>').attr({'src': 'retro/images/' + encodeURIComponent(filename), alt: filename + ' preview'});
      }
      preview.css({display: 'block', width: '128px', height: '128px', 'object-fit': 'cover', margin: '0 auto 8px', 'border-radius': '50%'})
        .appendTo(button);
      $('<span></span>').text(filename).appendTo(button);
      button.on('click', function () {
        if ($('#portalMediaDeleteMode').is(':checked')) deleteFile(filename);
        else selectFile(filename);
      });
      button.on('contextmenu', function (event) {
        event.preventDefault();
        deleteFile(filename);
      });
      choices.append(button);
    });
    $('#portalMediaAdd').text('Add ' + label());
    $('#portalMediaProtected').text('Right-click a thumbnail to delete it. The original ' + mode + '.gif is protected.');
    const activeModeCss = {'background-color': '#2980b9', color: '#fff', 'border-color': '#78dcff'};
    const inactiveModeCss = {'background-color': '', color: '', 'border-color': ''};
    $('#portalModeWormhole').css(mode === 'wormhole' ? activeModeCss : inactiveModeCss);
    $('#portalModeBlackHole').css(mode === 'blackhole' ? activeModeCss : inactiveModeCss);
    const picker = $('#portalMediaPicker');
    if (picker.hasClass('ui-dialog-content')) picker.dialog('option', 'title', 'Select ' + label());
    refreshButtons();
  }

  function loadLibrary(openAfter) {
    $.get(API_ROOT + '/get/portal_media').done(function (data) {
      applyResponse(data);
      render();
      if (openAfter) {
        $('#portalMediaPicker').dialog({
          modal: true,
          width: Math.min(430, Math.max(260, $(window).width() - 20)),
          resizable: false,
          title: 'Select ' + label()
        });
      }
    }).fail(function () { showMessage('Unable to load the portal-media library.'); });
  }

  function addMedia() {
    $('#portalMediaFile').val('').trigger('click');
  }

  function uploadFile(file) {
    if (!/\.(?:gif|png|jpe?g|mp4|webm)$/i.test(file.name)) {
      showMessage('Choose a GIF, PNG, JPG/JPEG, MP4, or WebM file.');
      return;
    }
    if (file.size > 80 * 1024 * 1024) {
      showMessage('The selected file is larger than the 80 MB limit.');
      return;
    }
    const uploadMode = mode;
    const add = $('#portalMediaAdd').prop('disabled', true).text('Uploading...');
    const reader = new FileReader();
    reader.onload = function (event) {
      request('/update/portal_media_asset', {
        media_type: uploadMode,
        filename: file.name,
        content: event.target.result
      }).done(function (data) {
        if (!data || data.success === false) {
          showMessage((data && data.message) || 'Unable to add the media file.');
          return;
        }
        applyResponse(data);
        render();
        showMessage('Added as ' + data.filename + '.', 'Media added');
      }).fail(function () { showMessage('Unable to upload the media file.'); })
        .always(function () { add.prop('disabled', false).text('Add ' + label()); });
    };
    reader.onerror = function () {
      add.prop('disabled', false).text('Add ' + label());
      showMessage('Unable to read the selected file.');
    };
    reader.readAsDataURL(file);
  }

  function buildUi() {
    if ($('#selectWormholeGifButton').length) return;
    const anchor = $('#openWormholeMenuButton');
    if (!anchor.length) return;
    const closeButton = anchor.closest('.debug_button_container').find('button').last();
    const selectButton = anchor.clone(false)
      .attr('id', 'selectWormholeGifButton')
      .removeAttr('action')
      .text('Select Wormhole');
    (closeButton.length ? closeButton : anchor).after(selectButton);

    const picker = $('<div id="portalMediaPicker"></div>').appendTo('body');
    const modes = $('<div></div>').css({display: 'flex', gap: '8px', 'margin-bottom': '12px'}).appendTo(picker);
    $('<button type="button" id="portalModeWormhole" class="btn-secondary">Wormhole</button>')
      .css({width: '164px', height: '48px'}).appendTo(modes);
    $('<button type="button" id="portalModeBlackHole" class="btn-secondary">Black Hole</button>')
      .css({width: '164px', height: '48px'}).appendTo(modes);
    $('<div id="portalMediaChoices"></div>').css({display: 'flex', 'flex-wrap': 'wrap', gap: '8px', 'max-height': '390px', overflow: 'auto'}).appendTo(picker);
    $('<button type="button" id="portalMediaAdd" class="btn-secondary">Add Wormhole</button>')
      .css({width: '100%', height: '48px', 'margin-top': '12px'}).appendTo(picker);
    $('<label><input type="checkbox" id="portalMediaDeleteMode"> Delete media</label>')
      .css({display: 'block', color: '#fff', margin: '12px 0'}).appendTo(picker);
    const scaleLabel = $('<label for="portalMediaScale"></label>')
      .css({display: 'flex', 'justify-content': 'space-between', color: '#fff'}).appendTo(picker);
    $('<span>Scale selected media</span>').appendTo(scaleLabel);
    $('<strong id="portalMediaScaleValue">100%</strong>').appendTo(scaleLabel);
    $('<input type="range" id="portalMediaScale" min="50" max="250" step="5" value="100">')
      .css({width: '100%'}).appendTo(picker);
    $('<small id="portalMediaProtected"></small>').css({display: 'block', color: '#ddd', 'margin-top': '8px'}).appendTo(picker);
    $('<input type="file" id="portalMediaFile" accept=".gif,.png,.jpg,.jpeg,.mp4,.webm" hidden>').appendTo(picker);

    selectButton.on('click', function () { loadLibrary(true); });
    $('#portalModeWormhole').on('click', function () { mode = 'wormhole'; render(); });
    $('#portalModeBlackHole').on('click', function () { mode = 'blackhole'; render(); });
    $('#portalMediaAdd').on('click', addMedia);
    $('#portalMediaFile').on('change', function () { if (this.files && this.files[0]) uploadFile(this.files[0]); });
    $('#portalMediaScale').on('input', function () { $('#portalMediaScaleValue').text($(this).val() + '%'); })
      .on('change', function () {
        request('/update/portal_media', {
          media_type: mode,
          filename: current().selected,
          scale: parseInt($(this).val(), 10)
        }).done(function (data) {
          if (!data || data.success === false) {
            showMessage((data && data.message) || 'Unable to save the scale.');
            return;
          }
          applyResponse(data);
          refreshButtons();
        }).fail(function () { showMessage('Unable to save the scale.'); });
      });
    loadLibrary(false);
  }

  $(buildUi);
})(jQuery);
