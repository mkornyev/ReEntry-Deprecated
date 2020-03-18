
var stagedResources = [] 

$(document).ready(function(){
    $('#make-referral').attr('state', 'off')
    $('#make-referral').click(toggleSelect)
});

function toggleSelect() {
    if ($(this).attr('state') === 'off') {

        $('.resource-card').each(function() {
            $(this).attr('state','out')
            $(this).click(toggleItem)
        }) 

        $(this).html('Cancel')
        $(this).attr('state', 'on')
        $('#commit-referral').css('display', 'block')
    } else if ($(this).attr('state') === 'on') {
        $('.resource-card').each(function() {
            $(this).unbind('click')
            $(this).attr('state','out')
            $(this).css('border','1px solid rgba(0,0,0,.125)')
        }) 

        stagedResources = []

        $(this).html('Make Referral')
        $(this).attr('state', 'off')
        $('#commit-referral').css('display', 'none')
    }
}

function toggleItem(event) {
    event.preventDefault() 
    state = $(this).attr('state')
    id = $(this).attr('id').substring(9)

    if (state === 'in') {
        $(this).attr('state','out')
        $(this).css('border','1px solid rgba(0,0,0,.125)')
        stagedResources = stagedResources.filter(function(inId) { inId != id; })
    } else if (state === 'out') {
        $(this).attr('state','in')
        $(this).css('border','5px solid yellow')
        $(this).css('border-radius','10px')
        stagedResources.push(id)
    }
}

// Func to get login token from cookie
// function getCSRFToken() {
//     var cookies = document.cookie.split(";");
//     for (var i = 0; i < cookies.length; i++) {
//         c = cookies[i].trim();
//         if (c.startsWith("csrftoken=")) {
//             return c.substring("csrftoken=".length, c.length);
//         }
//     }
//     return "unknown";
// }

function commitReferrals() {
    if (stagedResources.length === 0) return; 

    document.location.href = '/create_referral?resources=' + JSON.stringify(stagedResources);

    // var req = new XMLHttpRequest();
    // req.onreadystatechange = function() {
    //     if (req.readyState != 4) return
    //     if (req.status != 200) return
    //     var response = JSON.parse(req.responseText)
    //     if (response['error'] != null) {
    //         // displayError(response.error);
    //         alert('Error when sending axaj')
    //     } else {
    //         document.location.href = response['redirect'];
    //     }
    // }
    // req.open("POST", "/stage_referrals/", true);
    // req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    // req.send("payload=" + JSON.stringify(stagedResources) + "&csrfmiddlewaretoken="+getCSRFToken());
}