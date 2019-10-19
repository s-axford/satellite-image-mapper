// toggles sidebar visablity and switches chevron direction
function toggleNav() {
    sidebar = document.getElementById("sidebar");
    main = document.getElementById("main");
    btn = document.getElementById("togglebtn");
    if (sidebar.style.width == "0px") {
        sidebar.style.width = "160px";
        sidebar.style.padding = "20px";
        main.style.marginLeft = "200px";
        btn.innerHTML = "&#171;";
    } else {
        sidebar.style.width = "0";
        sidebar.style.padding = "0";
        main.style.marginLeft = "0";
        btn.innerHTML = "&#187;";
    }
  }

// expands image to full browser width
function expandImage() {
    var image = document.getElementById("mainimage");
    image.classList.toggle("expanded");
}