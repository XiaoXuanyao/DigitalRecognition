function requireService(sname, mes, respFunc) {
    // ���� XMLHttpRequest ����
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
    const msgBuffer = new TextEncoder().encode(message); // �ı�ת�ֽ�
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer); // ��ϣ
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // תΪ����
    const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join(""); // תʮ������
    return hashHex;
}
