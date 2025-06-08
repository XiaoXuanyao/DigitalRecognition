function requireService(sname, mes, respFunc) {
    // 创建 XMLHttpRequest 对象
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://hlchen200628.qicp.net/?" + sname, true);
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

function onHeadLoad() {
    document.body.style.display = "inline";
    if (sessionStorage.getItem("username")) {
        const signinBtn = document.getElementById("signinBtn");
        signinBtn.innerHTML = `<i class="fas fa-user"></i> 用户`;
        signinBtn.href = "user.html"
    }
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
