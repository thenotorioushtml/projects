
// drop down menu for the nav bar
var settingsmenu = document.querySelector(".settings-menu");

function settingsMenuToggle() {
    settingsmenu.classList.toggle("settings-menu-height");
}
// drop down menu for the posts
function postMenuToggle(element) {
    var postId = element.getAttribute("data-post-id");
    var postmenu = document.querySelector("#post-menu-" + postId);
    postmenu.classList.toggle("post-menu-height");
}
// dark or light theme switch
var darkBtn = document.getElementById("dark-btn");
darkBtn.onclick = function() {
    darkBtn.classList.toggle("dark-btn-on");
    document.body.classList.toggle("dark-theme");

    if(localStorage.getItem("theme") == "light") {
        localStorage.setItem("theme", "dark");
    }
    else {
        localStorage.setItem("theme", "light");
    }
}

// the browser will remember the theme
if(localStorage.getItem("theme") == "light") {
    darkBtn.classList.remove("dark-btn-on");
    document.body.classList.remove("dark-theme");
}
else if(localStorage.getItem("theme") == "dark") {
    darkBtn.classList.add("dark-btn-on");
    document.body.classList.add("dark-theme");
}
else  {
    localStorage.setItem("theme", "light");
}

// like ajax call
$(document).on('click', '.like-image', function() {
    var postId = $(this).closest('.like-section').data('post-id');
    var likeCount = $(this).siblings('.like-count');
    var likeImage = $(this);
    if (postId) {
        $.ajax({
            url: '/like/' + postId,
            type: 'GET',
            success: function(data) {
                if(data.success) {
                    likeCount.text(data.like_count);
                    if (data.is_liked) {
                        likeImage.attr("src", "/static/images/like.png");
                    } else {
                        likeImage.attr("src", "/static/images/like-blue.png");
                    }
                }
                else {
                    alert("An error occured while liking the post. Please try again later.");
                }
            },

            error: function() {
                alert("An error occured while liking the post. Please try again later.");
            }
        });
    } else {
        console.log("Post id not found");
    }
});

// image preview before uploading
const content = document.getElementById("content");
if (content) {
    content.addEventListener("change", function() {
        var reader = new FileReader();
        reader.onload = function(e) {
            // Get loaded data and render thumbnail
            document.getElementById("image-preview").src = e.target.result;
            document.getElementById("image-preview").style.display = "block";
        };
        // Read the image file as a data URL
        reader.readAsDataURL(this.files[0]);
    });
}
    