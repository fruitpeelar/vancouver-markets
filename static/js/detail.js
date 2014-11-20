var toggle_detail_box = function(url, market_id) {
    var box = $('detail_box_'+market_id);

    if ( box.visible() == true ) {
        box.hide();
    }
    else {
        var ajax = new Ajax.Updater(box, url);
        box.show();
    }
}