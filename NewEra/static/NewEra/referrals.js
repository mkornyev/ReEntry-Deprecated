
// -------- MAKE REFERRAL ACTION --------

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

        console.log("Before:")
        console.log(stagedResources)
        index = stagedResources.indexOf(id)
        stagedResources.splice(index, 1)

        console.log("After:")
        console.log(stagedResources)

        // stagedResources = stagedResources.filter(function(inId) { inId != id; })
    } else if (state === 'out') {
        $(this).attr('state','in')
        $(this).css('border','5px solid yellow')
        $(this).css('border-radius','10px')
        stagedResources.push(id)
    }
    console.log(stagedResources)
}

function commitReferrals() {
    if (stagedResources.length === 0) return; 

    document.location.href = '/create_referral?resources=' + JSON.stringify(stagedResources);
}
