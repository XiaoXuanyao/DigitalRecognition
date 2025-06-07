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

function onHeadLoad() {
    document.body.style.display = "inline";
    // 初始化时间并设置定时器
    updateTime();
    setInterval(updateTime, 1000);
    
    // 联系我们按钮功能
    document.querySelector(".contact-btn").addEventListener("click", function (e) {
        e.preventDefault();
        alert(
            "请联系我们的支持团队: support@aimodelplatform.com\n电话: 400-123-4567\n工作时间: 周一至周五 9:00-18:00"
        );
    });

    // 模拟管理员登录状态切换
    document.querySelector(".login-btn").addEventListener("click", function (e) {
        if (this.getAttribute("href") === "login.html") return;

        e.preventDefault();
        document.body.classList.toggle("is-admin");
        this.innerHTML = document.body.classList.contains("is-admin")
            ? '<i class="fas fa-sign-out-alt"></i> 退出'
            : '<i class="fas fa-sign-in-alt"></i> 登录';

        // 添加视觉反馈
        if (document.body.classList.contains("is-admin")) {
            this.style.backgroundColor = "#ff6b6b";
            this.style.borderColor = "#ff6b6b";
            this.style.color = "#fff";
        } else {
            this.style.backgroundColor = "";
            this.style.borderColor = "";
            this.style.color = "";
        }

    });
}

// 时间显示功能
function updateTime() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const day = now.getDate();

    // 更新时间
    document.getElementById("time-hour").textContent = hours.toString().padStart(2, "0");
    document.getElementById("time-minutes").textContent = minutes.toString().padStart(2, "0");
    document.getElementById("time-seconds").textContent = seconds.toString().padStart(2, "0");

    // 更新日期
    document.getElementById("time-year").textContent = year;
    document.getElementById("time-month").textContent = month.toString().padStart(2, "0");
    document.getElementById("time-day").textContent = day.toString().padStart(2, "0");
}
