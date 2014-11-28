var toggle_details = function(url) {
	var el = $('details');
	var ajax = new Ajax.Updater(el, url);
}

var add_comment = function(comment_el) {
    var comment_el = $(comment_el);
 
    var ajax = new Ajax.Request(comment_el.action, {
                method: comment_el.method,
                parameters: comment_el.serialize(),
                onSuccess: function(request) {
                    if ( request.responseText.isJSON() == true ) {
                        var data = request.responseText.evalJSON(true);
                        $('details').update(data['msg']);
                    }
                    else {
                        alert(req.responseText);
                    }
                },
                onFailure: function(req) {
                }
    });
}

var add_to_favourite = function(addfav_el) {
    var addfav_el = $(addfav_el);
 
    var ajax = new Ajax.Request(addfav_el.action, {
                method: 'post',
                parameters: addfav_el.serialize(),
                onSuccess: function(request) {
                    if ( request.responseText.isJSON() == true ) {
                        var data = request.responseText.evalJSON(true);
                        $('favourite').update(data['msg']);
                    }
                    else {
                        alert(req.responseText);
                    }
                },
                onFailure: function(req) {
                }
    });
}