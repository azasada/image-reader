$(document).on("submit", "#imageForm", function(e) {
    e.preventDefault();
    let formData = new FormData();
    let images = $("#uploadImage").prop("files");
    for (let i = 0; i < images.length; i++) {
        formData.append("file", images[i]);
    }
    formData.append("lang", $("#lang").val());
    formData.append("crop", $('input[name="crop"]:checked').val());
    formData.append("spellcheck", $('input[name="spellcheck"]:checked').val());
    document.getElementById("submitButton").innerText = "Czekaj...";

    $.ajax({
        type: "POST",
        url: "/",
        data: formData,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            document.getElementById("ocrText").innerText = data["text"];
            document.getElementById("showAfter").style.display = "";
            document.getElementById("submitButton").innerText = "Odczytaj";
        },
    });
});
