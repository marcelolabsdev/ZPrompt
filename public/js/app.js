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

    function selectType(type) {
        document.querySelectorAll(".prompt-type-card").forEach(function (c) {
            c.classList.remove(
                "border-primary",
                "bg-primary/10",
                "ring-2",
                "ring-ring"
            );
        });
        var card = document.querySelector('[data-type="' + type + '"]');
        if (card) {
            card.classList.add(
                "border-primary",
                "bg-primary/10",
                "ring-2",
                "ring-ring"
            );
        }
        selectedType = type;
        validateForm();
    }

    document.querySelectorAll(".prompt-type-card").forEach(function (card) {
        card.addEventListener("click", function () {
            selectType(card.dataset.type);
        });
    });

    selectType("start");

    userInput.addEventListener("input", validateForm);

    userInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!generateBtn.disabled) {
                handleGenerate();
            }
        }
    });

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

    function offsetToTzName(offset) {
        var offsetH = Math.floor(Math.abs(offset) / 60);
        var offsetM = Math.abs(offset) % 60;
        var sign = offset >= 0 ? "+" : "-";
        return "UTC" + sign + (offsetH < 10 ? "0" : "") + offsetH + ":" + (offsetM < 10 ? "0" : "") + offsetM;
    }

    function calcOffsetFromTzName(tzName) {
        try {
            var now = new Date();
            var utcStr = now.toLocaleString("en-US", { timeZone: "UTC" });
            var localStr = now.toLocaleString("en-US", { timeZone: tzName });
            return (new Date(localStr) - new Date(utcStr)) / 60000;
        } catch (e) {
            return 0;
        }
    }

    var cachedOffset = null;

    function detectOffsetAsync() {
        var browserOffset = -new Date().getTimezoneOffset();
        try {
            var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (tz && tz !== "UTC") {
                cachedOffset = browserOffset;
                return;
            }
        } catch (e) {}

        if (browserOffset !== 0) {
            cachedOffset = browserOffset;
            return;
        }

        cachedOffset = 0;

        fetch("https://ipapi.co/json/")
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.timezone && data.timezone !== "UTC") {
                    var realOffset = calcOffsetFromTzName(data.timezone);
                    if (realOffset !== 0) {
                        cachedOffset = realOffset;
                        localStorage.setItem("zprompt-tz-offset", realOffset);
                        localStorage.setItem("zprompt-tz-name", data.timezone);
                        updatePeakInfo();
                    }
                }
            })
            .catch(function () {});
    }

    (function loadCachedTz() {
        var cached = localStorage.getItem("zprompt-tz-offset");
        if (cached !== null) {
            cachedOffset = parseInt(cached, 10);
        }
    })();

    detectOffsetAsync();

    function updatePeakInfo() {
        var now = new Date();
        var offset = cachedOffset !== null ? cachedOffset : (-new Date().getTimezoneOffset());

        var offsetStr = offsetToTzName(offset);

        var localDate = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (offset * 60000));
        var localH = localDate.getHours();
        var localM = localDate.getMinutes();
        var timeStr = (localH < 10 ? "0" : "") + localH + ":" + (localM < 10 ? "0" : "") + localM;

        var utcH = now.getUTCHours();
        var isPeak = utcH >= 6 && utcH < 10;
        var status = isPeak ? "PEAK" : "OFF-PEAK";
        var statusColor = isPeak ? "text-destructive" : "text-primary";
        var msg = isPeak ? "Horas pico - uso limitado" : "Buen momento para usar Z.ai";

        var peakStartUTC = 6;
        var peakEndUTC = 10;
        var localOffsetH = offset / 60;
        var peakStartLocal = (peakStartUTC + localOffsetH + 24) % 24;
        var peakEndLocal = (peakEndUTC + localOffsetH + 24) % 24;
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
