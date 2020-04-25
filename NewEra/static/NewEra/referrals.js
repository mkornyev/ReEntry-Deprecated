// THIS FILE IS LINKED FROM THE FOLLOWING LOCATIONS: 
// resources.html
// create_referral.html

var stagedDeleteId = null;

$(document).ready(function() {
    # 
    $('#make-referral').attr('state', 'off');
    $('#make-referral').click(toggleSelect);
    $('#referral-ins').css('display', 'none');

    // Validation to require ONE of: { phone, email }
    $('#outOfSystemForm').on('submit', function(e){
        var phone = $('#outOfSystemPhone').val()
        var email = $('#outOfSystemEmail').val()

        if( (phone == null || phone == '') && (email == null || email == '') ){ 
            alert("Please enter a phone number or email.")
            e.preventDefault()
            return false 
        }

        return true 
    })
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
        $('#commit-referral').css('display', 'block');
        let refCount = 0;
        document.getElementById("commit-referral").innerHTML = "Select Resources " + "(" + refCount + ")"
        $('#referral-ins').css('display', 'block')
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
        $('#referral-ins').css('display', 'none')
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
        $(this).removeClass("border-3");
        stagedResources = stagedResources.filter((inId) => inId != id);

    } else if (state === 'out') {
        $(this).attr('state','in');
        $(this).removeClass("border-0");
        $(this).addClass("border-3")
        $(this).addClass("border-success");

        stagedResources.push(id);

    }

    let refCount = stagedResources.length
    document.getElementById("commit-referral").innerHTML = "Select Resources " + "(" + refCount + ")"

    localStorage.stagedResources = JSON.stringify(stagedResources);
}

function commitReferrals() {
    stagedResources = window.localStorage.stagedResources
    if (stagedResources === "[]") return; 

    document.location.href = '/create_referral?resources=' + stagedResources;
}
