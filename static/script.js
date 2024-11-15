document.getElementById("search-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent the form from submitting the default way

    const formData = new FormData(event.target);
    const response = await fetch("/search", {
        method: "POST",
        body: formData,
    });

    const data = await response.json(); // Get the JSON response

    // Clear previous results
    const resultsContainer = document.getElementById("search-results");
    resultsContainer.innerHTML = '';

    // Display search results
    if (data.profiles.length > 0) {
        const list = document.createElement("ul");
        data.profiles.forEach(profile => {
            const listItem = document.createElement("li");
            listItem.textContent = `${profile.username} - ${profile.bio} - ${profile.location}`;
            list.appendChild(listItem);
        });
        resultsContainer.appendChild(list);
    } else {
        resultsContainer.textContent = "No profiles found.";
    }
});

document.getElementById("download-button").addEventListener("click", async function() {
    const username = document.getElementById("username").value;
    const location = document.getElementById("location").value;
    const bioKeyword = document.getElementById("bio-keyword").value;

    const response = await fetch(`/download?username=${username}&location=${location}&bio_keyword=${bioKeyword}`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'filtered_data.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
});
