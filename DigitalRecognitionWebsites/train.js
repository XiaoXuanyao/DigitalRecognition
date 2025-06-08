// 文件上传功能
const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const emptyFileList = document.getElementById("empty-file-list");
const uploadCount = document.getElementById("uploadCount");
const uploadPercent = document.getElementById("uploadPercent");
const uploadFill = document.getElementById("uploadFill");

uploadArea.addEventListener("click", () => fileInput.click());
emptyFileList.addEventListener("click", () => fileInput.click());

uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = "var(--primary-color)";
    uploadArea.style.backgroundColor = "rgba(0, 102, 102, 0.1)";
});

uploadArea.addEventListener("dragleave", () => {
    uploadArea.style.borderColor = "var(--border-color)";
    uploadArea.style.backgroundColor = "";
});

uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = "var(--border-color)";
    uploadArea.style.backgroundColor = "";

    if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
    }
});

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFiles(fileInput.files);
    }
});

// 验证标签输入是否为有效数字
function validateLabelInput(input) {
    const value = input.value.trim();
    if (value === "") {
        input.classList.remove("valid", "invalid");
        return false;
    }

    // 检查是否为0-9的数字
    if (/^[0-9]$/.test(value)) {
        input.classList.add("valid");
        input.classList.remove("invalid");
        return true;
    } else {
        input.classList.add("invalid");
        input.classList.remove("valid");
        return false;
    }
}

function checkNoFile() {
    if (fileList.children.length === 0) {
        fileList.innerHTML = `
            <div class="empty-message">
                <div id="empty-file-list">
                    <i class="fas fa-cloud-upload-alt fa-2x"></i>
                    <p>尚未上传图片</p>
                    <p>上传后可使用标注功能</p>
                </div>
            </div>
        `;
        const emptyFileList = document.getElementById("empty-file-list");
        emptyFileList.addEventListener("click", () => fileInput.click());
    }
}

function updateUploadProcessBar(filesCount, uploadedCount) {
    progress = uploadedCount / (filesCount + 1e-6) * 100;
    uploadFill.style.width = `${progress}%`;
    uploadPercent.textContent = progress.toFixed(1);
    uploadCount.textContent = filesCount - uploadedCount;
    if (progress > 100 - 1e-4) {
        startBtn.innerHTML = '<i class="fas fa-play"></i> 开始训练模型';
        startBtn.disabled = false;
    }
    else if (filesCount == 0) {
        startBtn.innerHTML = '<i class="fas fa-info-circle"></i> 未上传训练集';
        startBtn.disabled = true;
    }
}

function handleFiles(files) {
    startBtn.innerHTML = '<i class="fas fa-info-circle"></i> 正在上传训练集...';
    startBtn.disabled = true;
    filesCount = files.length;
    uploadedCount = 0;
    // 移除空列表提示
    if (fileList.querySelector(".empty-message")) {
        fileList.innerHTML = "";
    }

    notImageFiles = "";
    imgData = []
    for (let i = 0; i < files.length; i++) {
        // 校验图像格式
        if (!files[i].type.match("image.*")) {
            uploadedCount++;
            updateUploadProcessBar(filesCount, uploadedCount);
            notImageFiles += files[i].name + "\n";
            continue;
        }
        
        // 设置默认标签
        defaultLabel = "";
        labelArr = files[i].name.split('_');
        if (labelArr.length > 0 && labelArr[labelArr.length - 1].length > 0)
            defaultLabel = labelArr[labelArr.length - 1].substring(0, 1);
        defaultLabel = defaultLabel.match("[0-9]") ? defaultLabel : "";

        // 添加到列表
        const fileItem = document.createElement("div");
        fileItem.className = "file-item";
        fileItem.id = files[i].name;
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-image"></i>
                <span class="file-name">${files[i].name}</span>
            </div>
            <input type="text" class="input" style="width:50px;" maxlength="1" placeholder="标签" value="${defaultLabel}" />
            <button class="delete-btn"><i class="fas fa-trash"></i></button>
        `;
        fileList.appendChild(fileItem);

        // 添加标签输入验证
        const labelInput = fileItem.querySelector(".input");
        labelInput.addEventListener("input", () => {
            validateLabelInput(labelInput);
        });

        // 添加删除功能
        fileItem.querySelector(".delete-btn").addEventListener("click", () => {
            fileList.removeChild(fileItem);
            checkNoFile();
        });

        // 读取图像
        const reader = new FileReader();
        const fileName = files[i].name;
        reader.onload = function(event) {
            const content = event.target.result;
            imgData.push({
                filename: fileName,
                imgdata: content.split(',')[1]
            });
            if (imgData.length == files.length)
                uploadImage();
        }
        reader.readAsDataURL(files[i]);
    }

    // 上传图像
    function uploadImage() {
        let onceCnt = 200;
        for (let i = 0; i < imgData.length; i += onceCnt) {
            buff = []
            let cnt = Math.min(onceCnt, imgData.length - i)
            for (let j = 0; j < cnt; j++)
                buff.push(imgData[i + j]);
            requireService("uploadimg/train", {
                "data": structuredClone(buff)
            }, function(respMes) {
                res = JSON.parse(respMes);
                if (res.Result == "OK") {
                    uploadedCount += res.Cnt;
                    updateUploadProcessBar(filesCount, uploadedCount);
                }
            });
        }
    }

    checkNoFile();
    if (notImageFiles != "")
        alert("以下文件不是图像文件，已自动过滤：\n" + notImageFiles);
}

const resetDataset = document.getElementById("resetDataset");
resetDataset.addEventListener("click", () => {
    // 移除空列表提示
    if (fileList.querySelector(".empty-message")) {
        fileList.innerHTML = "";
    }
    if (fileList.children.length === 0) {
        alert("训练集尚未上传");
        checkNoFile();
        return;
    }
    while (fileList.firstChild) {
        fileList.removeChild(fileList.firstChild);
    }
    checkNoFile();
    requireService("clearimg/train", {
    }, function(respMes) {
        if (respMes == "Result: OK") {
            updateUploadProcessBar(0, 0);
        }
        else {
            alert("请求失败");
        }
    });
});

window.addEventListener("load", () => {
    requireService("clearimg/train", {
    }, function(respMes) {
        if (respMes == "Result: OK") {
            updateUploadProcessBar(0, 0);
        }
    });
});


// 初始化图表
const chartCtx = document.getElementById("accuracyChart").getContext("2d");
const lossCtx = document.getElementById("lossChart").getContext("2d");
let accuracyChart;
let lossChart;

// 训练功能
const startBtn = document.getElementById("startTraining");
const progressFill = document.getElementById("progressFill");
const progressPercent = document.getElementById("progressPercent");
const batchCount = document.getElementById("batchCount");
const chartPlaceholder = document.getElementById("chartPlaceholder");
const lossPlaceholder = document.getElementById("lossPlaceholder");

startBtn.addEventListener("click", () => {
    const epochs = parseInt(document.getElementById("epochs").value);
    const learningRate = parseFloat(document.getElementById("learningRate").value);
    const batchSize = parseInt(document.getElementById("batchSize").value);

    // 验证输入
    if (fileList.querySelector(".empty-message") || fileList.children.length === 0) {
        alert("请先上传训练图片");
        return;
    }

    // 检查所有标签是否有效
    let allLabelsValid = true;
    const labelInputs = document.querySelectorAll(".label-input");
    const invalidFiles = [];

    labelInputs.forEach((input, index) => {
        if (!validateLabelInput(input)) {
            allLabelsValid = false;
            invalidFiles.push(fileList.children[index].querySelector(".file-name").textContent);
        }
    });

    if (!allLabelsValid) {
        alert(`以下图片的标签无效，请输入0-9的数字：\n${invalidFiles.join("\n")}`);
        return;
    }

    // 发送训练请求
    requireService("train", {
        epochs: epochs,
        learningrate: learningRate,
        batchsize: batchSize
    }, function(respMes) {
        if (respMes == "Result: OK") {
            setTimeout(() => trainProcess(), 200);
        }
        else {
            alert("服务器存在另一个训练进程，训练无法开始。")
        }
    });

    function trainProcess() {
        // 隐藏占位符，显示图表
        chartPlaceholder.style.display = "none";
        lossPlaceholder.style.display = "none";
        document.getElementById("accuracyChart").style.display = "block";
        document.getElementById("lossChart").style.display = "block";

        // 初始化图表
        if (accuracyChart) {
            accuracyChart.destroy();
        }
        if (lossChart) {
            lossChart.destroy();
        }

        accuracyChart = new Chart(chartCtx, {
            type: "line",
            data: {
                labels: Array.from({ length: 10 }, (_, i) => i * 1),
                datasets: [
                    {
                        label: "val-Accuracy",
                        data: [],
                        borderColor: "rgba(141, 204, 204, 1)",
                        backgroundColor: "rgba(141, 204, 204, 0.5)",
                        tension: 0.1,
                        fill: true,
                    },
                    {
                        label: "Accuracy",
                        data: [],
                        borderColor: "rgba(198, 235, 203, 1)",
                        backgroundColor: "rgba(198, 235, 203, 0.5)",
                        tension: 0.1,
                        fill: true,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function (value) {
                                return (value * 100).toFixed(0) + "%";
                            },
                        },
                    },
                },
            },
        });

        lossChart = new Chart(lossCtx, {
            type: "line",
            data: {
                labels: Array.from({ length: 10 }, (_, i) => i * 1),
                datasets: [
                    {
                        label: "val-Loss",
                        data: [],
                        borderColor: "rgba(141, 204, 204, 1)",
                        backgroundColor: "rgba(141, 204, 204, 0.5)",
                        tension: 0.1,
                        fill: true,
                    },
                    {
                        label: "Loss",
                        data: [],
                        borderColor: "rgba(198, 235, 203, 1)",
                        backgroundColor: "rgba(198, 235, 203, 0.5)",
                        tension: 0.1,
                        fill: true,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function (value) {
                                return value.toFixed(4);
                            },
                        },
                    },
                },
            },
        });

        let cEpoch = 0;
        let maxEpoch = 0;
        let cBatch = 0;
        let maxBatch = 0;
        let cLoss = 0;
        let cAcc = 0;
        let cvalLoss = 0;
        let cvalAcc = 0;
        let statu = "Free";
        // 训练过程
        const trainingInterval = setInterval(() => {
            // 更新epoch
            requireService("getstatu/train", {
            }, function(respMes) {
                let mes = JSON.parse(respMes);
                if (mes.Result == "OK") {
                    let data = mes.Data;
                    cEpoch = data.cEpoch;
                    maxEpoch = data.maxEpoch;
                    cBatch = data.cBatch;
                    maxBatch = data.maxBatch;
                    cLoss = data.cLoss;
                    cAcc = data.cAcc;
                    cvalLoss = data.cvalLoss;
                    cvalAcc = data.cvalAcc;
                    statu = mes.Statu;
                }
                else if (mes.Result == "Training not started") {
                    finishTraining();
                    return;
                }
                else if (mes.Result == "No such statu") {
                    finishTraining();
                    return;
                }
            });

            // 更新进度
            const Step = maxEpoch >= 20 ? Math.floor(maxEpoch / 20) : 1
            let progress = (Math.max(cEpoch - 1, 0) % Step + cBatch / maxBatch) / Step * 100;

            // 更新UI
            if (statu == "ReadDataset") {
                progressPercent.textContent = "% 读取数据集中，请稍后…… ";
                batchCount.textContent = maxBatch;
            }
            else if (statu == "Training") {
                progressFill.style.width = `${progress}%`;
                progressPercent.textContent = progress.toFixed(1);
                batchCount.textContent = maxBatch;
            }

            // 准确率变化
            accData = []
            valaccData = []
            for (let j = 0; j < cAcc.length; j += Step) {
                accData.push(cAcc[j]);
                valaccData.push(cvalAcc[j]);
            }
            accuracyChart.data.labels = Array.from(
                { length: maxEpoch / Step },
                (_, i) => (i + 1) * (Step));
            accuracyChart.data.datasets[0].data = valaccData;
            accuracyChart.data.datasets[1].data = accData;
            accuracyChart.update();

            // 损失值变化
            lossData = []
            vallossData = []
            for (let j = 0; j < cLoss.length; j += Step) {
                lossData.push(cLoss[j]);
                vallossData.push(cvalLoss[j]);
            }
            maxLoss = Math.max(...lossData, ...vallossData, 1);
            lossChart.options.scales.y.max = maxLoss;
            lossChart.data.labels = Array.from(
                { length: maxEpoch / Step },
                (_, i) => (i + 1) * (Step));
            lossChart.data.datasets[0].data = vallossData;
            lossChart.data.datasets[1].data = lossData;
            lossChart.update();
            
            if (cEpoch == maxEpoch && maxEpoch != 0)
                finishTraining();
        }, 200);

        function finishTraining() {
            const progress = 100
            progressFill.style.width = `${progress}%`;
            progressPercent.textContent = progress.toFixed(1);
            console.log("训练完成");
            clearInterval(trainingInterval);
            startBtn.innerHTML = '<i class="fas fa-play"></i> 开始训练模型';
            startBtn.disabled = false;
        }

        startBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> 训练中...';
        startBtn.disabled = true;
    }
});