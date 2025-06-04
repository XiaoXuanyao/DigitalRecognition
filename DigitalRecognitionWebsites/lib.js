function requireService(sname, mes, respFunc) {
    // 创建 XMLHttpRequest 对象
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:25565/?" + sname, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("sname", sname);
    let mesStr = JSON.stringify(mes);
    xhr.send(mesStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = xhr.responseText;
            respFunc(response);
        }
    };
}

async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message); // 文本转字节
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer); // 哈希
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // 转为数组
    const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join(""); // 转十六进制
    return hashHex;
}
