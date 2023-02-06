function changeAxis(channel, target, accel, speed, func = null) {
  jQuery.post( '/servo/' + channel + "/" + target , {
    "speed" : speed,
    "accel" : accel,
  } , function(response) {
    if (func != null) {
      func(response)
    }
  } );
}

function updateImage(id, callback = null) {
  jQuery.get("/image/" + id, function(data) {
    $('.img-container img').attr('src', 'data:image/jpg;base64,' + data)
    if (callback !=null) {
      callback(data)
    }
  })
}

function readImage(id, callback = null) {
  jQuery.get("/cached_image_js/" + id, function(data) {
    if (callback !=null) {
      callback(data)
    }
  })
}

$.when( $.ready ).then(function() {
  readImage(0, function(data) {
    $('.img-container img').attr('src', 'data:image/jpg;base64,' + data)
  });

  $('#refresh_image').on('click', function(e) {
    elem = $(this);
    elem.prop("disabled", true);
    elem.html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>');  
    updateImage(0, function() {
      elem.prop("disabled", false);
      elem.html('Refresh');  
    });
  });

  $('.servo-control').on('change', function(e) {
    elem = $(this);
    let servo_value = elem.closest('.row').find('.servo-value')
    let servo_set_btn = elem.closest('.row').find('.btn-set')
    elem.prop('disabled', true)
    servo_value.prop('disabled', true)
    servo_set_btn.prop('disabled', true)

    channel = elem.data('channel');
    changeAxis(channel, elem.val(), 25, 30, function(data) {
      elem.prop('disabled', false)
      servo_value.prop('disabled', false)
      servo_set_btn.prop('disabled', false)
      elem.val(data)
      servo_value.val(data)
    });
  });

  $('input.save-label').on('change', function() {
    elem = $(this)
    if (elem.val() != '') {
      $('.save-button').removeClass('disabled')
    } else {
      $('.save-button').addClass('disabled')
    }
  })

  $('.stow-button').on('click', function() {
    elem = $(this);
    elem.prop('disabled', true)
    // changeAxis(0, 6000, 25, 30);
    // changeAxis(1, 6000, 25, 30);
    // changeAxis(2, 5800, 25, 30);
    // changeAxis(3, 4200, 25, 30);
    // changeAxis(4, 6000, 25, 5);
    jQuery.post( '/stow', function(data) {
      elem.prop('disabled', false)
      var channel_positions = jQuery.parseJSON(data);
      $(channel_positions).each(function(index, elem)
       {
        $('div.row-' + elem[0] + '.row-channel-container .servo-control').val(elem[1])
        $('div.row-' + elem[0] + '.row-channel-container .servo-value').val(elem[1])
      })
    } );
  })

  $('.reset-button').on('click', function() {
    elem = $(this);
    elem.prop('disabled', true)
    jQuery.post( '/motion', {
      "move_list" : JSON.stringify([
        { "channel" : 0, "target" : 6000},
        { "channel" : 1, "target" : 6000},
        { "channel" : 2, "target" : 6000},
        { "channel" : 3, "target" : 6000},
        { "channel" : 4, "target" : 6000},
      ])
    } , function(response) {
      elem.prop('disabled', false)
      $('.slider').val(6000)
      $('.servo-value').val(6000)
    } );
  })

  $('.container-bookmarks').on('click', '.btn-delete-bookmark', function() {
    let elem = $(this)
    let bookmark_id = elem.data('id')
    jQuery.post( '/delete/' +  bookmark_id,
     function(response) {
      $('#bookmark-'+ bookmark_id).fadeOut()
    });
  })

  $('.container-bookmarks').on('click', '.btn-set-bookmark', function() {
    let elem = $(this)
    elem.prop("disabled", true);

    // add spinner to button for some time
    elem.html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>');  

    bookmark_id = elem.data('id')
    jQuery.post( '/set/' + bookmark_id, function(data) {
      var channel_positions = jQuery.parseJSON(data);
      $(channel_positions).each(function(index, elem)
       {
        $('div.row-' + elem[0] + '.row-channel-container .servo-control').val(elem[1])
        $('div.row-' + elem[0] + '.row-channel-container .servo-value').val(elem[1])
      })
      updateImage(bookmark_id, function(data) {
        $('.img-thumbnail.image-thumb-' + bookmark_id).attr('src', 'data:image/jpg;base64,' + data)
        elem.prop("disabled", false)
        elem.html('Set')
      });
    });
  })

  // refresh all button
  $('#refresh-all-button').on('click', function() {
    let elem = $(this)
    elem.prop("disabled", true);
     // add spinner to button for some time
    elem.html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>');  
    jQuery.post('/refresh_all', function(data) {
      $('.bookmark-row').each(function(index, elem) {
        let bookmark_elem = $(elem);
        let bookmark_id = bookmark_elem.data('id');
        readImage(bookmark_id, function(data) {
          $('img.image-thumb-' + bookmark_id).attr('src', 'data:image/jpg;base64,' + data)
        });
      })
      elem.prop("disabled", false);
      // add spinner to button for some time
      elem.html('Refresh All'); 
    });
  });

  $('.save-button').on('click', function() {
    let motion_list = []
    let label = $('.save-label').val()
    $('.row-channel-container').each(function() {
      let row_container = $(this);
      let target_value = row_container.find('.servo-value')
      motion_list.push(
        {
          "accel" : 25,
          "channel" : row_container.data('channel'),
          "speed" : 30,
          "target" : target_value.val()
        }
      )
    })

    jQuery.post( '/save' , {
      "label" : label,
      "move_list" : JSON.stringify(motion_list)
    } , function(response) {
      $('.container-bookmarks').html(response)
    } );
  })

  $('.btn-set').on('click', function() {
    elem = $(this);
    elem.prop("disabled", true);
    // add spinner to button for some time
    elem.html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>');  

    let rowElem = elem.closest('.row')
    let channel = rowElem.data('channel')
    let target = rowElem.find('.servo-value').val()
    let slider = rowElem.find('.servo-control')
    slider.prop("disabled", true)

    changeAxis(channel, target, 25, 30, function(data) {
      elem.prop("disabled", false)
      elem.html("Set")
      slider.prop("disabled", false)
      slider.val(target)
      updateImage();
    })

  })
})
