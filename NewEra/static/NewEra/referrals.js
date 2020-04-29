// THIS FILE IS LINKED FROM THE FOLLOWING LOCATIONS: 
// resources.html
// create_referral.html

var stagedDeleteId = null;

$(document).ready(function() {
    $('#make-referral').attr('state', 'off');
    $('#make-referral').click(toggleSelect);
    // $('#referral-ins').css('display', 'none');

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

// Hide a referral's resource delete confirmation popup
cancel = () => {
    var delModal = document.getElementById('del-confirm');
    delModal.style.display = "none";
}

// Remove a resource from the referral
confirmDelete = () => {
    console.log(localStorage.stagedResources);
    if (stagedDeleteId == null) {
        // Fail silently: just close the modal, however this should not happen.
        var delModal = document.getElementById('del-confirm');
        delModal.style.display = "none";
        return;
    }

    // Grab the resources staged so far and get the one to remove
    stagedResources = JSON.parse(localStorage.getItem("stagedResources"));
    leftoverResources = stagedResources.filter((id) => id != stagedDeleteId);

    var empty = false;
    if (leftoverResources.length === 0) {
        empty = true;
    }

    localStorage.stagedResources = JSON.stringify(leftoverResources)

    // Generate a link based on the resources selected
    if (empty) {
        document.location.href = "/resources";
    }
    else {
        document.location.href = '/create_referral?resources=' + localStorage.stagedResources;
    }
}

// Remove a resource from the referral
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

        // 
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

// Toggle a resource as being part of the referral when selected
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
        // Remove the border from the resource and remove it from the staged resources
        $(this).attr('state','out');
        $(this).addClass("border-0");
        $(this).removeClass("border-success");
        $(this).removeClass("border-3");
        stagedResources = stagedResources.filter((inId) => inId != id);
    } else if (state === 'out') {
        // Add a border to the resource and add it to the staged resources
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

// Send the resources to the referral
function commitReferrals() {
    stagedResources = window.localStorage.stagedResources
    if (stagedResources === "[]") return; 

    document.location.href = '/create_referral?resources=' + stagedResources;
}
