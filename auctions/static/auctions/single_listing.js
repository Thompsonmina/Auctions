document.addEventListener('DOMContentLoaded', function() {

	const listing_id = JSON.parse(document.getElementById("get-id").textContent);
	
	const check_if_listing_in_watchlist = async() =>
	{
		const response = await fetch(`/in_watchlist?listing_id=${listing_id}`)
		const data = await response.json();
		if (data.success == true)
		{
			console.log(data.in_watchlist)
			update_watchlist_button(data.in_watchlist)
		}

	}
	check_if_listing_in_watchlist()

	// toggle between adding to watchlist and removing from watchlist on click
	document.querySelector("#edit-watchlist").onclick = function() {
		
	    const action = this.dataset.action;
	    if (action === "add") 
	    {
	    	update_watchlist_button(true)
	    	alert("listing added")
	    }
	    else 
	    {
	    	update_watchlist_button(false)
	    	alert("listing removed")
	    }
	    // Send a GET request to the URL
	    
	    fetch(`/edit_watchlist?action=${action}&listing_id=${listing_id}`)
	    // Put response into json form
	    .then(response => response.json())
	    .then(data => {
	        // Log data to the console
	        
	        if (data.success)
	        {
	        	console.log("success")
	        }
	    });
	}

	document.querySelector("#close-bid").onclick = () =>
	{    
	    fetch(`/close_bid/${listing_id}`)
	    // Put response into json form
	    .then(response => response.json())
	    .then(data => {
	        // Log data to the console
	        if (data.success)
	        {
	        	console.log("success")
	        }
	    });
	}
	
});

function update_watchlist_button(in_watchlist)
{
	const watchlist = document.querySelector("#edit-watchlist");
	if (in_watchlist === true)
	{
		watchlist.dataset.action = "delete"
		watchlist.innerText = "remove from watchlist"
	}
	else
	{
		watchlist.dataset.action = "add"
		watchlist.innerText = "add to watchlist"		
	}
}