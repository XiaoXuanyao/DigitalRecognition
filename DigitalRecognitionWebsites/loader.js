if (!sessionStorage.getItem("pageHeader")) {
    const xhr1 = new XMLHttpRequest();
    xhr1.open("GET", "header.html", true);
    xhr1.onreadystatechange = function () {
        if (xhr1.readyState === 4 && xhr1.status === 200) {
            document.getElementById("pageHeader").innerHTML += xhr1.responseText;
            sessionStorage.setItem("pageHeader", xhr1.responseText);
            onHeadLoad();
        }
    };
    xhr1.send();
}
else {
    document.getElementById("pageHeader").innerHTML += 
        sessionStorage.getItem("pageHeader");
    onHeadLoad();
}

if (!sessionStorage.getItem("pageFooter")) {
    const xhr2 = new XMLHttpRequest();
    xhr2.open("GET", "footer.html", true);
    xhr2.onreadystatechange = function () {
        if (xhr2.readyState === 4 && xhr2.status === 200) {
            document.getElementById("pageFooter").innerHTML += xhr2.responseText;
            sessionStorage.setItem("pageFooter", xhr2.responseText);
        }
    };
    xhr2.send();
}
else {
    document.getElementById("pageFooter").innerHTML += 
        sessionStorage.getItem("pageFooter");
}