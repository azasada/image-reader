function setTheme(theme) {
    document.documentElement.setAttribute("data-bs-theme", theme)
    if (theme == "light") {
        document.getElementById("theme-switch").innerHTML = "DARK THEME";
    } else {
        document.getElementById("theme-switch").innerHTML = "LIGHT THEME";
    }
}

setTheme("light");
document.getElementById("theme-switch").addEventListener("click", () => {
    if (document.documentElement.getAttribute("data-bs-theme") == "dark") {
        setTheme("light");
    } else {
        setTheme("dark");
    }
})
