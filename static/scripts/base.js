window.addEventListener("scroll", function () {
    document.querySelector(".navbar").classList.toggle("scrolled", window.scrollY > 0);
});

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);

    var alertList = document.querySelectorAll(".alert-dismissible")
    if (alertList) {
        setTimeout(function () {
            alertList.forEach(element => {
                var alert = new bootstrap.Alert(element);
                alert.close()
            });
        }, 5000);
    }

    document.querySelector(".navbar-collapse").addEventListener("show.bs.collapse", function () {
        document.querySelector(".navbar").classList.add("scrolled");
    });

    document.querySelector(".navbar-collapse").addEventListener("hide.bs.collapse", function () {
        document.querySelector(".navbar").classList.toggle("scrolled", window.scrollY > 0);
    });

    var dobField = document.getElementById("date_of_birth");
    if (dobField) {
        dobField.type = "date";
    }

    var slider = document.getElementById("caloriesSlider");
    var text = document.getElementById("caloriesText");
    var correctAnswer = document.getElementById("correctAnswer")
    var showAnswerButton = document.getElementById("showAnswerButton");
    var hideAnswerButton = document.getElementById("hideAnswerButton");
    if (slider && text && correctAnswer) {
        slider.addEventListener("input", function () {
            text.innerHTML = slider.value;
        })
        showAnswerButton.addEventListener("click", function () {
            slider.disabled = true;
            correctAnswer.style.opacity = 1;
            showAnswerButton.classList.add("d-none");
            hideAnswerButton.classList.remove("d-none");
        });
        hideAnswerButton.addEventListener("click", function () {
            slider.disabled = false;
            correctAnswer.style.opacity = 0;
            hideAnswerButton.classList.add("d-none");
            showAnswerButton.classList.remove("d-none");
        });
    }

    const searchInput = document.getElementById("search-input");
    const searchButton = document.getElementById("search-button");
    if (searchInput && searchButton) {
        const searchParam = urlParams.get("search");
        if (searchParam) {
            searchInput.value = searchParam;
        }
        searchInput.addEventListener("click", function (e) {
            e.target.select();
        });
        searchInput.addEventListener("keydown", function (e) {
            if (e.code === "Enter") {
                searchButton.click();
            }
        });
        searchButton.addEventListener("click", function () {
            urlParams.set("search", searchInput.value);
            window.location.href = window.location.pathname + "?" + urlParams;
        });
    }

    const sendMailButton = document.getElementById("sendMailButton");
    const sendMailForm = document.getElementById("sendMailForm");
    if (sendMailButton && sendMailForm) {
        sendMailForm.addEventListener('submit', function () {
            sendMailButton.disabled = true;
            sendMailButton.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>Sending...';
        });
    }
});
