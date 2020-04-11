var stagedDeleteId = null;

$(document).ready(function() {
    $('#make-referral').attr('state', 'off')
    $('#make-referral').click(toggleSelect)
});

cancel = () => {
    var delModal = document.getElementById('del-confirm');
    delModal.style.display = "none";
}

confirmDelete = () => {
    console.log(localStorage.stagedResources);
    if (stagedDeleteId == null) {
        // Fail silently: just close the modal, however this
        // should not happen.
        var delModal = document.getElementById('del-confirm');
        delModal.style.display = "none";
        return;
    }

    stagedResources = JSON.parse(localStorage.getItem("stagedResources"));
    leftoverResources = stagedResources.filter((id) => id != stagedDeleteId);

    var empty = false;
    if (leftoverResources.length === 0) {
        empty = true;
    }

    localStorage.stagedResources = JSON.stringify(leftoverResources)

    if (empty) {
        document.location.href = "/resources";
    }

    else {
        document.location.href = '/create_referral?resources=' + localStorage.stagedResources;
    }
}

deleteResource = (id) => {
    stagedDeleteId = id;
    var delModal = document.getElementById('del-confirm');
    delModal.style.display = "block";
}

function toggleSelect () {

    localStorage.stagedResources = "[]";

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
            $(this).addClass("border-0")
            $(this).removeClass("border-success");
        }) 

        window.localStorage.stagedResources = "[]";

        $(this).html('Make Referral')
        $(this).attr('state', 'off')
        $('#commit-referral').css('display', 'none')
    }
}

function toggleItem(event) {
    event.preventDefault();
    state = $(this).attr('state');;
    id = $(this).attr('id').substring(9);

    stagedResources = localStorage.getItem("stagedResources");

    if (stagedResources.length === 0) {
        stagedResources = "[]";
    }

    stagedResources = JSON.parse(stagedResources);

    if (state === 'in') {
        $(this).attr('state','out');
        $(this).addClass("border-0");
        $(this).removeClass("border-success");
        stagedResources = stagedResources.filter((inId) => inId != id);

    } else if (state === 'out') {
        $(this).attr('state','in');
        $(this).removeClass("border-0");
        $(this).addClass("border-success");

        stagedResources.push(id);

    }

    localStorage.stagedResources = JSON.stringify(stagedResources);
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
    stagedResources = window.localStorage.stagedResources
    if (stagedResources === "[]") return; 

    document.location.href = '/create_referral?resources=' + stagedResources;

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
