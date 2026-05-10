(function () {
    var userInput = document.getElementById("user-input");
    var languageSelect = document.getElementById("language-select");
    var frameworkSelect = document.getElementById("framework-select");
    var databaseSelect = document.getElementById("database-select");
    var generateBtn = document.getElementById("generate-btn");
    var btnText = document.getElementById("btn-text");
    var btnSpinner = document.getElementById("btn-spinner");
    var errorSection = document.getElementById("error-section");
    var errorMessage = document.getElementById("error-message");
    var resultSection = document.getElementById("result-section");
    var resultIcon = document.getElementById("result-icon");
    var resultTitle = document.getElementById("result-title");
    var resultContent = document.getElementById("result-content");
    var resultTimestamp = document.getElementById("result-timestamp");
    var copyBtn = document.getElementById("copy-btn");
    var regenerateBtn = document.getElementById("regenerate-btn");
    var themeToggle = document.getElementById("theme-toggle");
    var themeIconSun = document.getElementById("theme-icon-sun");
    var themeIconMoon = document.getElementById("theme-icon-moon");

    var selectedType = null;
    var lastRequest = null;

    var TYPE_LUCIDE = {
        system: "monitor",
        start: "rocket",
        followup: "repeat",
        debug: "bug",
    };

    var TYPE_LABELS = {
        system: "System Prompt",
        start: "Start Prompt",
        followup: "Follow-Up",
        debug: "Debugging",
    };

    lucide.createIcons();

    function setThemeIcons(isDark) {
        if (isDark) {
            themeIconSun.classList.add("hidden");
            themeIconMoon.classList.remove("hidden");
        } else {
            themeIconSun.classList.remove("hidden");
            themeIconMoon.classList.add("hidden");
        }
    }

    function initTheme() {
        var stored = localStorage.getItem("zprompt-theme");
        if (stored === "light") {
            document.documentElement.classList.remove("dark");
            setThemeIcons(false);
        } else {
            document.documentElement.classList.add("dark");
            setThemeIcons(true);
        }
    }

    themeToggle.addEventListener("click", function () {
        var isDark = document.documentElement.classList.toggle("dark");
        localStorage.setItem("zprompt-theme", isDark ? "dark" : "light");
        setThemeIcons(isDark);
    });

    initTheme();

    document.querySelectorAll(".prompt-type-card").forEach(function (card) {
        card.addEventListener("click", function () {
            document.querySelectorAll(".prompt-type-card").forEach(function (c) {
                c.classList.remove(
                    "border-primary",
                    "bg-primary/10",
                    "ring-2",
                    "ring-ring"
                );
            });
            card.classList.add(
                "border-primary",
                "bg-primary/10",
                "ring-2",
                "ring-ring"
            );
            selectedType = card.dataset.type;
            validateForm();
        });
    });

    userInput.addEventListener("input", validateForm);

    function validateForm() {
        var hasText = userInput.value.trim().length >= 5;
        var hasType = selectedType !== null;
        generateBtn.disabled = !(hasText && hasType);
    }

    generateBtn.addEventListener("click", handleGenerate);
    regenerateBtn.addEventListener("click", handleGenerate);

    async function handleGenerate() {
        var text = userInput.value.trim();
        if (text.length < 5 || !selectedType) return;

        lastRequest = {
            text: text,
            prompt_type: selectedType,
            language: languageSelect.value || null,
            framework: frameworkSelect.value || null,
            database: databaseSelect.value || null,
        };

        setLoading(true);
        hideError();
        hideResult();

        try {
            var response = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(lastRequest),
            });

            var data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Error generando el prompt");
            }

            showResult(data);
        } catch (err) {
            showError(err.message);
        } finally {
            setLoading(false);
        }
    }

    function setLoading(loading) {
        generateBtn.disabled = loading;
        if (loading) {
            btnText.textContent = "Generando...";
            btnSpinner.classList.remove("hidden");
        } else {
            btnText.textContent = "Generar Prompt";
            btnSpinner.classList.add("hidden");
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorSection.classList.remove("hidden");
    }

    function hideError() {
        errorSection.classList.add("hidden");
    }

    function showResult(data) {
        var iconName = TYPE_LUCIDE[data.prompt_type] || "file-text";
        resultIcon.innerHTML = '<i data-lucide="' + iconName + '" class="h-4 w-4"></i>';
        resultTitle.textContent = data.label || TYPE_LABELS[data.prompt_type] || "Prompt";
        resultContent.textContent = data.prompt;
        resultTimestamp.textContent = "Generado: " + new Date().toLocaleString("es-ES");
        resultSection.classList.remove("hidden");
        lucide.createIcons();
        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function hideResult() {
        resultSection.classList.add("hidden");
    }

    copyBtn.addEventListener("click", async function () {
        var text = resultContent.textContent;
        if (!text) return;
        try {
            await navigator.clipboard.writeText(text);
            copyBtn.innerHTML = '<i data-lucide="check" class="h-3.5 w-3.5"></i> Copiado!';
            lucide.createIcons();
            setTimeout(function () {
                copyBtn.innerHTML = '<i data-lucide="copy" class="h-3.5 w-3.5"></i> Copiar';
                lucide.createIcons();
            }, 2000);
        } catch {
            var textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.style.position = "fixed";
            textarea.style.opacity = "0";
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            document.body.removeChild(textarea);
            copyBtn.innerHTML = '<i data-lucide="check" class="h-3.5 w-3.5"></i> Copiado!';
            lucide.createIcons();
            setTimeout(function () {
                copyBtn.innerHTML = '<i data-lucide="copy" class="h-3.5 w-3.5"></i> Copiar';
                lucide.createIcons();
            }, 2000);
        }
    });

    function updatePeakInfo() {
        var now = new Date();
        var utcH = now.getUTCHours();
        var utcM = now.getUTCMinutes();
        var offset = -now.getTimezoneOffset();
        var offsetH = Math.floor(Math.abs(offset) / 60);
        var offsetM = Math.abs(offset) % 60;
        var sign = offset >= 0 ? "+" : "-";
        var offsetStr = "UTC" + sign + (offsetH < 10 ? "0" : "") + offsetH + ":" + (offsetM < 10 ? "0" : "") + offsetM;

        var localH = now.getHours();
        var localM = now.getMinutes();
        var timeStr = (localH < 10 ? "0" : "") + localH + ":" + (localM < 10 ? "0" : "") + localM;

        var isPeak = utcH >= 6 && utcH < 10;
        var status = isPeak ? "PEAK" : "OFF-PEAK";
        var statusColor = isPeak ? "text-destructive" : "text-primary";
        var msg = isPeak ? "Horas pico - uso limitado" : "Buen momento para usar Z.ai";

        var peakStartUTC = 6;
        var peakEndUTC = 10;
        var localOffset = offset / 60;
        var peakStartLocal = (peakStartUTC + localOffset + 24) % 24;
        var peakEndLocal = (peakEndUTC + localOffset + 24) % 24;
        var peakLocalStartStr = (peakStartLocal < 10 ? "0" : "") + Math.floor(peakStartLocal) + ":00";
        var peakLocalEndStr = (peakEndLocal < 10 ? "0" : "") + Math.floor(peakEndLocal) + ":00";

        var el = document.getElementById("peak-info");
        if (!el) return;
        el.innerHTML =
            '<p class="' + statusColor + ' font-semibold">' + status + ' &middot; ' + msg + '</p>' +
            '<p class="mt-1">Tu hora: ' + timeStr + ' (' + offsetStr + ') &middot; Peak local: ' + peakLocalStartStr + ' - ' + peakLocalEndStr + '</p>' +
            '<p class="mt-1">GLM-5.1: 3x peak / 2x off-peak &middot; <span class="text-primary">1x off-peak hasta fin de junio</span></p>';
    }
    updatePeakInfo();
    setInterval(updatePeakInfo, 60000);
})();
