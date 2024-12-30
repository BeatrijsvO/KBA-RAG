document.addEventListener("DOMContentLoaded", function () {
    const uploadButton = document.getElementById("uploadButton");
    const askButton = document.getElementById("askButton");
    const fileUpload = document.getElementById("fileUpload");
    const userQuestion = document.getElementById("userQuestion");
    const uploadResult = document.getElementById("uploadResult");
    const answerResult = document.getElementById("answerResult");

    const API_BASE_URL = "https://kba-project.onrender.com"; // Pas aan naar jouw Render API URL

    // Bestanden uploaden
    uploadButton.addEventListener("click", async function () {
        const files = fileUpload.files;

        if (files.length === 0) {
            uploadResult.textContent = "Geen bestanden geselecteerd.";
            return;
        }

        const formData = new FormData();
        for (const file of files) {
            formData.append("files", file);
        }

        try {
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            if (response.ok) {
                uploadResult.textContent = result.message;
            } else {
                uploadResult.textContent = `Fout: ${result.error}`;
            }
        } catch (error) {
            uploadResult.textContent = `Fout: ${error.message}`;
        }
    });

    // Vraag stellen
    askButton.addEventListener("click", async function () {
        const vraag = userQuestion.value.trim();

        if (!vraag) {
            answerResult.textContent = "Vul een vraag in.";
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/kba`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ vraag }),
            });

            const result = await response.json();
            if (response.ok) {
                answerResult.textContent = result.antwoord;
            } else {
                answerResult.textContent = `Fout: ${result.error}`;
            }
        } catch (error) {
            answerResult.textContent = `Fout: ${error.message}`;
        }
    });
});
